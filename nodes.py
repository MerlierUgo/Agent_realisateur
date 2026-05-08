import os
from typing import Annotated, TypedDict

from state import AgentRealState

# 3. Définition du Noeud unique
def assistant( model):
    # On envoie tout l'historique des messages au LLM
    def _node(state : AgentRealState):
        response = model.invoke(state["messages"])
        print("state:", state["messages"])
        return {"messages": [response]}
    return _node


