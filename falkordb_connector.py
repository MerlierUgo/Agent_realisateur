"""
Module de gestion de FalkorDB.
Génère et exécute les requêtes Cypher pour injecter les entités et relations.
"""

import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import asdict

from ontology import Triple, NodeType, RelationType, Ontology

logger = logging.getLogger(__name__)


class CypherGenerator:
    """Génère les requêtes Cypher MERGE à partir des triplets"""
    
    @staticmethod
    def generate_merge_queries(triples: List[Triple]) -> List[str]:
        """
        Génère les requêtes MERGE Cypher pour les triplets
        
        Args:
            triples: Liste de triplets extraits
            
        Returns:
            Liste de requêtes Cypher en tant que chaînes
        """
        queries = []
        
        for triple in triples:
            # Génère les MERGE pour les nœuds
            subject_merge = CypherGenerator._generate_node_merge(
                triple.subject,
                triple.subject_type,
                triple.subject_properties
            )
            object_merge = CypherGenerator._generate_node_merge(
                triple.object,
                triple.object_type,
                triple.object_properties
            )
            
            # Génère le MERGE pour la relation
            relation_merge = CypherGenerator._generate_relation_merge(
                triple.subject,
                triple.subject_type,
                triple.relation,
                triple.object,
                triple.object_type
            )
            
            # Combine les trois requêtes
            # Format: MERGE subject ; MERGE object ; MERGE relation
            combined_query = f"{subject_merge} {object_merge} {relation_merge}"
            queries.append(combined_query)
        
        return queries
    
    @staticmethod
    def _generate_node_merge(name: str, node_type: NodeType, properties: Dict[str, str] = None) -> str:
        """
        Génère une requête MERGE pour un nœud
        
        Args:
            name: Nom de l'entité
            node_type: Type du nœud
            properties: Dictionnaire de propriétés additionnelles
            
        Returns:
            Requête MERGE pour le nœud
        """
        if properties is None:
            properties = {}
        
        # Nettoie le nom
        name = Ontology.normalize_entity_name(name, node_type)
        name_escaped = Ontology.sanitize_property_value(name)
        
        # Label du nœud
        label = node_type.value
        
        # Clé d'identification du nœud
        # Pour les scenes, on utilise 'id'; pour les autres, on utilise 'name'
        if node_type == NodeType.SCENE:
            identifier = f"id: '{name_escaped}'"
            set_clause = f"name: '{name_escaped}'"
        else:
            identifier = f"name: '{name_escaped}'"
            set_clause = ""
        
        # Construis les propriétés additionnelles
        additional_props = []
        if properties:
            for prop_name, prop_value in properties.items():
                if prop_value and prop_value.strip():
                    prop_value_escaped = Ontology.sanitize_property_value(prop_value)
                    additional_props.append(f"{prop_name}: '{prop_value_escaped}'")
        
        # Combine les propriétés
        if set_clause:
            additional_props.insert(0, set_clause)
        
        set_part = ", ".join(additional_props)
        if set_part:
            set_part = f" SET n += {{{set_part}}}"
        else:
            set_part = ""
        
        # Requête finale
        query = f"MERGE (n:{label} {{{identifier}}}) {set_part}"
        return query
    
    @staticmethod
    def _generate_relation_merge(
        source_name: str,
        source_type: NodeType,
        relation: RelationType,
        target_name: str,
        target_type: NodeType
    ) -> str:
        """
        Génère une requête MERGE pour une relation
        
        Args:
            source_name: Nom du nœud source
            source_type: Type du nœud source
            relation: Type de relation
            target_name: Nom du nœud cible
            target_type: Type du nœud cible
            
        Returns:
            Requête MERGE pour la relation
        """
        # Normalise les noms
        source_name = Ontology.normalize_entity_name(source_name, source_type)
        target_name = Ontology.normalize_entity_name(target_name, target_type)
        
        source_name_escaped = Ontology.sanitize_property_value(source_name)
        target_name_escaped = Ontology.sanitize_property_value(target_name)
        
        # Identifiants des nœuds
        if source_type == NodeType.SCENE:
            source_identifier = f"id: '{source_name_escaped}'"
        else:
            source_identifier = f"name: '{source_name_escaped}'"
        
        if target_type == NodeType.SCENE:
            target_identifier = f"id: '{target_name_escaped}'"
        else:
            target_identifier = f"name: '{target_name_escaped}'"
        
        # Requête MERGE avec MATCH des deux nœuds
        query = (
            f"MATCH (s:{source_type.value} {{{source_identifier}}}) "
            f"MATCH (t:{target_type.value} {{{target_identifier}}}) "
            f"MERGE (s)-[:{relation.value}]->(t)"
        )
        
        return query
    
    @staticmethod
    def generate_delete_all_query() -> str:
        """
        Génère une requête pour supprimer tous les nœuds et relations (utile pour le debug)
        
        Returns:
            Requête MATCH DETACH DELETE
        """
        return "MATCH (n) DETACH DELETE n"


class FalkorDBConnector:
    """Gère la connexion et les opérations sur FalkorDB"""
    
    def __init__(self, host: str = "localhost", port: int = 6379, graph_name: str = "screenplay"):
        """
        Initialise la connexion à FalkorDB
        
        Args:
            host: Adresse du serveur FalkorDB
            port: Port du serveur FalkorDB
            graph_name: Nom du graphe
        """
        self.host = host
        self.port = port
        self.graph_name = graph_name
        self.db = None
        self._connect()
    
    def _connect(self):
        """Établit la connexion à FalkorDB"""
        try:
            from falkordb import FalkorDB
            
            # Crée une instance de FalkorDB
            self.db = FalkorDB(host=self.host, port=self.port)
            logger.info(f"✅ Connecté à FalkorDB sur {self.host}:{self.port}")
        except ImportError:
            logger.error("falkordb-py n'est pas installé. Installez-le avec: pip install falkordb")
            raise
        except Exception as e:
            logger.error(f"Erreur de connexion à FalkorDB: {e}")
            raise
    
    def execute_query(self, query: str) -> Optional[Dict]:
        """
        Exécute une requête Cypher
        
        Args:
            query: Requête Cypher
            
        Returns:
            Résultat de la requête
        """
        try:
            if not self.db:
                logger.error("Pas de connexion établie à FalkorDB")
                return None
            
            graph = self.db.select_graph(self.graph_name)
            result = graph.query(query)
            
            logger.debug(f"Requête exécutée: {query[:80]}...")
            return result
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de la requête: {e}")
            logger.debug(f"Requête: {query}")
            return None
    
    def execute_queries(self, queries: List[str]) -> Tuple[int, int]:
        """
        Exécute une liste de requêtes Cypher
        
        Args:
            queries: Liste de requêtes Cypher
            
        Returns:
            Tuple (nombre succès, nombre erreurs)
        """
        success_count = 0
        error_count = 0
        
        for query in queries:
            try:
                result = self.execute_query(query)
                if result is not None:
                    success_count += 1
                else:
                    error_count += 1
            except Exception as e:
                logger.error(f"Erreur: {e}")
                error_count += 1
        
        logger.info(f"Exécution terminée: {success_count} succès, {error_count} erreurs")
        return success_count, error_count
    
    def inject_triples(self, triples: List[Triple]) -> Tuple[int, int]:
        """
        Injecte les triplets dans FalkorDB
        
        Args:
            triples: Liste de triplets
            
        Returns:
            Tuple (nombre succès, nombre erreurs)
        """
        # Génère les requêtes Cypher
        queries = CypherGenerator.generate_merge_queries(triples)
        
        logger.info(f"Injection de {len(queries)} requêtes Cypher dans FalkorDB...")
        
        # Exécute les requêtes
        return self.execute_queries(queries)
    
    def get_all_nodes(self, node_type: NodeType = None) -> List[Dict]:
        """
        Récupère tous les nœuds (optionnellement filtrés par type)
        
        Args:
            node_type: Type de nœud à filtrer (optionnel)
            
        Returns:
            Liste de nœuds
        """
        if node_type:
            query = f"MATCH (n:{node_type.value}) RETURN n"
        else:
            query = "MATCH (n) RETURN n"
        
        try:
            result = self.execute_query(query)
            return result if result else []
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des nœuds: {e}")
            return []
    
    def get_all_relationships(self) -> List[Dict]:
        """
        Récupère toutes les relations
        
        Returns:
            Liste de relations
        """
        query = "MATCH (s)-[r]->(t) RETURN s, r, t"
        
        try:
            result = self.execute_query(query)
            return result if result else []
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des relations: {e}")
            return []
    
    def clear_database(self):
        """Supprime tous les nœuds et relations (utile pour le debug)"""
        query = CypherGenerator.generate_delete_all_query()
        logger.warning("Suppression de tous les nœuds et relations...")
        self.execute_query(query)
    
    def close(self):
        """Ferme la connexion à FalkorDB"""
        try:
            if self.db:
                self.db.close()
                logger.info("Connexion à FalkorDB fermée")
        except Exception as e:
            logger.error(f"Erreur lors de la fermeture de la connexion: {e}")


class CypherValidator:
    """Valide les requêtes Cypher avant exécution"""
    
    @staticmethod
    def validate_merge_query(query: str) -> bool:
        """
        Valide une requête MERGE Cypher
        
        Args:
            query: Requête à valider
            
        Returns:
            True si valide
        """
        # Vérifications basiques
        if not query.startswith("MERGE"):
            logger.warning(f"Requête ne commence pas par MERGE: {query[:50]}")
            return False
        
        # Vérifie la présence de parenthèses
        if query.count("(") != query.count(")"):
            logger.warning(f"Parenthèses non équilibrées: {query[:50]}")
            return False
        
        # Vérifie qu'il n'y a pas de guillemets non échappés problématiques
        # (c'est une validation basique)
        
        return True
