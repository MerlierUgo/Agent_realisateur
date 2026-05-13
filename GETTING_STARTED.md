# 🚀 Getting Started - Screenplay Pipeline

Guide rapide de démarrage pour le pipeline d'extraction scénario → FalkorDB.

## 📋 Checklist d'Installation

### 1. Prérequis

- ✅ Python 3.12+
- ✅ Ollama (ou autre LLM)
- ✅ Docker (pour FalkorDB - optionnel)
- ✅ Redis CLI (optionnel, pour debug)

### 2. Installation des Dépendances

```bash
# Installer les packages Python
pip install -e .

# Ou manuellement
pip install falkordb langchain langchain-community sentence-transformers python-dotenv
```

### 3. Lancer FalkorDB (Optionnel)

#### Option A: Docker

```bash
# Lancer le conteneur
docker run -p 6379:6379 falkordb/falkordb

# Ou avec docker-compose
docker-compose up -d
```

#### Option B: Redis CLI (Test)

```bash
# Vérifier la connexion
redis-cli ping
# Output: PONG
```

### 4. Lancer Ollama (Pour LLM local)

```bash
# Dans un terminal séparé
ollama serve

# Ou télécharger le modèle d'abord
ollama pull llama3.2:3b
```

## 🎯 Usage Rapide

### Démonstration Basique

```bash
python quickstart.py
```

### Tests Complets

```bash
python screenplay_test.py
```

### Mode Interactif

```python
# quickstart.py avec mode interactif activé
# Éditer la dernière ligne: interactive_mode(processor)

python quickstart.py
```

## 📁 Structure du Projet

```
Agent_realisateur/
├── 🔧 CONFIGURATION
│   ├── pyproject.toml              # Dépendances Python
│   ├── .env                        # Variables d'environnement
│   └── docker-compose.yml          # Stack Docker (optional)
│
├── 📚 MODULES PRINCIPAUX
│   ├── ontology.py                 # Ontologie + validation
│   ├── entity_extractor.py         # Extraction LLM
│   ├── falkordb_connector.py       # Génération Cypher
│   ├── screenplay_processor.py     # Pipeline orchestration
│   └── screenplay_integration.py   # Intégration LangGraph
│
├── 🧪 TESTS & EXEMPLES
│   ├── screenplay_test.py          # Suite de tests
│   ├── quickstart.py               # Démarrage rapide
│   └── EXAMPLES.md                 # Exemples détaillés
│
├── 📖 DOCUMENTATION
│   ├── SCREENPLAY_PIPELINE.md      # Docs complètes
│   ├── README.md                   # Overview projet
│   ├── GETTING_STARTED.md          # Ce fichier
│   ├── GRAPH_ARCHITECTURE.md       # Architecture du graphe
│   ├── MESSAGE_STORAGE.md          # Stockage messages
│   └── RAG_SETUP.md                # Configuration RAG
│
└── 📊 DONNÉES
    ├── retriever_doc/
    │   └── fight_club_script.txt    # Exemple scénario
    └── supabase_setup.sql          # Schéma Supabase
```

## 🔨 Workflow Courant

### 1. Extraire d'un Chunk

```python
from screenplay_processor import ScreenplayProcessor
from langchain_community.llms import Ollama

llm = Ollama(model="llama3.2:3b")
processor = ScreenplayProcessor(llm)

screenplay = "EXT. PARKING - NUIT\nLuc sort un pistolet."
triples, success, errors = processor.process_screenplay_chunk(screenplay)
```

### 2. Traiter un Fichier Complet

```python
triples, success, errors = processor.process_screenplay_file(
    "./retriever_doc/fight_club_script.txt"
)
print(f"{len(triples)} triplets extraits")
```

### 3. Interroger le Graphe

```python
# Tous les personnages
results = processor.query_graph("MATCH (c:Character) RETURN c.name")

# Relations
results = processor.query_graph(
    "MATCH (p:Prop)-[:USED_BY]->(c:Character) RETURN p.name, c.name"
)
```

### 4. Nettoyer la Base

```python
# Supprimer tous les nœuds (debug)
processor.db.clear_database()
```

## 📊 Anatomie d'un Triplet

```python
Triple {
    subject: "LUC"                               # Nom de l'entité source
    subject_type: NodeType.CHARACTER             # Type: Scene, Character, Location, Prop, Time
    relation: RelationType.APPEARS_IN            # Type de relation
    object: "PARKING_NIGHT"                      # Nom de l'entité cible
    object_type: NodeType.SCENE                  # Type cible
    
    subject_properties: {"role": "Protagonist"}  # Props du source
    object_properties: {"time": "NIGHT"}         # Props du target
}
```

## 🔍 Anatomy de l'Extraction

```
INPUT (Texte Brut)
    ↓
[1] LLM → JSON Triplets
    ↓
[2] Normalisation (JEAN vs jean vs M. Jean)
    ↓
[3] Validation Ontologie (rejected if invalid)
    ↓
[4] Déduplication
    ↓
[5] Génération Cypher MERGE
    ↓
[6] Injection FalkorDB
    ↓
OUTPUT (Graph Node & Relations)
```

## 🎯 Cas d'Usage Courants

### Cas 1: Extraire une Scène

```python
scene_text = """
INT. BUREAU - JOUR
Jean travaille. Marie entre.
MARIE: C'est urgent.
"""

triples, _, _ = processor.process_screenplay_chunk(scene_text)
# ✓ Extrait: Jean, Marie, Bureau, Jour, + relations
```

### Cas 2: Analyser Qui Utilise Quoi

```python
query = """
MATCH (p:Prop)-[:USED_BY]->(c:Character)-[:APPEARS_IN]->(s:Scene)
RETURN c.name, p.name, count(s) as appearances
ORDER BY appearances DESC
"""
processor.query_graph(query)
```

### Cas 3: Créer une Timeline

```python
query = """
MATCH (s:Scene)-[:HAPPENS_DURING]->(t:Time)
MATCH (s)-[:LOCATED_AT]->(l:Location)
RETURN s.id, t.name, l.name
ORDER BY s.number
"""
processor.query_graph(query)
```

## ⚙️ Configuration

### Variables d'Environnement (.env)

```bash
# LLM
LLM_MODEL=llama3.2:3b
LLM_HOST=localhost:11434

# FalkorDB
FALKORDB_HOST=localhost
FALKORDB_PORT=6379

# Logging
LOG_LEVEL=INFO
```

### Settings Avancés

```python
# Custom LLM
from langchain_openai import OpenAI
llm = OpenAI(api_key="sk-...", model="gpt-4")

# Custom FalkorDB
processor = ScreenplayProcessor(
    llm,
    falkordb_host="192.168.1.100",
    falkordb_port=6380
)

# Logging debug
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚨 Troubleshooting

### Erreur: "FalkorDB non disponible"

**Solution**: Vérifier que FalkorDB est lancé

```bash
# Vérifier le statut
docker ps | grep falkordb

# Ou lancer
docker run -p 6379:6379 falkordb/falkordb

# Test de connexion
redis-cli ping  # Doit retourner: PONG
```

### Erreur: "No module named 'falkordb'"

**Solution**: Installer la dépendance

```bash
pip install falkordb
```

### LLM Timeout

**Solution**: Augmenter le timeout ou utiliser un modèle plus rapide

```python
llm = Ollama(
    model="mistral:latest",  # Plus rapide que llama
    request_timeout=120  # Seconds
)
```

### Mémoire Insuffisante

**Solution**: Utiliser un plus petit modèle LLM

```python
llm = Ollama(model="mistral:7b")  # Au lieu de 70b
```

## 📈 Performance

### Benchmark Rapide

```python
import time

screenplay = "..." * 5000  # 5000 chars

processor = ScreenplayProcessor(llm)
start = time.time()
triples, _, _ = processor.process_screenplay_chunk(screenplay)
elapsed = time.time() - start

print(f"Temps: {elapsed:.2f}s")
print(f"Triplets/sec: {len(triples)/elapsed:.1f}")
```

### Optimisations

1. **Batch Processing**: Traiter plusieurs scénarios en parallèle
2. **Caching LLM**: Réutiliser les résultats identiques
3. **Graph Indexing**: Créer des indices FalkorDB
4. **Chunk Size**: Adapter la taille des chunks au LLM

## 🔄 Intégration Existant

### Avec le Graph LangGraph

```python
# Dans graph.py
from screenplay_integration import screenplay_extraction_node

# Ajouter le nœud
workflow.add_node("screenplay_extraction", screenplay_extraction_node)

# Ajouter la route
workflow.add_conditional_edges("conversation", screenplay_router)
```

### Avec Supabase

```python
# Les triples peuvent être stockés dans Supabase
from message_storage import MessageStorage

storage = MessageStorage(supabase)
storage.save_message(
    thread_id,
    "screenplay_extraction",
    f"Extraits: {len(triples)} triplets"
)
```

## 📚 Ressources

| Ressource | Lien |
|-----------|------|
| FalkorDB Docs | https://docs.falkordb.com |
| Cypher Reference | https://opencypher.org/ |
| LangChain | https://python.langchain.com |
| Ollama | https://ollama.ai |

## ✅ Checklist Démarrage

- [ ] Python 3.12+ installé
- [ ] Dépendances installées (`pip install -e .`)
- [ ] Ollama lancé (`ollama serve`)
- [ ] FalkorDB lancé (optionnel)
- [ ] Tests passent (`python screenplay_test.py`)
- [ ] Quickstart fonctionne (`python quickstart.py`)
- [ ] Premier scénario traité avec succès

## 🎯 Prochaines Étapes

1. **Explorer**: Lire SCREENPLAY_PIPELINE.md
2. **Expérimenter**: Lancer les exemples dans EXAMPLES.md
3. **Intégrer**: Ajouter les nœuds au graphe existant
4. **Customizer**: Adapter l'ontologie selon vos besoins
5. **Analyser**: Créer des requêtes Cypher personnalisées

## 🆘 Support

Pour des problèmes:
1. Consulter les logs: `logging.basicConfig(level=logging.DEBUG)`
2. Regarder la section Troubleshooting
3. Tester les cas dans `screenplay_test.py`
4. Vérifier les exemples dans `EXAMPLES.md`

---

**Bon développement! 🚀**
