#!/usr/bin/env python3
"""
Quick Start - Pipeline Screenplay to Knowledge Graph
Script de démarrage rapide pour extraire des entités d'un scénario
et les injecter dans FalkorDB.
"""

import os
import logging
from pathlib import Path
from screenplay_processor import ScreenplayProcessor
from langchain_community.llms import Ollama

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Fonction principale"""
    
    logger.info("🎬 SCREENPLAY TO KNOWLEDGE GRAPH PIPELINE")
    logger.info("=" * 60)
    
    # 1. Initialiser le LLM
    logger.info("\n1️⃣  Initialisation du LLM...")
    try:
        # llm = Ollama(model="llama3.2:3b")
        llm = Ollama(model="llama3:8b", format="json", temperature=0)
        logger.info("   ✅ LLM Ollama prêt (llama3:8b)")
    except Exception as e:
        logger.error(f"   ❌ Erreur LLM: {e}")
        logger.info("   💡 Assurez-vous que Ollama est lancé: ollama serve")
        return
    
    # 2. Initialiser le processeur
    logger.info("\n2️⃣  Initialisation du processeur FalkorDB...")
    try:
        processor = ScreenplayProcessor(
            llm,
            falkordb_host="localhost",
            falkordb_port=6379
        )
        if processor.db_available:
            logger.info("   ✅ Connecté à FalkorDB")
        else:
            logger.info("   ⚠️  FalkorDB non disponible - mode simulation")
    except Exception as e:
        logger.warning(f"   ⚠️  {e}")
        logger.info("   💡 Pour utiliser FalkorDB: docker run -p 6379:6379 falkordb/falkordb")
        processor = ScreenplayProcessor(llm)
    
    # 3. Texte exemple
    logger.info("\n3️⃣  Traitement d'un exemple...")
    
    example_screenplay = """
EXT. PARKING SOUTERRAIN - NUIT

Luc sort un pistolet de sa poche et le pose sur le capot d'une Mercedes noire.
Sarah l'observe de loin, cachée derrière un pilier en béton.

LUC
C'est fini. Plus jamais.

Sarah s'approche lentement. Elle porte une enveloppe jaune à la main.

SARAH
Tu as trouvé ce que tu cherchais?

Luc prend l'enveloppe sans la regarder. Il glisse le pistolet dans sa veste.

INT. BUREAU - JOUR

Jean travaille à son ordinateur. Sur son bureau: un stylo vert, une photo encadrée, 
et une tasse de café froid. La porte s'ouvre. Marie entre, l'air pressé.

MARIE
(essoufflée)
C'est urgent. Le contrat est signé. Les documents sont en sécurité.

JEAN
Où exactement?

Marie pose une clé USB sur le bureau, à côté du stylo.

MARIE
Dans le coffre. Niveau B5.

EXT. RUE PRINCIPALE - MATIN

Un taxi jaune arrive dans la brume. Il pleut doucement. Luc et Sarah montent dedans 
avec leurs valises usées.

CONDUCTEUR
Où allez-vous?

LUC
À la gare centrale. Et vite.
"""
    
    # Traite le scénario
    triples, success, errors = processor.process_screenplay_chunk(example_screenplay)
    
    # 4. Afficher les résultats
    logger.info("\n4️⃣  Résultats de l'extraction...")
    logger.info(f"   📊 Triplets extraits: {len(triples)}")
    logger.info(f"   ✅ Injections réussies: {success}")
    logger.info(f"   ❌ Erreurs: {errors}")
    
    if triples:
        logger.info("\n   Aperçu des triplets:")
        for i, triple in enumerate(triples[:5], 1):
            logger.info(f"   {i}. {triple.subject} ({triple.subject_type.value}) "
                       f"-[{triple.relation.value}]-> {triple.object} ({triple.object_type.value})")
        
        if len(triples) > 5:
            logger.info(f"   ... et {len(triples) - 5} autres")
    
    # 5. Options supplémentaires
    logger.info("\n5️⃣  Options supplémentaires...")
    
    if processor.db_available:
        logger.info("\n   📚 Requêtes possibles sur FalkorDB:")
        logger.info("   • Récupérer tous les personnages:")
        logger.info('       processor.query_graph("MATCH (c:Character) RETURN c.name")')
        
        logger.info("   • Récupérer tous les lieux:")
        logger.info('       processor.query_graph("MATCH (l:Location) RETURN l.name")')
        
        logger.info("   • Récupérer les accessoires d'un personnage:")
        logger.info('       processor.query_graph("MATCH (p:Prop)-[:USED_BY]->(c:Character {name: \'LUC\'}) RETURN p.name")')
    
    # 6. Traiter un fichier
    logger.info("\n6️⃣  Traiter un fichier complet...")
    
    screenplay_file = Path("./retriever_doc/fight_club_script.txt")
    if screenplay_file.exists():
        logger.info(f"   📂 Fichier trouvé: {screenplay_file}")
        logger.info("   💡 Pour traiter: processor.process_screenplay_file('./retriever_doc/fight_club_script.txt')")
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ PIPELINE PRÊT À L'EMPLOI")
    logger.info("=" * 60)
    
    # Retourner le processeur pour utilisation interactive
    return processor


def interactive_mode(processor):
    """Mode interactif pour tester les requêtes"""
    logger.info("\n🎮 MODE INTERACTIF")
    logger.info("Commandes disponibles:")
    logger.info("  'query <cypher>' - Exécuter une requête Cypher")
    logger.info("  'scene <id>' - Récupérer la structure d'une scène")
    logger.info("  'scenes' - Lister toutes les scènes")
    logger.info("  'characters' - Lister tous les personnages")
    logger.info("  'quit' - Quitter")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if user_input.lower() == "quit":
                logger.info("Au revoir!")
                break
            
            elif user_input.lower().startswith("query "):
                cypher_query = user_input[6:].strip()
                result = processor.query_graph(cypher_query)
                logger.info(f"Résultat:\n{result}")
            
            elif user_input.lower().startswith("scene "):
                scene_id = user_input[6:].strip()
                result = processor.get_scene_structure(scene_id)
                logger.info(f"Scène {scene_id}:\n{result}")
            
            elif user_input.lower() == "scenes":
                result = processor.query_graph("MATCH (s:Scene) RETURN s.id, s.name")
                logger.info(f"Scènes:\n{result}")
            
            elif user_input.lower() == "characters":
                result = processor.query_graph("MATCH (c:Character) RETURN c.name")
                logger.info(f"Personnages:\n{result}")
            
            else:
                logger.info("Commande inconnue. Tapez 'help' ou 'quit'.")
        
        except KeyboardInterrupt:
            logger.info("\nInterruption utilisateur")
            break
        except Exception as e:
            logger.error(f"Erreur: {e}")


if __name__ == "__main__":
    try:
        processor = main()
        
        # Options: mode interactif ou simple démonstration
        # Décommentez la ligne suivante pour le mode interactif
        # interactive_mode(processor)
        
    except KeyboardInterrupt:
        logger.info("\n\n👋 Arrêt.")
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        raise
