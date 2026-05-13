"""
Pipeline principal pour traiter les scénarios.
Orchestre l'extraction, la normalisation et l'injection des entités dans FalkorDB.
"""

import logging
from typing import List, Tuple, Optional
from pathlib import Path

from entity_extractor import EntityExtractor, EntityDeduplicator
from falkordb_connector import FalkorDBConnector, CypherGenerator
from ontology import Triple, Ontology

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ScreenplayProcessor:
    """Pipeline complet de traitement de scénario"""
    
    def __init__(self, llm, falkordb_host: str = "localhost", falkordb_port: int = 6379):
        """
        Initialise le processeur de scénario
        
        Args:
            llm: Instance du LLM (ex: Ollama)
            falkordb_host: Adresse du serveur FalkorDB
            falkordb_port: Port du serveur FalkorDB
        """
        self.llm = llm
        self.extractor = EntityExtractor(llm)
        self.deduplicator = EntityDeduplicator()
        
        try:
            self.db = FalkorDBConnector(host=falkordb_host, port=falkordb_port)
            self.db_available = True
        except Exception as e:
            logger.warning(f"FalkorDB non disponible: {e}. Mode simulation activé.")
            self.db = None
            self.db_available = False
    
    def process_screenplay_chunk(self, screenplay_chunk: str) -> Tuple[List[Triple], int, int]:
        """
        Traite un chunk de scénario
        
        Args:
            screenplay_chunk: Texte du scénario à traiter
            
        Returns:
            Tuple (liste de triplets traités, succès, erreurs)
        """
        logger.info("=" * 60)
        logger.info("🎬 TRAITEMENT D'UN CHUNK DE SCÉNARIO")
        logger.info("=" * 60)
        
        # Étape 1: Extraction des entités via LLM
        logger.info("\n📍 ÉTAPE 1: Extraction des entités via LLM...")
        triples = self.extractor.extract_entities(screenplay_chunk)
        logger.info(f"   ✓ {len(triples)} triplets extraits")
        
        if not triples:
            logger.warning("   ⚠️  Aucun triplet extrait")
            return [], 0, 0
        
        # Étape 2: Normalisation des noms d'entités
        logger.info("\n📍 ÉTAPE 2: Normalisation des noms d'entités...")
        normalized_triples = []
        for triple in triples:
            triple_norm = triple.normalize()
            normalized_triples.append(triple_norm)
            logger.debug(f"   {triple_norm.subject} ({triple_norm.subject_type.value}) "
                        f"-[{triple_norm.relation.value}]-> "
                        f"{triple_norm.object} ({triple_norm.object_type.value})")
        logger.info(f"   ✓ Normalisation complète")
        
        # Étape 3: Déduplication
        logger.info("\n📍 ÉTAPE 3: Déduplication...")
        deduped_triples = self.deduplicator.deduplicate_triples(normalized_triples)
        duplicates_removed = len(normalized_triples) - len(deduped_triples)
        if duplicates_removed > 0:
            logger.info(f"   ✓ {duplicates_removed} doublons supprimés")
        else:
            logger.info(f"   ✓ Aucun doublon détecté")
        
        # Étape 4: Génération des requêtes Cypher
        logger.info("\n📍 ÉTAPE 4: Génération des requêtes Cypher...")
        cypher_queries = CypherGenerator.generate_merge_queries(deduped_triples)
        logger.info(f"   ✓ {len(cypher_queries)} requêtes Cypher générées")
        
        # Affiche un exemple de requête
        if cypher_queries:
            logger.debug(f"   Exemple de requête:\n   {cypher_queries[0]}")
        
        # Étape 5: Injection dans FalkorDB
        logger.info("\n📍 ÉTAPE 5: Injection dans FalkorDB...")
        if self.db_available:
            success, errors = self.db.inject_triples(deduped_triples)
            logger.info(f"   ✓ {success} requêtes exécutées avec succès")
            if errors > 0:
                logger.warning(f"   ⚠️  {errors} erreurs")
        else:
            logger.info("   ⚠️  FalkorDB non disponible - simulation uniquement")
            success = len(cypher_queries)
            errors = 0
            # En mode simulation, on affiche les requêtes
            for i, query in enumerate(cypher_queries[:3], 1):
                logger.info(f"\n   Requête {i}:\n   {query}")
            if len(cypher_queries) > 3:
                logger.info(f"\n   ... et {len(cypher_queries) - 3} autres requêtes")
        
        logger.info("\n" + "=" * 60)
        logger.info(f"✅ RÉSUMÉ: {success} succès, {errors} erreurs")
        logger.info("=" * 60 + "\n")
        
        return deduped_triples, success, errors
    
    def process_screenplay_file(self, file_path: str) -> Tuple[List[Triple], int, int]:
        """
        Traite un fichier scénario complet
        
        Args:
            file_path: Chemin du fichier scénario
            
        Returns:
            Tuple (liste de tous les triplets, succès total, erreurs total)
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"Fichier non trouvé: {file_path}")
            return [], 0, 0
        
        logger.info(f"📂 Lecture du fichier: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                screenplay_text = f.read()
        except Exception as e:
            logger.error(f"Erreur de lecture du fichier: {e}")
            return [], 0, 0
        
        # Divise le scénario en chunks (par scènes si possible)
        chunks = self._chunk_screenplay(screenplay_text)
        logger.info(f"📝 Scénario divisé en {len(chunks)} chunks")
        
        all_triples = []
        total_success = 0
        total_errors = 0
        
        # Traite chaque chunk
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"\n🔄 Traitement chunk {i}/{len(chunks)}...")
            triples, success, errors = self.process_screenplay_chunk(chunk)
            all_triples.extend(triples)
            total_success += success
            total_errors += errors
        
        logger.info(f"\n🎉 TRAITEMENT COMPLET DU FICHIER")
        logger.info(f"   Total: {len(all_triples)} triplets, "
                   f"{total_success} succès, {total_errors} erreurs")
        
        return all_triples, total_success, total_errors
    
    def _chunk_screenplay(self, screenplay_text: str, max_chunk_size: int = 2000) -> List[str]:
        """
        Divise un scénario en chunks gérables
        
        Args:
            screenplay_text: Texte du scénario
            max_chunk_size: Taille maximale d'un chunk en caractères
            
        Returns:
            Liste de chunks
        """
        # Cherche les en-têtes de scènes pour diviser naturellement
        scene_pattern = r'(INT\.|EXT\.)[^\n]*\n'
        
        import re
        scenes = re.split(scene_pattern, screenplay_text)
        
        chunks = []
        current_chunk = ""
        
        for scene in scenes:
            if len(current_chunk) + len(scene) > max_chunk_size and current_chunk.strip():
                chunks.append(current_chunk.strip())
                current_chunk = scene
            else:
                current_chunk += scene
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Si pas de scènes détectées, divise simplement par taille
        if len(chunks) <= 1:
            chunks = [screenplay_text[i:i + max_chunk_size] 
                     for i in range(0, len(screenplay_text), max_chunk_size)]
        
        return [c for c in chunks if c.strip()]
    
    def query_graph(self, query: str) -> Optional[List]:
        """
        Exécute une requête sur le graphe
        
        Args:
            query: Requête Cypher
            
        Returns:
            Résultat de la requête
        """
        if not self.db_available:
            logger.warning("FalkorDB non disponible")
            return None
        
        return self.db.execute_query(query)
    
    def get_scene_structure(self, scene_id: str) -> Optional[dict]:
        """
        Récupère la structure complète d'une scène
        
        Args:
            scene_id: ID de la scène
            
        Returns:
            Dictionnaire avec les infos de la scène
        """
        if not self.db_available:
            logger.warning("FalkorDB non disponible")
            return None
        
        query = f"""
        MATCH (s:Scene {{id: '{scene_id}'}})
        OPTIONAL MATCH (c:Character)-[:APPEARS_IN]->(s)
        OPTIONAL MATCH (p:Prop)-[:PRESENT_IN]->(s)
        OPTIONAL MATCH (s)-[:LOCATED_AT]->(l:Location)
        OPTIONAL MATCH (s)-[:HAPPENS_DURING]->(t:Time)
        RETURN s, collect(c) as characters, collect(p) as props, l, t
        """
        
        return self.db.execute_query(query)
    
    def close(self):
        """Ferme les ressources"""
        if self.db_available:
            self.db.close()


def demo_extraction(screenplay_text: str):
    """
    Fonction de démonstration pour l'extraction sans LLM
    (pour test/débogage)
    """
    logger.info("🧪 DÉMONSTRATION D'EXTRACTION")
    logger.info("=" * 60)
    
    extractor = EntityExtractor(None)
    scenes = extractor.extract_scenes_from_screenplay(screenplay_text)
    
    logger.info(f"✓ {len(scenes)} scènes détectées:")
    for scene in scenes:
        logger.info(f"  - {scene['id']}: {scene['name']}")
    
    return scenes
