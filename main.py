import os
import uuid
import dotenv
from langchain_community.llms import Ollama
from supabase import create_client, Client

from graph import graph
from retriever import VectorRetriever
from message_storage import MessageStorage

# 1. Charger les variables d'environnement
dotenv.load_dotenv()

# 2. Initialisation du LLM (Ollama)
# Utilisation de llama3.2:3b pour un bon compromis vitesse/intelligence
llm = Ollama(model="llama3.2:3b")

# 3. Initialisation de Supabase
supabase: Client = create_client(
    os.getenv("REACT_APP_SUPABASE_URL"), 
    os.getenv("REACT_APP__ANON_KEY")
)

# 4. Initialisation du Retriever (RAG)
retriever = VectorRetriever(supabase)

# 5. Initialisation du gestionnaire de messages
message_storage = MessageStorage(supabase)

def run_interactive_chat():
    print("\n🎬 --- AGENT ASSISTANT RÉALISATEUR PRÊT ---")
    print("Système : LangGraph + Semantic Router + Supabase")
    print("(Tapez 'exit' pour quitter)\n")

    # On compile le graphe
    app = graph(llm, retriever)
    
    # ID de session unique pour la mémoire (MemorySaver)
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    print(f"📝 Session ID: {thread_id}\n")

    while True:
        user_input = input("👤 Réalisateur : ")
        
        if user_input.lower() in ["exit", "quit", "q"]:
            print("\n🎥 Coupez ! Session terminée.")
            break

        if not user_input.strip():
            continue

        # 💾 Sauvegarder le message utilisateur
        message_storage.save_message(thread_id, "user", user_input)

        # Préparation de l'input pour le StateGraph
        inputs = {
            "messages": [("user", user_input)], 
            "context": "", 
            "planning_action": ""
        }

        print("\n" + "—"*40)
        
        # On utilise .stream pour voir passer les nœuds (utile pour debugger le Router)
        try:
            last_response = None
            
            for event in app.stream(inputs, config=config):
                for node_name, value in event.items():
                    # On affiche le nœud actif pour le debug sémantique
                    print(f"⚙️  [Node: {node_name}]")
                    
                    if "messages" in value:
                        # On récupère le dernier message généré
                        response = value["messages"][-1]
                        
                        # Si c'est le message final (souvent venant du nœud conversation)
                        if node_name in ["conversation", "planning"]:
                            print("\n🤖 Assistant :")
                            # Gestion du format (certains LLM renvoient un objet Message, d'autres du texte)
                            content = response.content if hasattr(response, 'content') else str(response)
                            print(content)
                            last_response = content
            
            # 💾 Sauvegarder la réponse de l'assistant si elle existe
            if last_response:
                message_storage.save_message(thread_id, "assistant", last_response)
            
            print("—"*40 + "\n")
            
        except Exception as e:
            print(f"\n❌ Erreur pendant l'exécution : {e}\n")

# 5. Lancement
if __name__ == "__main__":
    # OPTIONNEL: Indexer les documents au premier lancement
    # print("\n📚 Indexation des documents...")
    retriever.load_and_index_documents("./retriever_doc")
    
    run_interactive_chat()