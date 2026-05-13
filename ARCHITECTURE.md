# 📋 Structure & Architecture du Pipeline

Documentation détaillée de l'architecture du pipeline Screenplay → FalkorDB.

## 🏗️ Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────────┐
│                  SCREENPLAY INPUT                           │
│              (Text Scénario en Chunk ou Fichier)            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           ENTITY EXTRACTOR (LLM)                            │
│  • Parse screenplay chunk                                   │
│  • Appel LLM pour extraction entités                        │
│  • Parse JSON response                                      │
│  • Crée objets Triple                                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           NORMALIZATION & VALIDATION                        │
│  • Normalise noms d'entités (JEAN, jean, M. Jean → JEAN)  │
│  • Valide contre ontologie                                  │
│  • Rejette relations non autorisées                         │
│  • Déduplique les triplets                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           CYPHER GENERATOR                                  │
│  • Crée requêtes MERGE Cypher                              │
│  • MERGE node1, MERGE node2, MERGE relation                │
│  • Assure idempotence                                       │
│  • Escape les valeurs                                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           FALKORDB CONNECTOR                                │
│  • Établit connexion Redis                                  │
│  • Exécute requêtes Cypher                                  │
│  • Gère erreurs                                             │
│  • Retourne résultats                                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              KNOWLEDGE GRAPH (FalkorDB)                     │
│  • Nœuds: Scene, Character, Location, Prop, Time          │
│  • Relations: APPEARS_IN, LOCATED_AT, USED_BY, etc.        │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Modules et Responsabilités

### 1. `ontology.py` - Définition de l'Ontologie

**Responsabilités:**
- Définir les types de nœuds (NodeType enum)
- Définir les types de relations (RelationType enum)
- Valider les relations autorisées (RelationshipRule)
- Normaliser les noms d'entités
- Sanitizer les valeurs pour Cypher

**Classes principales:**
- `NodeType`: SCENE, CHARACTER, LOCATION, PROP, TIME
- `RelationType`: APPEARS_IN, LOCATED_AT, USED_BY, PRESENT_IN, HAPPENS_DURING
- `Ontology`: Méthodes statiques pour validation et normalisation
- `Triple`: Représente un triplet sujet-relation-objet

**Exemple:**

```python
# Validation
if Ontology.is_valid_relationship(NodeType.CHARACTER, RelationType.APPEARS_IN, NodeType.SCENE):
    print("✓ Relation valide")

# Normalisation
name = Ontology.normalize_entity_name("M. Jean")  # → "JEAN"

# Sanitize
safe_value = Ontology.sanitize_property_value("C'est une \"citation\"")
# → C'est une \"citation\"
```

### 2. `entity_extractor.py` - Extraction d'Entités

**Responsabilités:**
- Appeler le LLM pour extraction
- Parser la réponse JSON
- Convertir en objets Triple
- Valider contre l'ontologie
- Gérer les erreurs LLM

**Classes principales:**
- `EntityExtractor`: Orchestration extraction
- `EntityDeduplicator`: Déduplication des triplets

**Workflow:**

```
Prompt + Screenplay
        ↓
   invoke(LLM)
        ↓
   JSON Response
        ↓
   Parse & Create Triple objects
        ↓
   Normalize names
        ↓
   Validate against Ontology
        ↓
   Return List[Triple]
```

**Exemple:**

```python
extractor = EntityExtractor(llm)
triples = extractor.extract_entities("EXT. PARKING - NUIT\nLuc...")
# ✓ 2 triplets extraits

deduplicator = EntityDeduplicator()
deduped = deduplicator.deduplicate_triples(triples)
# ✓ 1 doublon supprimé
```

### 3. `falkordb_connector.py` - Gestion FalkorDB

**Responsabilités:**
- Générer requêtes MERGE Cypher
- Gérer la connexion FalkorDB
- Exécuter les requêtes
- Gérer les erreurs d'exécution

**Classes principales:**
- `CypherGenerator`: Génération requêtes Cypher
- `FalkorDBConnector`: Gestion connexion et exécution
- `CypherValidator`: Validation basique Cypher

**Workflow Cypher:**

```
Triple
  ├─ Node Merge (Subject)
  │  MERGE (n:Character {name: 'LUC'})
  │
  ├─ Node Merge (Object)
  │  MERGE (n:Scene {id: 'PARKING_NIGHT'})
  │
  └─ Relation Merge
     MATCH (s:Character {name: 'LUC'})
     MATCH (t:Scene {id: 'PARKING_NIGHT'})
     MERGE (s)-[:APPEARS_IN]->(t)
```

**Exemple:**

```python
connector = FalkorDBConnector(host="localhost", port=6379)

# Exécuter une requête
result = connector.execute_query("MATCH (n:Character) RETURN n.name")

# Injecter des triplets
success, errors = connector.inject_triples(triples)

# Requête personnalisée
characters = connector.get_all_nodes(NodeType.CHARACTER)
```

### 4. `screenplay_processor.py` - Orchestration Pipeline

**Responsabilités:**
- Orchestrer le pipeline complet
- Diviser le scénario en chunks
- Appeler les étapes séquentiellement
- Gérer les logs et résumés
- Exposer l'API utilisateur

**Classes principales:**
- `ScreenplayProcessor`: Pipeline principal

**Étapes Principales:**

```
1. Extraction entités via LLM
2. Normalisation noms
3. Validation ontologie
4. Déduplication
5. Génération Cypher
6. Injection FalkorDB
```

**Exemple:**

```python
processor = ScreenplayProcessor(llm, falkordb_host="localhost")

# Traiter un chunk
triples, success, errors = processor.process_screenplay_chunk(screenplay)

# Traiter un fichier
triples, success, errors = processor.process_screenplay_file("script.txt")

# Interroger le graphe
results = processor.query_graph("MATCH (c:Character) RETURN c.name")
```

### 5. `screenplay_integration.py` - Intégration LangGraph

**Responsabilités:**
- Créer des nœuds LangGraph
- Router vers le bon nœud
- Intégrer avec Agent Réalisateur existant

**Nœuds disponibles:**
- `screenplay_extraction_node`: Extraction entités
- `scene_structure_query_node`: Récupérer structure scène
- `custom_graph_query_node`: Requête personnalisée

**Exemple:**

```python
from screenplay_integration import screenplay_extraction_node

# Intégrer au graphe
workflow.add_node(
    "screenplay_extraction",
    lambda state: screenplay_extraction_node(state, processor)
)
```

## 🔄 Flux de Données

### Chunk Processing

```
screenplay_text (string)
        ↓
EntityExtractor.extract_entities()
        ↓
List[Triple] (entités brutes)
        ↓
Triple.normalize() (boucle)
        ↓
List[Triple] (entités normalisées)
        ↓
EntityDeduplicator.deduplicate_triples()
        ↓
List[Triple] (entités dédup)
        ↓
CypherGenerator.generate_merge_queries()
        ↓
List[str] (requêtes Cypher)
        ↓
FalkorDBConnector.execute_queries()
        ↓
(success: int, errors: int)
```

### File Processing

```
screenplay_file (path)
        ↓
ScreenplayProcessor._chunk_screenplay()
        ↓
List[str] (chunks)
        ↓
process_screenplay_chunk() (boucle pour chaque chunk)
        ↓
List[Triple] (tous les triplets)
        ↓
(total_success: int, total_errors: int)
```

## 📊 Ontologie Graphique

### Nœuds Autorisés

```
┌──────────────┐
│    Scene     │  id, name, description, number, interior_exterior, time_of_day
└──────────────┘

┌──────────────┐
│  Character   │  name, role, description
└──────────────┘

┌──────────────┐
│  Location    │  name, description, type
└──────────────┘

┌──────────────┐
│     Prop     │  name, description, category
└──────────────┘

┌──────────────┐
│     Time     │  name, type (DAY, NIGHT, etc.)
└──────────────┘
```

### Relations Autorisées

```
Character ──APPEARS_IN──> Scene
Scene ──LOCATED_AT──> Location
Prop ──USED_BY──> Character
Prop ──PRESENT_IN──> Scene
Scene ──HAPPENS_DURING──> Time
```

### Matrice de Validation

| Source | Relation | Target | Valide |
|--------|----------|--------|--------|
| Character | APPEARS_IN | Scene | ✅ |
| Character | LOCATED_AT | Location | ❌ |
| Scene | LOCATED_AT | Location | ✅ |
| Scene | HAPPENS_DURING | Time | ✅ |
| Prop | USED_BY | Character | ✅ |
| Prop | PRESENT_IN | Scene | ✅ |

## 🎯 Points de Décision

### 1. Extraction via LLM

**Entrée:** Text brut
**Sortie:** JSON avec triplets
**Logique:** 
- LLM reçoit prompt guidant
- Extrait sujet, relation, objet
- Retourne JSON structuré

### 2. Normalisation

**Entrée:** Nom brut (ex: "M. Jean")
**Sortie:** Nom normalisé (ex: "JEAN")
**Logique:**
- Majuscules
- Articles supprimés
- Titres supprimés
- Espaces multiples réduits

### 3. Validation Ontologie

**Entrée:** Triple (sujet-relation-objet)
**Sortie:** Valide (True/False)
**Logique:**
- Cherche dans VALID_RELATIONSHIPS
- Vérifie source, relation, target
- Retourne True si trouvé

### 4. Déduplication

**Entrée:** List[Triple]
**Sortie:** List[Triple] (dedupliquée)
**Logique:**
- Crée clé unique: (subject, subject_type, relation, object, object_type)
- Garde première occurrence
- Rejette doublons

### 5. Génération Cypher

**Entrée:** Triple
**Sortie:** Requête MERGE Cypher
**Logique:**
- MERGE nœud source avec identifiants
- MERGE nœud cible avec identifiants
- MERGE la relation entre eux
- Combine les trois requêtes

## 📝 Format JSON (LLM Response)

**Format attendu:**

```json
{
  "triples": [
    {
      "subject": "LUC",
      "subject_type": "CHARACTER",
      "relation": "APPEARS_IN",
      "object": "PARKING_NIGHT",
      "object_type": "SCENE",
      "subject_properties": {
        "role": "Protagonist"
      },
      "object_properties": {
        "description": "Dark parking"
      }
    }
  ]
}
```

**Parsing:**
- Cherche bloc JSON dans réponse
- Parse avec json.loads()
- Extrait "triples" array
- Crée Triple pour chaque item

## 🔐 Sécurité

### Escape Cypher

```python
# Avant
name = 'Jean "The Killer"'

# Après (après sanitize_property_value)
name = 'Jean \"The Killer\"'

# Cypher Safe
MERGE (n:Character {name: 'Jean \"The Killer\"'})
```

### Validation Ontologie

```python
# Relations invalides rejetées
Triple(
    subject="JEAN",
    subject_type=NodeType.CHARACTER,
    relation=RelationType.LOCATED_AT,  # ❌ Invalid!
    object="BUREAU",
    object_type=NodeType.LOCATION
).is_valid()  # False
```

## 📊 Gestion d'Erreurs

### Niveaux d'Erreur

1. **LLM Error**: API non réponse ou format JSON invalide
   - → Loggé en ERROR, triplet ignoré
   
2. **Ontology Error**: Relation non autorisée
   - → Loggé en WARNING, triplet rejeté
   
3. **Cypher Error**: Syntaxe invalide ou propriétés
   - → Loggé en ERROR, requête pas exécutée
   
4. **FalkorDB Error**: Connexion ou exécution
   - → Loggé en ERROR, counted as error

### Récupération

```
try:
    triple = create_triple_from_dict(data)
    if not triple.is_valid():
        log.warning("Invalid ontology")
        continue  # Skip this triple
    queries = generate_cypher(triple)
    execute(queries)
except Exception as e:
    log.error(f"Error: {e}")
    error_count += 1
```

## 🧪 Points de Test

### Unit Tests
- Normalisation de noms
- Validation d'ontologie
- Génération Cypher

### Integration Tests
- Extraction complète
- Déduplication
- Injection FalkorDB (mock)

### End-to-End Tests
- Fichier complet → Graphe
- Requêtes sur le graphe
- Mode simulation

## 📈 Performance

### Profiling

```python
import cProfile
cProfile.run('processor.process_screenplay_chunk(screenplay)')
```

### Optimisations

1. **Cache LLM**: Réutiliser extractions identiques
2. **Batch Cypher**: Combiner requêtes
3. **Index FalkorDB**: Créer indices sur properties clés
4. **Chunking**: Adapter taille chunks au LLM

## 🔌 Points d'Extension

### 1. Custom LLM

```python
class CustomLLM:
    def invoke(self, prompt):
        # Custom logic
        return response

processor = ScreenplayProcessor(CustomLLM())
```

### 2. Custom Ontology

```python
# Ajouter une nouvelle relation
Ontology.VALID_RELATIONSHIPS.append(
    RelationshipRule(
        RelationType.CUSTOM,
        NodeType.CHARACTER,
        NodeType.LOCATION
    )
)
```

### 3. Custom Properties

```python
# Ajouter propriétés à un type de nœud
Ontology.NODE_PROPERTIES[NodeType.CHARACTER].add("nationality")
```

### 4. Custom Query

```python
# Exécuter requête personnalisée
results = processor.query_graph("""
    MATCH (c:Character)-[:APPEARS_IN]->(s:Scene {time_of_day: 'NIGHT'})
    RETURN c.name, count(s) as night_scenes
""")
```

## 📚 Workflow Complet Visuel

```
┌──────────────────────────────────────────────────────────┐
│ User: screenplay_text                                    │
└────────────────────┬─────────────────────────────────────┘
                     │
          ┌──────────▼──────────┐
          │ ScreenplayProcessor │
          └──────────┬──────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
    [Chunk?]   [Extract]    [Log Start]
        │            │            │
        └────────────┼────────────┘
                     │
              ┌──────▼──────┐
              │ EntityExtractorresence
              │ + LLM Call  │
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │ Parse JSON  │
              │ + Create    │
              │   Triples   │
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │ Normalize   │
              │ Names       │
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │ Validate    │
              │ Ontology    │
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │ Dedup       │
              │ Triples     │
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │ Generate    │
              │ Cypher      │
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │ FalkorDB    │
              │ Execute     │
              └──────┬──────┘
                     │
          ┌──────────▼──────────┐
          │ (success, errors)   │
          └─────────────────────┘
```

---

C'est l'architecture complète du pipeline! 🎉
