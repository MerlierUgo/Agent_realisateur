import os
from typing import Annotated, TypedDict

from state import AgentRealState

# ============ NOEUD 1: RETRIEVER (RAG) ============
def retriever_node(retriever):
    """Noeud de retrieval avec contexte"""
    def _node(state: AgentRealState):
        # Extraire la dernière question de l'utilisateur
        last_message = state["messages"][-1] if state["messages"] else None
        if last_message and isinstance(last_message, tuple):
            query = last_message[1]
        else:
            query = str(last_message)
        
        # Récupérer les documents similaires
        retrieved_chunks = retriever.retrieve(query, top_k=3)
        context = retriever.format_context(retrieved_chunks)
        
        print("🧠 User Query:", query)
        if retrieved_chunks:
            print(f"\n📚 {len(retrieved_chunks)} chunk(s) sélectionné(s):")
            for i, chunk in enumerate(retrieved_chunks, 1):
                print(f"   [{i}] {chunk[:150]}...")
        
        return {"context": context}
    
    return _node


# ============ NOEUD 2: CONVERSATION LLM SIMPLE ============
def conversation_node(model):
    """Noeud de conversation simple avec contexte optionnel"""
    def _node(state: AgentRealState):
        # Récupérer le contexte s'il existe
        context = state.get("context", "")
        
        # Augmenter le prompt si contexte disponible
        augmented_messages = state["messages"].copy()
        if context:
            system_context = f"Tu es un assistant réalisateur expert. Utilise le contexte suivant si pertinent:\n\n{context}"
            augmented_messages = [("system", system_context)] + augmented_messages
        
        # Invoquer le LLM
        response = model.invoke(augmented_messages)
        
        print("\n💬 LLM Response Generated")
        
        return {"messages": [response]}
    
    return _node


# ============ NOEUD 3: PLANIFICATION (Calendar API) ============
def planning_node(model):
    """Noeud de planification pour la gestion du calendrier"""
    def _node(state: AgentRealState):
        # Extraire la dernière question de l'utilisateur
        last_message = state["messages"][-1] if state["messages"] else None
        if last_message and isinstance(last_message, tuple):
            query = last_message[1]
        else:
            query = str(last_message)
        
        # TODO: Ajouter la logique d'extraction de la date/heure/titre d'événement
        print(f"\n📅 Planning Node: Traitement de '{query}'")
        print("   ⚙️  [Structure] Extraction date/heure/titre")
        print("   ⚙️  [Structure] Validation des paramètres")
        print("   ⚙️  [Structure] Préparation de l'appel API Calendar")
        
        # Placeholder pour la réponse
        response = "Je vais créer un événement dans votre calendrier."
        
        return {"messages": [response], "planning_action": "calendar_create"}
    
    return _node



