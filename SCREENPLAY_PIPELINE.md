# 🎬 Screenplay to Knowledge Graph Pipeline

Pipeline Python complet pour extraire les entités et relations structurées d'un scénario de film et les injecter dans FalkorDB via Cypher.

## 📋 Architecture

### Modules Principaux

```
ontology.py                  # Ontologie du graphe (nœuds, relations, validation)
entity_extractor.py          # Extraction d'entités via LLM
falkordb_connector.py        # Génération Cypher et exécution FalkorDB
screenplay_processor.py      # Pipeline d'orchestration
screenplay_test.py           # Tests et démo
```

## 🎯 Ontologie

### Nœuds (Node Types)

| Type | Description | Propriétés |
|------|-------------|-----------|
| **Scene** | Une scène du film | id, name, description, number, interior_exterior, time_of_day |
| **Character** | Un personnage | name, role, description |
| **Location** | Un lieu | name, description, type |
| **Prop** | Un accessoire/objet | name, description, category |
| **Time** | Moment de la journée | name, type (DAY, NIGHT, etc.) |

### Relations (Relationship Types)

```
Character -[:APPEARS_IN]-> Scene
Scene -[:LOCATED_AT]-> Location
Prop -[:USED_BY]-> Character
Prop -[:PRESENT_IN]-> Scene
Scene -[:HAPPENS_DURING]-> Time
```

## 🔄 Workflow

### Étape 1: Extraction via LLM
- Prend un chunk de texte de scénario
- Utilise un LLM (Ollama, GPT, etc.) pour extraire les entités et relations
- Retourne des triplets JSON (Sujet, Relation, Objet)

### Étape 2: Normalisation
- Convertit les noms en majuscules
- Harmonise les variantes (ex: "Jean", "M. Jean" → "JEAN")
- Supprime les articles inutiles

### Étape 3: Validation
- Vérifie que chaque relation respecte l'ontologie
- Rejette les triplets invalides avec avertissement

### Étape 4: Déduplication
- Élimine les triplets en doublon
- Conserve les propriétés uniques

### Étape 5: Génération Cypher
- Crée des requêtes MERGE Cypher idempotentes
- Assure l'unicité des nœuds

### Étape 6: Injection FalkorDB
- Exécute les requêtes contre le serveur FalkorDB
- Rapporte les succès/erreurs

## 💾 Installation

### 1. Dépendances Python

```bash
# Installer les dépendances
pip install -r requirements.txt

# Ou via pyproject.toml
pip install -e .
```

### 2. FalkorDB

#### Option A: Docker (Recommandé)

```bash
# Démarrer FalkorDB en tant que conteneur
docker run -p 6379:6379 falkordb/falkordb

# Ou avec docker-compose
cat > docker-compose.yml << EOF
version: '3'
services:
  falkordb:
    image: falkordb/falkordb
    ports:
      - "6379:6379"
    volumes:
      - falkordb_data:/var/lib/falkordb
volumes:
  falkordb_data:
EOF

docker-compose up -d
```

#### Option B: Depuis les sources

```bash
# Voir la documentation FalkorDB
# https://github.com/FalkorDB/FalkorDB
```

## 🚀 Utilisation

### Usage Basique

```python
from screenplay_processor import ScreenplayProcessor
from langchain_community.llms import Ollama

# Initialiser le LLM
llm = Ollama(model="llama3.2:3b")

# Créer le processeur
processor = ScreenplayProcessor(llm, falkordb_host="localhost", falkordb_port=6379)

# Traiter un chunk de scénario
screenplay_text = """
EXT. PARKING - NUIT
Luc sort un pistolet de sa poche et le pose sur le capot de la voiture.
"""

triples, success, errors = processor.process_screenplay_chunk(screenplay_text)
print(f"Traité: {len(triples)} triplets, {success} succès, {errors} erreurs")
```

### Traiter un Fichier Complet

```python
# Traiter un fichier scénario
triples, success, errors = processor.process_screenplay_file("script.md")
```

### Query le Graphe

```python
# Exemple: Récupérer la structure d'une scène
result = processor.query_graph("MATCH (s:Scene) RETURN s LIMIT 5")

# Récupérer tous les personnages d'une scène
result = processor.query_graph("""
  MATCH (c:Character)-[:APPEARS_IN]->(s:Scene {id: 'PARKING_NIGHT'})
  RETURN c.name, c.role
""")
```

## 📊 Exemple de Transformation

### Input
```
EXT. PARKING - NUIT
Luc sort un pistolet de sa poche.
Sarah l'observe de loin.
```

### Extraction (JSON)
```json
{
  "triples": [
    {
      "subject": "Luc",
      "subject_type": "Character",
      "relation": "APPEARS_IN",
      "object": "PARKING_NIGHT",
      "object_type": "Scene",
      "subject_properties": {},
      "object_properties": {}
    },
    {
      "subject": "Pistolet",
      "subject_type": "Prop",
      "relation": "USED_BY",
      "object": "Luc",
      "object_type": "Character",
      "subject_properties": {},
      "object_properties": {}
    }
  ]
}
```

### Cypher Généré

```cypher
MERGE (n:Character {name: 'LUC'}) SET n += {}
MERGE (n:Scene {id: 'PARKING_NIGHT'}) SET n += {}
MATCH (s:Character {name: 'LUC'}) MATCH (t:Scene {id: 'PARKING_NIGHT'}) MERGE (s)-[:APPEARS_IN]->(t)

MERGE (n:Prop {name: 'PISTOLET'}) SET n += {}
MATCH (s:Prop {name: 'PISTOLET'}) MATCH (t:Character {name: 'LUC'}) MERGE (s)-[:USED_BY]->(t)
```

### Résultat dans FalkorDB
```
Graph with nodes:
- (LUC:Character)
- (PISTOLET:Prop)
- (PARKING_NIGHT:Scene)

And relations:
- (LUC)-[:APPEARS_IN]->(PARKING_NIGHT)
- (PISTOLET)-[:USED_BY]->(LUC)
```

## 🧪 Tests

```bash
# Lancer les tests
python screenplay_test.py

# Ou avec pytest
pytest screenplay_test.py -v
```

### Tests Disponibles

1. **test_extraction_without_db()** - Extraction de scènes sans LLM
2. **test_cypher_generation()** - Génération de requêtes Cypher
3. **test_deduplication()** - Déduplication de triplets
4. **test_ontology_validation()** - Validation selon l'ontologie
5. **test_full_pipeline_with_mock_llm()** - Pipeline complet avec mock LLM

## 🔒 Sécurité

- **SQL Injection Cypher**: Les valeurs sont correctement échappées
- **Validation d'Ontologie**: Rejette les relations non autorisées
- **Logs Structurés**: Tous les événements sont loggés

## 📝 Logging

```python
import logging

# Activer les logs détaillés
logging.basicConfig(
    level=logging.DEBUG,  # ou INFO, WARNING
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

### Niveaux de Log

- **DEBUG**: Détails de chaque operation
- **INFO**: Résumés de progression
- **WARNING**: Anomalies (doublons, relations invalides)
- **ERROR**: Erreurs graves (connexion, parsing)

## 🛠️ Configuration Avancée

### Personnaliser l'Ontologie

```python
from ontology import Ontology, NodeType, RelationType, RelationshipRule

# Ajouter une nouvelle relation autorisée
Ontology.VALID_RELATIONSHIPS.append(
    RelationshipRule(
        RelationType.SOME_NEW_RELATION,
        NodeType.CHARACTER,
        NodeType.LOCATION
    )
)
```

### Adapter le Prompt d'Extraction

```python
from entity_extractor import EntityExtractor

extractor = EntityExtractor(llm)
extractor.EXTRACTION_SYSTEM_PROMPT = "Votre prompt personnalisé..."
```

### Configurer FalkorDB

```python
processor = ScreenplayProcessor(
    llm,
    falkordb_host="192.168.1.100",
    falkordb_port=6380,
    # graph_name="mon_film"  # Si FalkorDBConnector est adapté
)
```

## 🐛 Troubleshooting

### Erreur: "falkordb-py n'est pas installé"

```bash
pip install falkordb
```

### Erreur: "Connexion refusée à FalkorDB"

```bash
# Vérifier que FalkorDB est running
docker ps | grep falkordb

# Ou démarrer FalkorDB
docker run -p 6379:6379 falkordb/falkordb
```

### Le LLM n'extrait rien

- Vérifier que le LLM est accessible
- Augmenter le timeout du LLM
- Adapter le prompt d'extraction
- Utiliser un LLM plus puissant

### Requêtes Cypher non valides

- Vérifier les logs pour les caractères échappés
- Tester les requêtes manuellement avec `redis-cli`
- Valider avec `CypherValidator`

## 📚 Ressources

- [FalkorDB Documentation](https://docs.falkordb.com)
- [Cypher Query Language](https://opencypher.org/)
- [LangChain LLM Integration](https://python.langchain.com/docs/integrations/llms/)

## 📄 Fichiers

```
ontology.py              # Définition ontologie + validation
entity_extractor.py      # Extraction entités + déduplication
falkordb_connector.py    # Génération Cypher + connexion
screenplay_processor.py  # Pipeline orchestration
screenplay_test.py       # Tests et démonstration
```

## 🎓 Cas d'Usage

### 1. Analyser un Scénario Complet

```python
processor = ScreenplayProcessor(llm)
triples, success, errors = processor.process_screenplay_file("fight_club.md")
```

### 2. Extraire la Structure d'une Scène

```python
scene_structure = processor.get_scene_structure("PARKING_NIGHT")
print(scene_structure)  # Characters, Props, Location, Time
```

### 3. Requête Personnalisée

```python
# Tous les props utilisés par un personnage
query = """
MATCH (p:Prop)-[:USED_BY]->(c:Character {name: 'LUC'})
RETURN p.name, p.category
"""
results = processor.query_graph(query)
```

## 🔄 Intégration avec Agent Réalisateur

```python
# Dans nodes.py ou graph.py
from screenplay_processor import ScreenplayProcessor

processor = ScreenplayProcessor(llm)

def extract_scene_structure_node(state: AgentRealState):
    """Extrait la structure d'une scène du scénario"""
    # ...
    return {"context": processor.get_scene_structure(scene_id)}
```

---

**Version**: 0.1.0  
**Auteur**: Data Engineering Team  
**Dernière mise à jour**: Mai 2026
