# Architecture du Graph - Trois Noeuds

## 📊 Flux du Graph

```
User Query
    ↓
[Router] - Analyse la requête
    ↓
    ├─→ Keywords: calendrier, planifier, réunion, rendez-vous...
    │    ↓
    │   [Planning Node] → Calendar API ✅
    │    ↓
    │   END ✓
    │
    └─→ Sinon (requête générale)
         ↓
        [Retriever Node] - RAG (si disponible) 📚
         ↓
        [Conversation Node] - LLM Response 💬
         ↓
        END ✓
```

## 🔄 Les trois noeuds

### 1. **Retriever Node** 🔍
- **Rôle**: Chercher les documents pertinents dans Supabase
- **Input**: User query
- **Output**: Context (chunks pertinents)
- **Fichier**: `nodes.py` → `retriever_node()`

```python
retriever.retrieve(query, top_k=3)  # Cherche les 3 chunks similaires
```

### 2. **Conversation Node** 💬
- **Rôle**: Générer une réponse avec le contexte optionnel
- **Input**: Messages + Context
- **Output**: LLM Response
- **Fichier**: `nodes.py` → `conversation_node()`

```python
response = model.invoke(augmented_messages)
```

### 3. **Planning Node** 📅
- **Rôle**: Gérer les actions de calendrier/planification
- **Input**: User query (avec mots-clés: calendrier, rendez-vous, etc.)
- **Output**: Planning action structure
- **Fichier**: `nodes.py` → `planning_node()`

**Structure à implémenter** :
```python
# TODO: Ajouter
- Extraction date/heure/titre d'événement
- Validation des paramètres
- Appel API Calendar
- Confirmation de l'utilisateur
```

## 🎯 Routeur (Router)

La fonction `route_intent()` décide quel noeud utiliser selon la requête:

```python
def route_intent(state: AgentRealState):
    if "calendrier" or "planifier" or "réunion" in query.lower():
        return "planning"  # → Planning Node
    else:
        return "retriever"  # → Retriever Node → Conversation Node
```

**Amélioration future** : Utiliser NLU/NER pour une meilleure classification

## 📝 State

Le state contient maintenant 3 champs :

```python
class AgentRealState(TypedDict):
    messages: Annotated[list, add_messages]      # Historique messages
    context: str                                  # Contexte RAG
    planning_action: str                          # Action planning
```

## 🚀 Utilisation

### Query générale (avec RAG)
```
User: "donne moi les 3 régles du fight club"
→ Router → Retriever → Conversation → Réponse augmentée
```

### Query de planification
```
User: "crée un rendez-vous demain à 14h pour une réunion"
→ Router → Planning → Action Calendar
```

## 📌 Prochaines étapes

1. **Implémenter Planning Node complètement** :
   - Intégration Google Calendar API / Outlook
   - Extraction NER (date, heure, titre)
   - Validation et confirmation

2. **Améliorer le Router** :
   - Utiliser un modèle NLU
   - Gérer les cas hybrides (RAG + Planning)

3. **Ajouter plus de noeuds** :
   - Search Web Node
   - Email Node
   - etc.

## 🔧 Tester le graph

```bash
# Query générale (RAG)
python main.py

# Query planning
# Modifier la query dans main.py :
query = "planifie une réunion demain à 10h"
python main.py
```

L'image `graph_structure.png` se régénère automatiquement ! 📸
