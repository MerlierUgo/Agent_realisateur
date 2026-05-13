from langgraph.graph import END, StateGraph
from nodes import retriever_node, conversation_node, planning_node
from state import AgentRealState
from langgraph.checkpoint.memory import MemorySaver
from sentence_transformers import util
from sentence_transformers import SentenceTransformer
import numpy as np


# 1. Initialisation du model pour le semantic routing
semantic_model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Définition des routes avec exemples métier "Assistant Réalisateur"
ROUTES = {
    "planification": [
        "What is the schedule for tomorrow?",
        "Send an email to the producer",
        "Is the lead actor available on Tuesday?",
        "What time is the call sheet?",
        "Check my calendar for the scouting session",
        "Weather forecast for the shoot",
        "calendrier", "planifier", "réunion", "rendez-vous", "événement"
    ],
    "retriever": [
        "What props are needed for scene 5?",
        "Search the script for the hospital sequence",
        "What is the character's back story in the document?",
        "Find the technical requirements for the drone shot",
        "Read the production notes about the location",
        "document", "script", "props", "cherche", "find"
    ],
    "conversation": [
        "What do you think of this scene?",
        "I need some creative inspiration",
        "Let's talk about the mood of the film",
        "How should the character react here?",
        "Tell me a joke to relax the crew"
    ]
}

# Encoder tous les exemples une seule fois
encoded_routes = {}
for route_name, utterances in ROUTES.items():
    encoded_routes[route_name] = semantic_model.encode(utterances, convert_to_tensor=True)

# Mots-clés qui indiquent UNE INTENTION explicite de recherche/planning
SEARCH_INTENT_KEYWORDS = [
    "search", "find", "look", "look for", "look up", "get me",
    "cherche", "trouve", "recherche", "donne-moi", "montre-moi",
    "show me", "give me", "need", "what", "where", "which"
]

PLANNING_INTENT_KEYWORDS = [
    "schedule", "calendar", "email", "send", "set up", "create",
    "calendrier", "planifie", "crée", "programme", "envoyer",
    "call sheet", "available", "time", "when", "check"
]


def detect_intent(query: str):
    """Détecte l'intention EXPLICITE avant le semantic routing"""
    query_lower = query.lower()
    
    # Vérifier si y'a une intention explicite de PLANNING
    if any(keyword in query_lower for keyword in PLANNING_INTENT_KEYWORDS):
        return "planification"
    
    # Vérifier si y'a une intention explicite de RECHERCHE
    if any(keyword in query_lower for keyword in SEARCH_INTENT_KEYWORDS):
        return "retriever"
    
    # Pas d'intention claire → utiliser semantic routing
    return None


def router_init(state: AgentRealState):
    """Router sémantique utilisant Sentence-Transformers avec préfiltre d'intention"""
    query = state["messages"][-1][1] if isinstance(state["messages"][-1], tuple) else str(state["messages"][-1])
    
    # 1. ÉTAPE 1: Vérifier intention explicite
    explicit_intent = detect_intent(query)
    if explicit_intent:
        print(f"🛣️  Route: {explicit_intent} (explicit intent)")
        return explicit_intent
    
    # 2. ÉTAPE 2: Semantic routing pour les cas ambigus
    query_embedding = semantic_model.encode(query, convert_to_tensor=True)
    
    # Comparer avec chaque route
    best_route = None
    best_score = -1
    
    for route_name, route_embeddings in encoded_routes.items():
        # Calcul de la similarité cosinus avec tous les exemples
        similarities = util.pytorch_cos_sim(query_embedding, route_embeddings)
        max_similarity = similarities.max().item()
        
        if max_similarity > best_score:
            best_score = max_similarity
            best_route = route_name
    
    # Seuil minimum de confiance
    confidence_threshold = 0.3
    if best_score < confidence_threshold:
        best_route = "conversation"  # Fallback
    
    print(f"🛣️  Route: {best_route} (semantic, confidence: {best_score:.2f})")
    return best_route


def graph(model, retriever=None):
    # 3. Construction du Graphe
    workflow = StateGraph(AgentRealState)

    # Ajouter les trois noeuds
    if retriever:
        workflow.add_node("retriever", retriever_node(retriever))
    
    workflow.add_node("conversation", conversation_node(model))
    workflow.add_node("planning", planning_node(model))

    # Ajouter un noeud router pour dispatcher
    workflow.add_node("router", lambda state: state)

    # Définir l'entry point
    workflow.set_entry_point("router")
    
    # Routing conditionnel
    workflow.add_conditional_edges("router", router_init, {
        "conversation": "conversation",
        "retriever": "retriever" if retriever else "conversation",
        "planification": "planning",
    })
    
    # Transitions après les noeuds
    if retriever:
        workflow.add_edge("retriever", "conversation")
    
    workflow.add_edge("conversation", END)
    workflow.add_edge("planning", END)

    checkpoint = MemorySaver()
    # 4. Compilation
    app = workflow.compile(checkpointer=checkpoint)
    
    # --- EXPORT DU GRAPH EN PNG ---
    try:
        graph_png = app.get_graph().draw_mermaid_png()
        with open("graph_structure.png", "wb") as f:
            f.write(graph_png)
        print("✅ Image 'graph_structure.png' générée avec succès.")
    except Exception as e:
        print(f"❌ Erreur lors de la génération de l'image : {e}")

    return app

