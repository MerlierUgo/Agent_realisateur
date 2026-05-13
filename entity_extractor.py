"""
Module d'extraction d'entités et relations à partir d'un texte de scénario.
Utilise un LLM pour extraire les triplets (sujet, relation, objet) en format JSON.
"""

import json
import re
from typing import List, Dict, Any, Optional
from dataclasses import asdict
import logging

from ontology import NodeType, RelationType, Triple, Ontology

logger = logging.getLogger(__name__)


class EntityExtractor:
    """Extrait les entités et relations d'un texte de scénario via LLM"""
    
    # Prompt système pour l'extraction
    EXTRACTION_SYSTEM_PROMPT = """Tu es un expert en extraction d'informations cinématographiques.
Tu dois extraire les entités et relations d'un texte de scénario de film.

Entités possibles:
- Scene: Une scène du film (lieu + moment). ID: {LOCATION}_{TIME_OF_DAY}
- Character: Un personnage
- Location: Un lieu
- Prop: Un accessoire/objet
- Time: Moment de la journée (DAY, NIGHT, DAWN, DUSK, MORNING, AFTERNOON, EVENING)

Relations autorisées:
- Character APPEARS_IN Scene
- Scene LOCATED_AT Location
- Prop USED_BY Character
- Prop PRESENT_IN Scene
- Scene HAPPENS_DURING Time

Retourne un JSON valide avec cette structure:
{
    "triples": [
        {
            "subject": "nom du sujet",
            "subject_type": "Scene|Character|Location|Prop|Time",
            "relation": "APPEARS_IN|LOCATED_AT|USED_BY|PRESENT_IN|HAPPENS_DURING",
            "object": "nom de l'objet",
            "object_type": "Scene|Character|Location|Prop|Time",
            "subject_properties": {"propriété": "valeur", ...},
            "object_properties": {"propriété": "valeur", ...}
        }
    ]
}

IMPORTANT:
- Les noms des entités doivent être courts et distincts
- Les IDs de Scene doivent être: PARKING_NIGHT, BEDROOM_DAWN, etc.
- Retourne UNIQUEMENT du JSON valide, rien d'autre
- Ne crée des triplets que s'il y a une relation claire dans le texte

"""
    
    def __init__(self, llm):
        """
        Initialise l'extracteur d'entités
        
        Args:
            llm: Instance d'un LLM (ex: Ollama)
        """
        self.llm = llm
    
    def extract_entities(self, screenplay_text: str) -> List[Triple]:
        """
        Extrait les entités et relations d'un texte de scénario
        
        Args:
            screenplay_text: Texte du scénario (chunk)
            
        Returns:
            Liste de triplets (Triple) extraits et validés
        """
        # 1. Appeler le LLM
        prompt = f"""{self.EXTRACTION_SYSTEM_PROMPT}

Texte du scénario:
{screenplay_text}

Réponds avec du JSON valide uniquement."""
        
        try:
            response = self.llm.invoke(prompt)
            logger.info(f"Réponse LLM reçue: {len(response)} caractères")
        except Exception as e:
            logger.error(f"Erreur lors de l'appel LLM: {e}")
            return []
        
        # 2. Parser la réponse JSON
        triples = self._parse_llm_response(response)
        
        # 3. Normaliser les noms d'entités
        normalized_triples = []
        for triple in triples:
            triple = triple.normalize()
            
            # 4. Valider le triplet selon l'ontologie
            if not triple.is_valid():
                logger.warning(f"Triplet invalide selon l'ontologie: {triple.subject} "
                              f"({triple.subject_type}) -[{triple.relation}]-> "
                              f"{triple.object} ({triple.object_type})")
                continue
            
            normalized_triples.append(triple)
        
        logger.info(f"Extraction complète: {len(normalized_triples)} triplets valides extraits")
        return normalized_triples
    
    def _parse_llm_response(self, response: str) -> List[Triple]:
        """
        Parse la réponse du LLM et convertit en objets Triple
        
        Args:
            response: Réponse textuelle du LLM
            
        Returns:
            Liste d'objets Triple
        """
        triples = []
        
        # Cherche un bloc JSON dans la réponse (robustesse si LLM ajoute du texte)
        json_match = re.search(r'\{[\s\S]*\}', response)
        if not json_match:
            logger.warning("Aucun JSON trouvé dans la réponse du LLM")
            return triples
        
        try:
            json_str = json_match.group(0)
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de parsing JSON: {e}")
            logger.debug(f"Réponse brute: {response}")
            return triples
        
        # Extrait les triplets du JSON
        triples_data = data.get("triples", [])
        for triple_data in triples_data:
            try:
                triple = self._create_triple_from_dict(triple_data)
                if triple:
                    triples.append(triple)
            except (KeyError, ValueError) as e:
                logger.warning(f"Erreur lors de la création d'un triplet: {e}")
                logger.debug(f"Données triplet: {triple_data}")
                continue
        
        return triples
    
    def _create_triple_from_dict(self, data: Dict[str, Any]) -> Optional[Triple]:
        try:
            # On force en MAJUSCULES pour correspondre aux Enums Python
            s_type_str = str(data.get("subject_type", "")).upper()
            o_type_str = str(data.get("object_type", "")).upper()
            rel_str = str(data.get("relation", "")).upper()

            # Mapping sécurisé
            subject_type = NodeType[s_type_str]
            object_type = NodeType[o_type_str]
            relation = RelationType[rel_str]
            
            return Triple(
                subject=data["subject"],
                subject_type=subject_type,
                relation=relation,
                object=data["object"],
                object_type=object_type,
                subject_properties=data.get("subject_properties", {}),
                object_properties=data.get("object_properties", {})
            )
        except KeyError as e:
            # Si la clé n'existe pas dans l'Enum (ex: le LLM a inventé un type)
            logger.error(f"Type ou Relation inconnu : {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur structurelle : {e}")
            return None
    
    def extract_scenes_from_screenplay(self, screenplay_text: str) -> List[Dict[str, str]]:
        """
        Extrait les informations de scènes du scénario.
        Cherche les patterns comme "EXT. LOCATION - TIME" ou "INT. LOCATION - TIME"
        
        Args:
            screenplay_text: Texte du scénario
            
        Returns:
            Liste de dictionnaires avec les infos de scènes
        """
        scenes = []
        
        # Pattern pour détecter les en-têtes de scène
        # Format: INT./EXT. LOCATION - TIME
        pattern = r'(INT\.|EXT\.)\s+([^-]+?)\s*-\s*([^.\n]+)'
        
        matches = re.finditer(pattern, screenplay_text, re.IGNORECASE)
        
        for match in matches:
            interior_exterior = match.group(1).upper()
            location = match.group(2).strip()
            time_of_day = match.group(3).strip().upper()
            
            # Normalise le time_of_day
            time_of_day = self._normalize_time_of_day(time_of_day)
            
            # Crée un ID de scène
            scene_id = f"{location.replace(' ', '_').upper()}_{time_of_day}"
            
            scenes.append({
                "id": scene_id,
                "name": f"{interior_exterior} {location}",
                "location": location,
                "interior_exterior": interior_exterior,
                "time_of_day": time_of_day,
                "description": ""
            })
        
        return scenes
    
    @staticmethod
    def _normalize_time_of_day(time_str: str) -> str:
        """
        Normalise une chaîne de temps vers une valeur standard
        
        Args:
            time_str: Chaîne à normaliser (ex: "NUIT", "night", "JOUR")
            
        Returns:
            Valeur normalisée (DAY, NIGHT, DAWN, DUSK, MORNING, AFTERNOON, EVENING)
        """
        time_str = time_str.strip().upper()
        
        # Mappings français -> anglais et variantes
        mappings = {
            "NUIT": "NIGHT",
            "NIGHT": "NIGHT",
            "JOUR": "DAY",
            "DAY": "DAY",
            "MATIN": "MORNING",
            "MORNING": "MORNING",
            "MIDI": "AFTERNOON",
            "AFTERNOON": "AFTERNOON",
            "APRÈS-MIDI": "AFTERNOON",
            "SOIR": "EVENING",
            "EVENING": "EVENING",
            "AUBE": "DAWN",
            "DAWN": "DAWN",
            "CRÉPUSCULE": "DUSK",
            "DUSK": "DUSK",
        }
        
        return mappings.get(time_str, "DAY")  # Par défaut: DAY


class EntityDeduplicator:
    """Déduplique les entités similaires"""
    
    @staticmethod
    def deduplicate_triples(triples: List[Triple]) -> List[Triple]:
        """
        Déduplique les triplets
        
        Args:
            triples: Liste de triplets
            
        Returns:
            Liste de triplets dédupliquée
        """
        seen = set()
        deduped = []
        
        for triple in triples:
            # Crée une clé unique pour le triplet
            key = (
                triple.subject.upper().strip(),
                triple.subject_type.value,
                triple.relation.value,
                triple.object.upper().strip(),
                triple.object_type.value
            )
            
            if key not in seen:
                seen.add(key)
                deduped.append(triple)
        
        return deduped
