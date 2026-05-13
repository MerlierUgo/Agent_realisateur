"""
Ontologie du graphe cinématographique.
Définit les nœuds, les relations autorisées et les validations.
"""

from enum import Enum
from typing import Set, Tuple, Dict, List
from dataclasses import dataclass


class NodeType(str, Enum):
    """Types de nœuds du graphe"""
    SCENE = "Scene"
    CHARACTER = "Character"
    LOCATION = "Location"
    PROP = "Prop"
    TIME = "Time"


class RelationType(str, Enum):
    """Types de relations du graphe"""
    APPEARS_IN = "APPEARS_IN"      # Character -> Scene
    LOCATED_AT = "LOCATED_AT"      # Scene -> Location
    USED_BY = "USED_BY"            # Prop -> Character
    PRESENT_IN = "PRESENT_IN"      # Prop -> Scene
    HAPPENS_DURING = "HAPPENS_DURING"  # Scene -> Time


@dataclass
class RelationshipRule:
    """Règle de validation pour une relation"""
    relation_type: RelationType
    source_type: NodeType
    target_type: NodeType


class Ontology:
    """Gère l'ontologie du graphe cinématographique"""
    
    # Règles d'ontologie : qui peut se connecter à qui
    VALID_RELATIONSHIPS: List[RelationshipRule] = [
        RelationshipRule(RelationType.APPEARS_IN, NodeType.CHARACTER, NodeType.SCENE),
        RelationshipRule(RelationType.LOCATED_AT, NodeType.SCENE, NodeType.LOCATION),
        RelationshipRule(RelationType.USED_BY, NodeType.PROP, NodeType.CHARACTER),
        RelationshipRule(RelationType.PRESENT_IN, NodeType.PROP, NodeType.SCENE),
        RelationshipRule(RelationType.HAPPENS_DURING, NodeType.SCENE, NodeType.TIME),
    ]
    
    # Propriétés standard pour chaque type de nœud
    NODE_PROPERTIES: Dict[NodeType, Set[str]] = {
        NodeType.SCENE: {"id", "name", "description", "number", "interior_exterior", "time_of_day"},
        NodeType.CHARACTER: {"name", "role", "description"},
        NodeType.LOCATION: {"name", "description", "type"},
        NodeType.PROP: {"name", "description", "category"},
        NodeType.TIME: {"name", "type"},  # Day, Night, Dawn, Dusk, etc.
    }
    
    # Valeurs autorisées pour certaines propriétés
    VALID_TIME_TYPES = {"DAY", "NIGHT", "DAWN", "DUSK", "MORNING", "AFTERNOON", "EVENING"}
    VALID_INTERIOR_EXTERIOR = {"INT", "EXT"}
    
    @staticmethod
    def is_valid_relationship(source_type: NodeType, relation: RelationType, target_type: NodeType) -> bool:
        """
        Vérifie si une relation est autorisée par l'ontologie
        
        Args:
            source_type: Type du nœud source
            relation: Type de relation
            target_type: Type du nœud cible
            
        Returns:
            True si la relation est valide
        """
        for rule in Ontology.VALID_RELATIONSHIPS:
            if (rule.source_type == source_type and 
                rule.relation_type == relation and 
                rule.target_type == target_type):
                return True
        return False
    
    @staticmethod
    def get_valid_targets(source_type: NodeType, relation: RelationType) -> Set[NodeType]:
        """
        Retourne les types de nœuds cibles valides pour une relation
        
        Args:
            source_type: Type du nœud source
            relation: Type de relation
            
        Returns:
            Ensemble des types de nœuds cibles valides
        """
        valid_targets = set()
        for rule in Ontology.VALID_RELATIONSHIPS:
            if rule.source_type == source_type and rule.relation_type == relation:
                valid_targets.add(rule.target_type)
        return valid_targets
    
    @staticmethod
    def normalize_entity_name(name: str, node_type: NodeType = None) -> str:
        """
        Normalise un nom d'entité:
        - Convertit en majuscules
        - Supprime les espaces multiples
        - Supprime les articles inutiles
        - Harmonise les noms similaires
        
        Args:
            name: Nom à normaliser
            node_type: Type de nœud (optionnel, pour normalisation spécifique)
            
        Returns:
            Nom normalisé
        """
        if not name:
            return ""
        
        # Nettoyage basique
        name = name.strip().upper()
        name = " ".join(name.split())  # Supprime espaces multiples
        
        # Supprime articles inutiles au début
        articles = ["LE ", "LA ", "LES ", "UN ", "UNE ", "DES ", "L'", "D'"]
        for article in articles:
            if name.startswith(article):
                name = name[len(article):].strip()
        
        # Supprime "M.", "Mme", "Dr" etc.
        titles = ["M. ", "MME ", "DR ", "DR. ", "MR ", "MRS ", "MS "]
        for title in titles:
            if name.startswith(title):
                name = name[len(title):].strip()
        
        return name.upper().strip()
    
    @staticmethod
    def sanitize_property_value(value: any, property_name: str = None) -> str:
        """
        Nettoie une valeur de propriété pour Cypher
        Échappe les guillemets et caractères spéciaux
        """
        if value is None:
            return ""
        
        value_str = str(value).strip()
        
        # Échappe les guillemets doubles
        value_str = value_str.replace('"', '\\"')
        
        # Échappe les antislash
        value_str = value_str.replace('\\', '\\\\')
        
        return value_str


@dataclass
class Triple:
    """Représente un triplet sujet-relation-objet avec propriétés"""
    subject: str
    subject_type: NodeType
    relation: RelationType
    object: str
    object_type: NodeType
    subject_properties: Dict[str, str] = None
    object_properties: Dict[str, str] = None
    
    def __post_init__(self):
        if self.subject_properties is None:
            self.subject_properties = {}
        if self.object_properties is None:
            self.object_properties = {}
    
    def is_valid(self) -> bool:
        """Valide le triplet selon l'ontologie"""
        return Ontology.is_valid_relationship(
            self.subject_type,
            self.relation,
            self.object_type
        )
    
    def normalize(self) -> "Triple":
        """Normalise les noms d'entités du triplet"""
        self.subject = Ontology.normalize_entity_name(self.subject, self.subject_type)
        self.object = Ontology.normalize_entity_name(self.object, self.object_type)
        return self
