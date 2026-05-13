# 🔧 Setup & Ressources Complètes

Guide complet d'installation et ressources pour le pipeline Screenplay.

## 🚀 Installation Pas à Pas

### Étape 1: Prérequis Système

#### Windows
```bash
# Vérifier Python
python --version  # Doit être >= 3.12

# Vérifier Git
git --version

# Vérifier Docker (optionnel pour FalkorDB)
docker --version
```

#### macOS
```bash
# Installer via Homebrew si nécessaire
brew install python@3.12
brew install docker

# Vérifier
python3 --version
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.12 python3-pip docker.io

# Vérifier
python3 --version
```

### Étape 2: Clone/Setup du Projet

```bash
# Naviguer à la racine du projet
cd d:\perso\Agent_realisateur

# Créer venv (optionnel mais recommandé)
python -m venv .venv

# Activer venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

# Installer dépendances
pip install -e .
```

### Étape 3: Setup LLM (Ollama)

```bash
# Option A: Installer Ollama
# Télécharger depuis https://ollama.ai
# Ou:
# macOS
brew install ollama

# Linux
curl https://ollama.ai/install.sh | sh

# Démarrer Ollama
ollama serve

# Dans un autre terminal, télécharger le modèle
ollama pull llama3.2:3b
```

### Étape 4: Setup FalkorDB (Optionnel)

#### Option A: Docker (Recommandé)

```bash
# Démarrer FalkorDB
docker run -p 6379:6379 falkordb/falkordb

# Ou avec docker-compose
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  falkordb:
    image: falkordb/falkordb:latest
    ports:
      - "6379:6379"
    volumes:
      - falkordb_data:/var/lib/falkordb
    environment:
      - FALKORDB_SAVE_ON_BGSAVE_ERROR=no
volumes:
  falkordb_data:
EOF

docker-compose up -d
```

#### Option B: Redis CLI (Vérifier)

```bash
# Installer Redis CLI (pour debug)
# macOS
brew install redis

# Windows (via WSL ou standalone Redis)
# Linux
sudo apt install redis-tools

# Tester connexion
redis-cli ping
# Doit retourner: PONG
```

### Étape 5: Configuration Variables d'Environnement

```bash
# Créer .env
cat > .env << 'EOF'
# LLM Configuration
LLM_MODEL=llama3.2:3b
LLM_HOST=localhost:11434

# FalkorDB Configuration
FALKORDB_HOST=localhost
FALKORDB_PORT=6379

# Logging
LOG_LEVEL=INFO

# Supabase (existant)
REACT_APP_SUPABASE_URL=your_url
REACT_APP_ANON_KEY=your_key
EOF
```

### Étape 6: Vérifier l'Installation

```bash
# Tester tous les modules
python -c "import ontology, entity_extractor, falkordb_connector, screenplay_processor"
print("✅ All imports successful")

# Lancer les tests
python screenplay_test.py
# Doit voir: ✅ TOUS LES TESTS TERMINÉS

# Lancer quickstart
python quickstart.py
# Doit traiter l'exemple scénario
```

---

## 📦 Installation Avancée

### Setup avec Virtual Environment (Recommandé)

```bash
# Créer venv Python
python3.12 -m venv screenplay_env

# Activer
# Windows
screenplay_env\Scripts\activate
# Unix
source screenplay_env/bin/activate

# Vérifier
which python  # Doit montrer screenplay_env

# Installer dans venv
pip install -e .

# Vérifier
pip list | grep falkordb
```

### Setup avec Poetry

```bash
# Installer Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Initialiser (si pas de pyproject.toml)
poetry init

# Installer dépendances
poetry install

# Activer environnement
poetry shell
```

### Setup avec Docker (Full Stack)

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .

RUN pip install -e .

COPY . .

CMD ["python", "quickstart.py"]
```

```bash
# Build et run
docker build -t screenplay-pipeline .
docker run -p 6379:6379 screenplay-pipeline
```

---

## 🔍 Vérification Installation

### Checklist

```bash
# 1. Python
python --version              # ✅ >= 3.12

# 2. Dépendances
pip list | grep -E "falkordb|langchain|ollama"

# 3. Imports
python -c "
from ontology import Ontology
from entity_extractor import EntityExtractor
from falkordb_connector import FalkorDBConnector
from screenplay_processor import ScreenplayProcessor
print('✅ All modules importable')
"

# 4. LLM (Ollama)
curl http://localhost:11434/api/tags  # ✅ Connecté

# 5. Database (FalkorDB)
redis-cli ping                         # ✅ PONG

# 6. Tests
python screenplay_test.py             # ✅ All pass

# 7. Quickstart
python quickstart.py                  # ✅ Working
```

---

## 🛠️ Troubleshooting Installation

### Problème: "No module named 'falkordb'"

**Solution:**
```bash
# Installer explicitement
pip install falkordb

# Ou réinstaller tout
pip install -e . --force-reinstall
```

### Problème: "LLM Timeout"

**Cause:** Ollama n'est pas lancé ou trop lent
**Solution:**
```bash
# Vérifier Ollama
curl http://localhost:11434/api/tags

# Redémarrer Ollama
# Fermer tous les terminaux Ollama
# Relancer: ollama serve

# Utiliser modèle plus rapide
ollama pull mistral:7b  # Plus rapide que llama
```

### Problème: "Connection refused (FalkorDB)"

**Cause:** FalkorDB/Redis pas lancé
**Solution:**
```bash
# Docker
docker run -p 6379:6379 falkordb/falkordb

# Ou docker-compose
docker-compose up -d

# Vérifier
redis-cli ping  # Doit retourner PONG
```

### Problème: "Memory Error"

**Cause:** Modèle LLM trop gros
**Solution:**
```bash
# Utiliser modèle plus petit
ollama pull mistral:latest        # 7B params
# Ou
ollama pull neural-chat:latest    # Optimisé

# Configuration
processor = ScreenplayProcessor(
    Ollama(model="mistral:latest"),
    request_timeout=120  # Plus de temps
)
```

### Problème: "Port already in use"

**Cause:** FalkorDB/Ollama déjà lancé
**Solution:**
```bash
# Vérifier processus
lsof -i :6379     # Redis/FalkorDB
lsof -i :11434    # Ollama

# Tuer processus (si nécessaire)
kill -9 <PID>

# Ou utiliser différent port
docker run -p 6380:6379 falkordb/falkordb
processor = ScreenplayProcessor(
    llm,
    falkordb_port=6380
)
```

---

## 📚 Ressources Recommandées

### Documentation Officielle

| Ressource | URL | Documentation |
|-----------|-----|-----------------|
| **FalkorDB** | https://falkordb.com | Graph database |
| **Cypher** | https://opencypher.org | Query language |
| **Redis** | https://redis.io | Data store |
| **LangChain** | https://python.langchain.com | LLM framework |
| **Ollama** | https://ollama.ai | Local LLM |

### Tutoriels & Guides

```
Knowledge Graphs:
├─ Comprehensive Knowledge Graphs
│  https://www.manning.com/books/
├─ Knowledge Graph By Example
│  https://en.wikipedia.org/wiki/Knowledge_graph
└─ GraphQL & Knowledge Graphs
   https://blog.apollographql.com/

Cypher Query:
├─ Cypher Query Language
│  https://opencypher.org/
├─ Property Graph Model
│  https://neo4j.com/docs/cypher-manual/
└─ FalkorDB Cypher Docs
   https://docs.falkordb.com/

LLM & NLP:
├─ LangChain Tutorials
│  https://python.langchain.com/docs/get_started/
├─ Prompt Engineering Guide
│  https://www.promptingguide.ai/
└─ Entity Recognition
   https://huggingface.co/docs/transformers/
```

### Communautés & Support

```
Forums:
├─ Stack Overflow [tag:falkordb]
├─ Stack Overflow [tag:cypher]
├─ LangChain Discord
└─ Ollama GitHub Discussions

GitHub:
├─ FalkorDB Issues: https://github.com/FalkorDB/FalkorDB
├─ LangChain Issues: https://github.com/langchain-ai/langchain
└─ Ollama Issues: https://github.com/ollama/ollama
```

---

## 🚀 Quick Commands Reference

### Installation
```bash
pip install -e .                    # Install deps
pip install falkordb                # Explicit FalkorDB
pip install -r requirements.txt     # From requirements
```

### Services
```bash
ollama serve                        # Start LLM
docker run -p 6379:6379 falkordb/falkordb  # Start DB
redis-cli ping                      # Test connection
```

### Testing
```bash
python screenplay_test.py           # All tests
python screenplay_test.py 2>&1 | grep -i pass  # Test results
python quickstart.py                # Quick start
```

### Debugging
```bash
# Logs détaillés
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from screenplay_processor import ScreenplayProcessor
# ... run code
"

# REPL
python -i quickstart.py  # Interactive mode
```

### Database
```bash
redis-cli                           # Redis CLI
redis-cli FLUSHALL                  # Clear database
redis-cli MONITOR                   # Watch commands
redis-cli --raw < script.txt       # Run script
```

---

## 📋 Configuration Checklist

- [ ] Python 3.12+ installed
- [ ] pip/venv configured
- [ ] Dependencies installed (`pip install -e .`)
- [ ] Ollama installed and running
- [ ] FalkorDB running (docker or local)
- [ ] .env file configured
- [ ] Tests passing (`python screenplay_test.py`)
- [ ] Quickstart working (`python quickstart.py`)
- [ ] Redis CLI working (`redis-cli ping`)

---

## 🔐 Security Best Practices

### Dépendances
```bash
# Vérifier vulnérabilités
pip install safety
safety check

# Ou
pip install pip-audit
pip-audit
```

### API Keys
```bash
# Ne JAMAIS committer .env
git add .gitignore
echo ".env" >> .gitignore

# Utiliser variables d'environnement seulement
export LLM_API_KEY="your_key"
```

### FalkorDB
```bash
# Si en production, sécuriser Redis
# Ajouter auth dans docker-compose
command: redis-server --requirepass yourpassword

# Dann in code:
db = FalkorDB(
    host="...",
    port=6379,
    password="yourpassword"
)
```

---

## 📈 Performance Tuning

### LLM Optimization
```python
# Cache LLM responses
from langchain.cache import InMemoryCache
import langchain
langchain.llm_cache = InMemoryCache()

# Plus rapide avec timeout
llm = Ollama(
    model="mistral:latest",
    request_timeout=60,
    top_p=0.1  # Moins varié mais rapide
)
```

### Database Optimization
```bash
# FalkorDB settings
docker run \
  -e "FALKORDB_THREAD_COUNT=4" \
  -e "FALKORDB_IO_THREADS=4" \
  -p 6379:6379 \
  falkordb/falkordb
```

### Memory Management
```python
# Chunk screenplay for large files
processor = ScreenplayProcessor(llm)
chunk_size = 1000  # characters

screenplay = read_large_file()
chunks = [screenplay[i:i+chunk_size] 
          for i in range(0, len(screenplay), chunk_size)]

for chunk in chunks:
    processor.process_screenplay_chunk(chunk)
    # Process chunked
```

---

## 🐛 Debug Mode

```python
import logging

# Ultra detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('screenplay.log'),
        logging.StreamHandler()
    ]
)

# Run with debug
from screenplay_processor import ScreenplayProcessor
processor = ScreenplayProcessor(llm)
processor.process_screenplay_chunk(text)

# Check logs
cat screenplay.log | tail -50
```

---

## 📞 Getting Help

1. **Check Documentation**
   - [GETTING_STARTED.md](GETTING_STARTED.md)
   - [SCREENPLAY_PIPELINE.md](SCREENSHOT_PIPELINE.md)
   - [EXAMPLES.md](EXAMPLES.md)

2. **Review Tests**
   - [screenplay_test.py](screenplay_test.py)
   - Run: `python screenplay_test.py`

3. **Check Logs**
   - Enable DEBUG logging
   - Look for error messages

4. **Verify Installation**
   - Run checklist above
   - Test each component separately

5. **Search Online**
   - FalkorDB: https://github.com/FalkorDB/FalkorDB/issues
   - LangChain: https://github.com/langchain-ai/langchain/discussions
   - Ollama: https://github.com/ollama/ollama/issues

---

**Setup Complete! 🎉**

Now run: `python quickstart.py`
