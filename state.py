from langgraph.graph.message import add_messages
from typing import Annotated, TypedDict

# 1. Définition de l'état (State)
class AgentRealState(TypedDict):
    # Messages de la conversation
    messages: Annotated[list, add_messages]
    # Contexte récupéré du vectorstore
    context: str
    # Action de planification (calendar, etc.)
    planning_action: str