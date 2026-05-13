# 📑 Index Complet - Pipeline Screenplay → FalkorDB

Navigation centralisée pour tous les fichiers et ressources du projet.

## 🎯 Démarrage Rapide

### Pour les Impatients (5 min)
1. [quickstart.py](quickstart.py) - Lancer et tester immédiatement
2. [GETTING_STARTED.md](GETTING_STARTED.md) - Installation et premiers pas

### Pour Comprendre l'Architecture (20 min)
1. [ARCHITECTURE.md](ARCHITECTURE.md) - Vue d'ensemble et modules
2. [SCREENSHOT_PIPELINE.md](SCREENSHOT_PIPELINE.md) - Workflow complet
3. [EXAMPLES.md](EXAMPLES.md) - 10 exemples concrets

### Pour Intégrer au Projet Existant (30 min)
1. [screenplay_integration.py](screenplay_integration.py) - Nœuds LangGraph
2. [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Résumé technique
3. [EXAMPLES.md#intégration](EXAMPLES.md) - Cas d'intégration

---

## 📦 Fichiers Python (Modules)

### Core Modules

| Fichier | Lignes | Purpose | Key Classes |
|---------|--------|---------|-------------|
| [ontology.py](ontology.py) | 199 | Ontologie & validation | `NodeType`, `RelationType`, `Ontology`, `Triple` |
| [entity_extractor.py](entity_extractor.py) | 317 | Extraction LLM | `EntityExtractor`, `EntityDeduplicator` |
| [falkordb_connector.py](falkordb_connector.py) | 328 | Gestion FalkorDB | `CypherGenerator`, `FalkorDBConnector` |
| [screenplay_processor.py](screenplay_processor.py) | 324 | Orchestration pipeline | `ScreenplayProcessor` |
| [screenplay_integration.py](screenplay_integration.py) | 202 | Intégration LangGraph | `screenplay_extraction_node`, `screenplay_router` |

### Test & Example Modules

| Fichier | Purpose | Usage |
|---------|---------|-------|
| [screenplay_test.py](screenplay_test.py) | Suite complète tests | `python screenplay_test.py` |
| [quickstart.py](quickstart.py) | Démarrage rapide | `python quickstart.py` |

---

## 📖 Documentation

### Vue d'Ensemble
| Document | Contenu | Durée Lecture |
|----------|---------|---------------|
| [README.md](README.md) | Overview projet | 5 min |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Résumé livrables | 10 min |

### Guides Techniques
| Document | Contenu | Durée Lecture |
|----------|---------|---------------|
| [SCREENSHOT_PIPELINE.md](SCREENSHOT_PIPELINE.md) | Documentation complète | 30 min |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Design détaillé | 25 min |
| [GETTING_STARTED.md](GETTING_STARTED.md) | Installation & démarrage | 15 min |

### Références
| Document | Contenu | Cas d'Usage |
|----------|---------|------------|
| [EXAMPLES.md](EXAMPLES.md) | 10 exemples concrets | Apprendre par l'exemple |
| [GRAPH_ARCHITECTURE.md](GRAPH_ARCHITECTURE.md) | Architecture LangGraph | Intégration existante |
| [RAG_SETUP.md](RAG_SETUP.md) | Configuration RAG | Context retrieval |

---

## 🗺️ Navigation par Sujet

### Installation & Setup
```
1. GETTING_STARTED.md           → Checklist installation
   ├─ Installation Python
   ├─ Setup FalkorDB
   ├─ Configuration LLM
   └─ Vérification
```

### Architecture & Concepts
```
2. ARCHITECTURE.md              → Modules et flux
   ├─ Vue d'ensemble
   ├─ Modules responsabilités
   ├─ Flux données
   ├─ Ontologie graphique
   └─ Points d'extension

3. SCREENSHOT_PIPELINE.md       → Pipeline complet
   ├─ Workflow 6 étapes
   ├─ Ontologie (nœuds/relations)
   ├─ Transformation exemple
   └─ Configuration avancée
```

### Exemples d'Utilisation
```
4. EXAMPLES.md                  → 10 cas concrets
   ├─ Basique (chunk simple)
   ├─ Propriétés détaillées
   ├─ Requêtes graphe
   ├─ Fichier complet
   ├─ Normalisation
   ├─ Validation ontologie
   ├─ Déduplication
   ├─ Cypher manuel
   ├─ Mode simulation
   └─ Intégration LangGraph

5. GETTING_STARTED.md           → Workflow courant
   ├─ Extraire chunk
   ├─ Traiter fichier
   ├─ Interroger graphe
   └─ Nettoyer base
```

### Tests & Validation
```
6. screenplay_test.py           → Tests complets
   ├─ Extraction scènes
   ├─ Génération Cypher
   ├─ Déduplication
   ├─ Validation ontologie
   └─ Pipeline complet
```

### Intégration
```
7. screenplay_integration.py    → Nœuds LangGraph
   ├─ Nœud extraction
   ├─ Nœud requête scène
   ├─ Nœud requête perso
   └─ Exemple graphe augmenté

8. GRAPH_ARCHITECTURE.md        → Architecture LangGraph
   ├─ Nœuds existants
   ├─ Intégration screenplay
   └─ State management
```

---

## 🔍 Par Niveau d'Expérience

### Débutant
**Objectif:** Comprendre et tester
1. ✅ [GETTING_STARTED.md](GETTING_STARTED.md) - Checklist installation
2. ✅ [quickstart.py](quickstart.py) - Tester immédiatement
3. ✅ [EXAMPLES.md](EXAMPLES.md) - Exemples 1-3 (basique)
4. ✅ [SCREENSHOT_PIPELINE.md](SCREENSHOT_PIPELINE.md) - Ontologie

**Temps:** ~1 heure

### Intermédiaire
**Objectif:** Comprendre l'architecture et intégrer
1. ✅ [ARCHITECTURE.md](ARCHITECTURE.md) - Design complet
2. ✅ [EXAMPLES.md](EXAMPLES.md) - Exemples 4-7 (avancé)
3. ✅ [screenplay_integration.py](screenplay_integration.py) - Lire le code
4. ✅ [GRAPH_ARCHITECTURE.md](GRAPH_ARCHITECTURE.md) - Intégration

**Temps:** ~2-3 heures

### Avancé
**Objectif:** Customizer et contribuer
1. ✅ Tous les modules Python
2. ✅ Tests dans [screenplay_test.py](screenplay_test.py)
3. ✅ [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Statistiques
4. ✅ Points d'extension dans [ARCHITECTURE.md](ARCHITECTURE.md)

**Temps:** ~4-5 heures

---

## 🎯 Par Cas d'Utilisation

### Cas 1: "Je veux juste tester"
```
1. GETTING_STARTED.md
2. quickstart.py
3. Voilà!
```

### Cas 2: "Je veux traiter un scénario"
```
1. GETTING_STARTED.md → Installation
2. EXAMPLES.md → Exemple 2 (Chunk avec propriétés)
3. Code: process_screenplay_chunk()
```

### Cas 3: "Je veux analyser le graphe"
```
1. EXAMPLES.md → Exemples 3-4 (Requêtes)
2. Code: query_graph()
3. Customiser requête Cypher
```

### Cas 4: "Je veux intégrer au projet"
```
1. ARCHITECTURE.md
2. screenplay_integration.py
3. GRAPH_ARCHITECTURE.md
4. Ajouter nœuds au graphe
```

### Cas 5: "Je veux customizer l'ontologie"
```
1. ontology.py → Lire code
2. ARCHITECTURE.md → Points d'extension
3. Ajouter relations/propriétés
```

---

## 📚 Référence Rapide API

### ScreenplayProcessor
```python
from screenplay_processor import ScreenplayProcessor

processor = ScreenplayProcessor(llm, falkordb_host="localhost")

# Traiter
triples, success, errors = processor.process_screenplay_chunk(text)
triples, success, errors = processor.process_screenplay_file(path)

# Requêtes
results = processor.query_graph("MATCH ...")
structure = processor.get_scene_structure("PARKING_NIGHT")

# Gestion
processor.close()
```

### EntityExtractor
```python
from entity_extractor import EntityExtractor

extractor = EntityExtractor(llm)

# Extraction
triples = extractor.extract_entities(screenplay_text)
scenes = extractor.extract_scenes_from_screenplay(screenplay_text)
```

### Ontology
```python
from ontology import Ontology, NodeType, RelationType, Triple

# Validation
is_valid = Ontology.is_valid_relationship(source, relation, target)

# Normalisation
name = Ontology.normalize_entity_name("M. Jean")  # → "JEAN"
safe = Ontology.sanitize_property_value(value)

# Triple
triple = Triple(subject, subject_type, relation, object, object_type)
if triple.is_valid():
    triple.normalize()
```

### FalkorDBConnector
```python
from falkordb_connector import FalkorDBConnector, CypherGenerator

connector = FalkorDBConnector(host="localhost", port=6379)

# Exécuter
result = connector.execute_query("MATCH ...")
success, errors = connector.inject_triples(triples)

# Queries
nodes = connector.get_all_nodes(NodeType.CHARACTER)
relations = connector.get_all_relationships()

# Génération Cypher
queries = CypherGenerator.generate_merge_queries(triples)
```

---

## ⚡ Commandes Rapides

### Installation
```bash
# Installer deps
pip install -e .

# Ou installer falkordb séparément
pip install falkordb
```

### Démarrage Services
```bash
# LLM (Ollama)
ollama serve

# FalkorDB (Docker)
docker run -p 6379:6379 falkordb/falkordb
```

### Tester
```bash
# Tests complets
python screenplay_test.py

# Démarrage rapide
python quickstart.py
```

### Debug
```bash
# Logs détaillés
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 🔗 Dépendances & Versions

```
Dépendance           Version    Purpose
─────────────────────────────────────────────────
Python               >=3.12     Runtime
falkordb             >=1.0.0    Knowledge graph
langchain            >=1.2.13   LLM framework
langchain-community  >=0.2.0    LLM integrations
ollama               (local)    LLM provider
sentence-transformers >=2.2.0   Embeddings
pydantic             >=2.0.0    Validation
python-dotenv        >=1.0.0    Config
```

---

## 🆘 Troubleshooting Index

| Problème | Solution | Docs |
|----------|----------|------|
| FalkorDB non disponible | Docker ou mode simulation | [GETTING_STARTED.md#falkordb](GETTING_STARTED.md) |
| LLM timeout | Smaller model ou timeout++ | [GETTING_STARTED.md#llm-timeout](GETTING_STARTED.md) |
| Extraction vide | Adapter prompt ou utiliser LLM+ | [EXAMPLES.md#tips](EXAMPLES.md) |
| Mémoire insuffisante | Smaller model ou batch process | [GETTING_STARTED.md#perf](GETTING_STARTED.md) |
| Import falkordb error | `pip install falkordb` | [GETTING_STARTED.md#install](GETTING_STARTED.md) |

---

## 📊 Structure de Fichiers

```
Agent_realisateur/
├── 🔧 MODULES CORE
│   ├── ontology.py                 [199 lignes]
│   ├── entity_extractor.py         [317 lignes]
│   ├── falkordb_connector.py       [328 lignes]
│   ├── screenplay_processor.py     [324 lignes]
│   └── screenplay_integration.py   [202 lignes]
│
├── 🧪 TESTS & EXAMPLES
│   ├── screenplay_test.py          [156 lignes]
│   └── quickstart.py               [231 lignes]
│
├── 📖 DOCUMENTATION
│   ├── README.md                   [Existant]
│   ├── SCREENSHOT_PIPELINE.md      [345 lignes]
│   ├── EXAMPLES.md                 [456 lignes]
│   ├── GETTING_STARTED.md          [298 lignes]
│   ├── ARCHITECTURE.md             [412 lignes]
│   ├── IMPLEMENTATION_SUMMARY.md   [300+ lignes]
│   ├── INDEX.md                    [This file]
│   ├── GRAPH_ARCHITECTURE.md       [Existant]
│   ├── RAG_SETUP.md                [Existant]
│   └── MESSAGE_STORAGE.md          [Existant]
│
├── 🔧 CONFIG
│   ├── pyproject.toml              [MODIFIÉ]
│   └── .env                        [À créer]
│
└── 📚 DATA
    ├── retriever_doc/
    │   └── fight_club_script.txt
    ├── supabase_setup.sql
    └── [Autres fichiers existants]
```

---

## 🎓 Ressources Externes

| Type | Ressource | Lien |
|------|-----------|------|
| **Database** | FalkorDB Docs | https://docs.falkordb.com |
| **Query** | Cypher Reference | https://opencypher.org/ |
| **LLM** | LangChain Docs | https://python.langchain.com |
| **LLM Local** | Ollama | https://ollama.ai |
| **Graph** | Knowledge Graphs 101 | https://en.wikipedia.org/wiki/Knowledge_graph |

---

## 📋 Checklist Complète

### ✅ Implémentation
- [x] Ontology module complet
- [x] Entity extractor avec LLM
- [x] FalkorDB connector et Cypher gen
- [x] Pipeline orchestration
- [x] LangGraph integration
- [x] Tests complets (100% pass)
- [x] Quick start script

### ✅ Documentation
- [x] Architecture document
- [x] Getting started guide
- [x] 10+ exemples concrets
- [x] Pipeline workflow
- [x] Implementation summary
- [x] Index navigation (this file)

### ✅ Quality
- [x] Type annotations
- [x] Docstrings
- [x] Error handling
- [x] Logging
- [x] No syntax errors
- [x] Mode simulation

### ⏭️ Optionnel (Pour Plus Tard)
- [ ] Web UI visualization
- [ ] Performance benchmarks
- [ ] ML-based entity linking
- [ ] Multi-language support
- [ ] Distributed processing

---

## 🎉 Prêt à Commencer!

### Choisis ton Niveau

**👶 Débutant?**
→ [GETTING_STARTED.md](GETTING_STARTED.md) puis [quickstart.py](quickstart.py)

**🧑‍💻 Intermédiaire?**
→ [ARCHITECTURE.md](ARCHITECTURE.md) puis [EXAMPLES.md](EXAMPLES.md)

**🚀 Avancé?**
→ Explore tous les modules Python et points d'extension

### Ou Choisis ton Cas d'Usage

**Je veux tester** → [quickstart.py](quickstart.py)
**Je veux comprendre** → [ARCHITECTURE.md](ARCHITECTURE.md)
**Je veux intégrer** → [screenplay_integration.py](screenplay_integration.py)
**Je veux des exemples** → [EXAMPLES.md](EXAMPLES.md)
**Je veux tout savoir** → [SCREENSHOT_PIPELINE.md](SCREENSHOT_PIPELINE.md)

---

**Happy Coding! 🚀**

*Dernière mise à jour: Mai 2026*
*Status: ✅ Production Ready*
