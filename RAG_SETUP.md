# Configuration du RAG pour l'Agent Réalisateur

## 📋 Étapes de configuration

### 1. **Configurer Supabase**

Exécutez le SQL depuis `supabase_setup.sql` dans votre dashboard Supabase:
- Allez dans **SQL Editor** 
- Créez une nouvelle requête et collez le contenu de `supabase_setup.sql`
- Exécutez-la

Cela créera:
- La table `documents` avec support vectoriel
- L'index pour les recherches rapides
- La fonction RPC `match_documents` pour la retrieval

### 2. **Variables d'environnement (.env)**

Assurez-vous que votre `.env` contient:
```
REACT_APP_SUPABASE_URL=https://votre-url.supabase.co
REACT_APP__ANON_KEY=votre_clé_anonyme
```

### 3. **Installer les dépendances**

```bash
pip install -e .
```

ou avec uv:
```bash
uv sync
```

### 4. **Charger vos documents**

Dans `main.py`, décommentez cette ligne:
```python
retriever.load_and_index_documents("./retriever_doc")
```

Puis lancez:
```bash
python main.py
```

Cela va:
- ✂️ Splitter vos documents en chunks (1000 tokens avec 200 tokens de chevauchement)
- 🧠 Générer les embeddings avec Ollama
- 💾 Stocker dans Supabase

### 5. **Utiliser la RAG**

Une fois indexé, commentez la ligne d'indexation et relancez `main.py`. Le retriever va automatiquement:
- Récupérer les documents similaires à votre query
- Les augmenter dans le prompt du LLM

## 📁 Structure

```
retriever.py          # Gestionnaire RAG (VectorRetriever)
supabase_setup.sql    # Configuration Supabase
state.py              # ✅ Ajout du contexte
nodes.py              # ✅ Utilisation du retriever
graph.py              # ✅ Passage du retriever
main.py               # ✅ Initialisation RAG
```

## ⚙️ Paramètres configurables (retriever.py)

```python
self.splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,        # Taille des chunks
    chunk_overlap=200,      # Chevauchement entre chunks
    separators=["\n\n", "\n", " ", ""]
)

retriever.retrieve(query, top_k=3)  # Nombre de docs à récupérer
```

## 🔍 Troubleshooting

**❌ "Erreur: table documents n'existe pas"**
→ Exécutez le SQL depuis supabase_setup.sql

**❌ "Erreur: match_documents function not found"**
→ Vérifiez que la fonction RPC a bien été créée dans Supabase

**❌ "Pas de résultats de retrieval"**
→ Vérifiez que vos documents ont été indexés (lancez l'indexation)
→ Vérifiez le seuil de similarité (similarity_threshold dans retriever.py)

## 🚀 Prochaines étapes

- Ajuster la stratégie de chunking selon vos documents
- Implémenter des filtres (par source, date, etc.)
- Ajouter un re-ranker pour meilleure pertinence
- Implémenter la mémoire long-terme (historique persistant)
