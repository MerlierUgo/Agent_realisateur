    
from langgraph.graph import END, StateGraph
from nodes import assistant
from state import AgentRealState
from langgraph.checkpoint.memory import MemorySaver


def graph(model):
    # 4. Construction du Graphe
    workflow = StateGraph(AgentRealState)

    # Ajouter le noeud
    workflow.add_node("assistant", assistant(model))

    # Définir l'entrée et la sortie
    workflow.set_entry_point("assistant")
    workflow.add_edge("assistant", END)

    checkpoint = MemorySaver()
    # 5. Compilation
    app = workflow.compile(checkpointer=checkpoint)
    

    # --- EXPORT DU GRAPH EN PNG ---
    try:
        # Génère le binaire du graphe
        graph_png = app.get_graph().draw_mermaid_png()
        with open("graph_structure.png", "wb") as f:
            f.write(graph_png)
        print("✅ Image 'graph_structure.png' générée avec succès.")
    except Exception as e:
        print(f"❌ Erreur lors de la génération de l'image (besoin de pygraphviz ou connexion internet pour mermaid) : {e}")

    return app

