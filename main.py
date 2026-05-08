import os
from typing import Annotated, TypedDict
from langchain_community.llms import Ollama
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from graph import graph

# 2. Initialisation du LLM (Ollama)
# Assure-toi d'avoir fait 'ollama pull llama3' au préalable
llm = Ollama(model="llama3.2:3b")

# 6. Invocation (Test)
if __name__ == "__main__":
    print("--- Début de l'Agent Assistant Réalisateur (Terminal) ---")
    
    query = "Bonjour, tu es mon assistant réalisateur. Peux-tu m'expliquer brièvement ton rôle ?"
    
    # On lance le graphe avec la query
    inputs = {"messages": [("user", query)]}
    config = {"configurable": {"thread_id": "1"}}

    app = graph(llm)
    for event in app.stream(inputs, config=config):
        for value in event.values():
            print("\nAssistant says:", value["messages"][-1])