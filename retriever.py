import os
from typing import List
from supabase import Client
from langchain_text_splitters import RecursiveCharacterTextSplitter
#from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_ollama import OllamaEmbeddings

class VectorRetriever:
    """Gestionnaire du stockage vectoriel et retrieval avec Supabase"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        self.table_name = "documents"
        
    def load_and_index_documents(self, docs_path: str) -> None:
        """Charger tous les documents d'un dossier et les indexer dans Supabase"""
        documents = []
        
        # Charger tous les fichiers .txt du dossier
        if os.path.isdir(docs_path):
            for filename in os.listdir(docs_path):
                if filename.endswith('.txt'):
                    filepath = os.path.join(docs_path, filename)
                    print(f"📖 Chargement: {filename}")
                    loader = TextLoader(filepath, encoding="utf-8")
                    docs = loader.load()
                    documents.extend(docs)
        else:
            print(f"❌ Le dossier {docs_path} n'existe pas")
            return
        
        if not documents:
            print("❌ Aucun document trouvé")
            return
        
        # Splitter en chunks
        print(f"✂️ Splitting en chunks...")
        chunks = self.splitter.split_documents(documents)
        print(f"✅ {len(chunks)} chunks créés")
        
        # Générer les embeddings et stocker dans Supabase
        print(f"🧠 Génération des embeddings...")
        for i, chunk in enumerate(chunks):
            try:
                # Générer l'embedding
                embedding = self.embeddings.embed_query(chunk.page_content)
                
                # Préparer les données
                data = {
                    "content": chunk.page_content,
                    "source": chunk.metadata.get("source", "unknown"),
                    "embedding": embedding,
                }
                
                # Insérer dans Supabase
                self.supabase.table(self.table_name).insert(data).execute()
                
                if (i + 1) % 10 == 0:
                    print(f"  → {i + 1}/{len(chunks)} chunks indexés")
            except Exception as e:
                print(f"⚠️ Erreur à l'indexation du chunk {i}: {e}")
                continue
        
        print(f"✅ Tous les documents ont été indexés!")
    
    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        """Récupérer les chunks les plus similaires à la query"""
        try:
            # Générer l'embedding de la query
            query_embedding = self.embeddings.embed_query(query)
            
            # Recherche par similarité dans Supabase
            results = self.supabase.rpc(
                "match_documents",
                {
                    "query_embedding": query_embedding,
                    "match_count": top_k,
                    "similarity_threshold": 0.5
                }
            ).execute()
            
            # Extraire le contenu
            contexts = [result["content"] for result in results.data]
            return contexts
        except Exception as e:
            print(f"⚠️ Erreur lors de la retrieval: {e}")
            return []
    
    def format_context(self, contexts: List[str]) -> str:
        """Formater le contexte pour le prompt"""
        if not contexts:
            return ""
        
        formatted = "📚 Contexte pertinent:\n"
        for i, context in enumerate(contexts, 1):
            formatted += f"\n[{i}] {context[:300]}...\n"
        
        return formatted
