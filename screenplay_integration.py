"""
Intégration du pipeline Screenplay avec l'Agent Réalisateur existant.
Ce module propose des nœuds et routeurs pour intégrer l'extraction d'entités
au graphe LangGraph existant.
"""

import logging
from typing import Optional
from state import AgentRealState
from screenplay_processor import ScreenplayProcessor
from ontology import NodeType

logger = logging.getLogger(__name__)


def screenplay_extraction_node(state: AgentRealState, processor: ScreenplayProcessor):
    """
    Nœud LangGraph pour extraire les entités d'un texte de scénario.
    
    Args:
        state: État du graphe
        processor: Instance du ScreenplayProcessor
        
    Returns:
        État modifié avec le contexte des entités extraites
    """
    # Récupère le dernier message utilisateur
    if not state["messages"]:
        return state
    
    last_message = state["messages"][-1]
    screenplay_text = last_message[1] if isinstance(last_message, tuple) else str(last_message)
    
    logger.info("🎬 Extraction des entités du scénario...")
    
    # Traite le scénario
    triples, success, errors = processor.process_screenplay_chunk(screenplay_text)
    
    # Crée un résumé des entités extraites
    context = f"""
Extraction Scénario Complétée:
- Triplets extraits: {len(triples)}
- Injection FalkorDB: {success} succès, {errors} erreurs

Entités trouvées:
"""
    
    # Groupe par type d'entité
    characters = set()
    locations = set()
    props = set()
    scenes = set()
    
    for triple in triples:
        if triple.subject_type == NodeType.CHARACTER:
            characters.add(triple.subject)
        if triple.object_type == NodeType.CHARACTER:
            characters.add(triple.object)
        if triple.subject_type == NodeType.LOCATION:
            locations.add(triple.subject)
        if triple.object_type == NodeType.LOCATION:
            locations.add(triple.object)
        if triple.subject_type == NodeType.PROP:
            props.add(triple.subject)
        if triple.object_type == NodeType.PROP:
            props.add(triple.object)
        if triple.subject_type == NodeType.SCENE:
            scenes.add(triple.subject)
        if triple.object_type == NodeType.SCENE:
            scenes.add(triple.object)
    
    if characters:
        context += f"\nPersonnages: {', '.join(sorted(characters))}"
    if locations:
        context += f"\nLieux: {', '.join(sorted(locations))}"
    if props:
        context += f"\nAccessoires: {', '.join(sorted(props))}"
    if scenes:
        context += f"\nScènes: {', '.join(sorted(scenes))}"
    
    # Met à jour l'état avec le contexte
    state["context"] = context
    
    return state


def scene_structure_query_node(state: AgentRealState, processor: ScreenplayProcessor, scene_id: Optional[str] = None):
    """
    Nœud LangGraph pour récupérer la structure d'une scène du graphe FalkorDB.
    
    Args:
        state: État du graphe
        processor: Instance du ScreenplayProcessor
        scene_id: ID de la scène (optionnel, sinon extrait du message)
        
    Returns:
        État modifié avec les infos de la scène
    """
    logger.info("🔍 Requête structure de scène...")
    
    # Cherche l'ID de scène
    if not scene_id and state["messages"]:
        # Essaie d'extraire le scene_id du dernier message
        last_message = state["messages"][-1]
        message_text = last_message[1] if isinstance(last_message, tuple) else str(last_message)
        
        # Cherche des patterns comme "PARKING_NIGHT"
        import re
        matches = re.findall(r'[A-Z_]+_(?:DAY|NIGHT|DAWN|DUSK|MORNING|AFTERNOON|EVENING)', message_text)
        if matches:
            scene_id = matches[0]
    
    if not scene_id:
        context = "❌ Aucun ID de scène fourni. Format attendu: LOCATION_TIME (ex: PARKING_NIGHT)"
    else:
        try:
            scene_data = processor.get_scene_structure(scene_id)
            if scene_data:
                context = f"""
Scène: {scene_id}

Données extraites du graphe FalkorDB:
{scene_data}
"""
            else:
                context = f"⚠️  Scène '{scene_id}' non trouvée dans FalkorDB"
        except Exception as e:
            context = f"❌ Erreur lors de la récupération: {e}"
    
    state["context"] = context
    return state


def custom_graph_query_node(state: AgentRealState, processor: ScreenplayProcessor):
    """
    Nœud LangGraph pour exécuter une requête Cypher personnalisée.
    
    Args:
        state: État du graphe
        processor: Instance du ScreenplayProcessor
        
    Returns:
        État modifié avec les résultats
    """
    logger.info("📊 Exécution requête personnalisée...")
    
    if not state["messages"]:
        return state
    
    last_message = state["messages"][-1]
    query = last_message[1] if isinstance(last_message, tuple) else str(last_message)
    
    try:
        result = processor.query_graph(query)
        context = f"""
Résultat Cypher Query:
{result}
"""
    except Exception as e:
        context = f"❌ Erreur requête: {e}"
    
    state["context"] = context
    return state


def screenplay_router(state: AgentRealState):
    """
    Routeur pour décider si un message concerne le scénario/graphe
    
    Args:
        state: État du graphe
        
    Returns:
        Nom du nœud suivant
    """
    if not state["messages"]:
        return "conversation"
    
    last_message = state["messages"][-1]
    message_text = last_message[1] if isinstance(last_message, tuple) else str(last_message)
    message_lower = message_text.lower()
    
    # Keywords pour décider si c'est une requête scénario
    screenplay_keywords = [
        "scène", "scene", "scénario", "screenplay", "personnage", "character",
        "lieu", "location", "prop", "accessoire", "cypher", "graphe", "graph",
        "falkordb", "entité", "entity"
    ]
    
    if any(keyword in message_lower for keyword in screenplay_keywords):
        # Cherche quel type de requête
        if "structure" in message_lower or "scene" in message_lower and "_" in message_text:
            return "scene_query"
        elif "cypher" in message_lower or "query" in message_lower:
            return "custom_query"
        else:
            return "screenplay_extraction"
    
    return "conversation"


def integration_example():
    """
    Exemple d'intégration dans le graphe LangGraph existant
    """
    from langgraph.graph import END, StateGraph
    from nodes import conversation_node, planning_node, retriever_node
    
    # Initialiser le processeur
    from langchain_community.llms import Ollama
    from screenplay_processor import ScreenplayProcessor
    
    llm = Ollama(model="llama3.2:3b")
    processor = ScreenplayProcessor(llm)
    
    # Créer le graphe augmenté
    workflow = StateGraph(AgentRealState)
    
    # Ajouter les nœuds existants
    workflow.add_node("conversation", conversation_node)
    workflow.add_node("planning", planning_node)
    workflow.add_node("retriever", retriever_node)
    
    # Ajouter les nœuds scénario
    def screenplay_extraction_wrapper(state):
        return screenplay_extraction_node(state, processor)
    
    def scene_query_wrapper(state):
        return scene_structure_query_node(state, processor)
    
    def custom_query_wrapper(state):
        return custom_graph_query_node(state, processor)
    
    workflow.add_node("screenplay_extraction", screenplay_extraction_wrapper)
    workflow.add_node("scene_query", scene_query_wrapper)
    workflow.add_node("custom_query", custom_query_wrapper)
    
    # Définir les routes conditionnelles
    workflow.add_conditional_edges(
        "conversation",
        screenplay_router,
        {
            "screenplay_extraction": "screenplay_extraction",
            "scene_query": "scene_query",
            "custom_query": "custom_query",
            "conversation": "conversation"
        }
    )
    
    # Définir les transitions finales
    workflow.add_edge("screenplay_extraction", END)
    workflow.add_edge("scene_query", END)
    workflow.add_edge("custom_query", END)
    
    # Compiler
    return workflow.compile()


if __name__ == "__main__":
    logger.info("📚 Intégration Screenplay Pipeline - Exemple d'utilisation")
    
    # Exemple d'intégration
    # graph = integration_example()
    # print("✅ Graphe intégré avec succès")
