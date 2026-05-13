"""
Script de démonstration et de test du pipeline FalkorDB screenplay.
Montre comment extraire les entités et les injecter dans FalkorDB.
"""

import logging
from screenplay_processor import ScreenplayProcessor, demo_extraction
from ontology import NodeType, RelationType, Triple
from entity_extractor import EntityExtractor, EntityDeduplicator
from falkordb_connector import CypherGenerator

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Exemple de scénario pour tester
EXAMPLE_SCREENPLAY = """
EXT. PARKING - NUIT

Luc sort un pistolet de sa poche et le pose sur le capot de la voiture.
Sarah l'observe de loin, cachée derrière un pilier.

INT. BUREAU - JOUR

Jean travaille à son ordinateur. Sur son bureau, il y a un stylo vert et une photo encadrée.
Marie entre par la porte.

MARIE
C'est urgent. Le contrat est signé.

JEAN
Où sont les documents?

Marie pose une clé USB sur le bureau.

EXT. RUE PRINCIPALE - MATIN

Un taxi jaune arrive. Il pleut. Luc et Sarah montent dedans.

CONDUCTEUR
Où allez-vous?

LUC
À la gare centrale.

INT. GARE - APRÈS-MIDI

Luc et Sarah courent avec leurs valises. Des policiers les poursuivent.
"""


def test_extraction_without_db():
    """Test l'extraction d'entités sans besoin de FalkorDB"""
    logger.info("🧪 TEST 1: Extraction sans LLM (reconnaissance de scènes)")
    logger.info("-" * 60)
    
    scenes = demo_extraction(EXAMPLE_SCREENPLAY)
    
    logger.info(f"\n✅ {len(scenes)} scènes extraites avec succès")
    return scenes


def test_cypher_generation():
    """Test la génération de requêtes Cypher"""
    logger.info("\n🧪 TEST 2: Génération de requêtes Cypher")
    logger.info("-" * 60)
    
    # Crée des triplets de test
    triples = [
        Triple(
            subject="LUC",
            subject_type=NodeType.CHARACTER,
            relation=RelationType.APPEARS_IN,
            object="PARKING_NIGHT",
            object_type=NodeType.SCENE,
            subject_properties={"role": "Protagonist"},
            object_properties={"description": "Parking at night"}
        ),
        Triple(
            subject="PISTOLET",
            subject_type=NodeType.PROP,
            relation=RelationType.USED_BY,
            object="LUC",
            object_type=NodeType.CHARACTER
        ),
        Triple(
            subject="PARKING_NIGHT",
            subject_type=NodeType.SCENE,
            relation=RelationType.LOCATED_AT,
            object="PARKING",
            object_type=NodeType.LOCATION
        ),
        Triple(
            subject="PARKING_NIGHT",
            subject_type=NodeType.SCENE,
            relation=RelationType.HAPPENS_DURING,
            object="NIGHT",
            object_type=NodeType.TIME
        ),
    ]
    
    # Génère les requêtes
    queries = CypherGenerator.generate_merge_queries(triples)
    
    logger.info(f"✓ {len(queries)} requêtes générées\n")
    
    for i, query in enumerate(queries, 1):
        logger.info(f"Requête {i}:")
        logger.info(f"  {query}\n")
    
    return queries


def test_deduplication():
    """Test la déduplication"""
    logger.info("\n🧪 TEST 3: Déduplication")
    logger.info("-" * 60)
    
    # Crée des triplets avec doublons
    triple1 = Triple(
        subject="LUC",
        subject_type=NodeType.CHARACTER,
        relation=RelationType.APPEARS_IN,
        object="PARKING_NIGHT",
        object_type=NodeType.SCENE
    )
    
    triple2 = Triple(
        subject="Luc",  # Variation du nom
        subject_type=NodeType.CHARACTER,
        relation=RelationType.APPEARS_IN,
        object="parking_night",  # Variation du nom
        object_type=NodeType.SCENE
    )
    
    triple3 = Triple(
        subject="JEAN",
        subject_type=NodeType.CHARACTER,
        relation=RelationType.APPEARS_IN,
        object="BUREAU_DAY",
        object_type=NodeType.SCENE
    )
    
    triples = [triple1, triple2, triple3]
    
    # Normalise d'abord
    for triple in triples:
        triple.normalize()
    
    # Déduplique
    deduplicator = EntityDeduplicator()
    deduped = deduplicator.deduplicate_triples(triples)
    
    logger.info(f"Avant déduplication: {len(triples)} triplets")
    logger.info(f"Après déduplication: {len(deduped)} triplets")
    logger.info(f"✓ {len(triples) - len(deduped)} doublons supprimés\n")
    
    for triple in deduped:
        logger.info(f"  {triple.subject} -[{triple.relation.value}]-> {triple.object}")
    
    return deduped


def test_ontology_validation():
    """Test la validation de l'ontologie"""
    logger.info("\n🧪 TEST 4: Validation de l'ontologie")
    logger.info("-" * 60)
    
    # Crée un triplet valide
    valid_triple = Triple(
        subject="LUC",
        subject_type=NodeType.CHARACTER,
        relation=RelationType.APPEARS_IN,
        object="PARKING_NIGHT",
        object_type=NodeType.SCENE
    )
    
    # Crée un triplet invalide
    invalid_triple = Triple(
        subject="LUC",
        subject_type=NodeType.CHARACTER,
        relation=RelationType.APPEARS_IN,
        object="PISTOLET",  # Une prop, pas une scène!
        object_type=NodeType.PROP
    )
    
    logger.info(f"Triplet 1 (valide):")
    logger.info(f"  {valid_triple.subject} ({valid_triple.subject_type.value}) "
               f"-[{valid_triple.relation.value}]-> "
               f"{valid_triple.object} ({valid_triple.object_type.value})")
    logger.info(f"  Valide: {valid_triple.is_valid()} ✓\n")
    
    logger.info(f"Triplet 2 (invalide):")
    logger.info(f"  {invalid_triple.subject} ({invalid_triple.subject_type.value}) "
               f"-[{invalid_triple.relation.value}]-> "
               f"{invalid_triple.object} ({invalid_triple.object_type.value})")
    logger.info(f"  Valide: {invalid_triple.is_valid()} ✗")


def test_full_pipeline_with_mock_llm():
    """Test le pipeline complet avec un mock LLM (si FalkorDB n'est pas dispo)"""
    logger.info("\n🧪 TEST 5: Pipeline complet (avec mock LLM)")
    logger.info("-" * 60)
    
    # Mock LLM qui retourne une réponse prédéfinie
    class MockLLM:
        def invoke(self, prompt):
            return """{
                "triples": [
                    {
                        "subject": "Luc",
                        "subject_type": "CHARACTER",
                        "relation": "APPEARS_IN",
                        "object": "PARKING_NIGHT",
                        "object_type": "SCENE",
                        "subject_properties": {"role": "Protagonist"},
                        "object_properties": {"description": "Parking at night"}
                    },
                    {
                        "subject": "Pistolet",
                        "subject_type": "PROP",
                        "relation": "USED_BY",
                        "object": "Luc",
                        "object_type": "CHARACTER",
                        "subject_properties": {},
                        "object_properties": {}
                    }
                ]
            }"""
    
    mock_llm = MockLLM()
    
    # Crée le processeur avec le mock LLM
    processor = ScreenplayProcessor(mock_llm)
    
    # Traite le scénario exemple
    triples, success, errors = processor.process_screenplay_chunk(EXAMPLE_SCREENPLAY)
    
    logger.info(f"\n✅ Pipeline complet testé")
    logger.info(f"   Triplets extraits: {len(triples)}")
    logger.info(f"   Succès: {success}, Erreurs: {errors}")


def run_all_tests():
    """Lance tous les tests"""
    logger.info("\n" + "=" * 60)
    logger.info("🎬 SUITE DE TESTS - SCREENPLAY PROCESSOR")
    logger.info("=" * 60)
    
    test_extraction_without_db()
    test_cypher_generation()
    test_deduplication()
    test_ontology_validation()
    test_full_pipeline_with_mock_llm()
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ TOUS LES TESTS TERMINÉS")
    logger.info("=" * 60)


if __name__ == "__main__":
    run_all_tests()
