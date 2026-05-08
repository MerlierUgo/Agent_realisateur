from langgraph.graph.message import add_messages
from typing import Annotated, TypedDict

# 1. Définition de l'état (State)
class AgentRealState(TypedDict):
    # add_messages permet d'accumuler l'historique au lieu de l'écraser
    messages: Annotated[list, add_messages]