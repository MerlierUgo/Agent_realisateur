# 📖 Exemples d'Utilisation - Screenplay Pipeline

Exemples concrets et cas d'usage du pipeline d'extraction scénario → FalkorDB.

## 1️⃣ Exemple Basique - Traiter un Chunk Simple

### Code

```python
from screenplay_processor import ScreenplayProcessor
from langchain_community.llms import Ollama

# Initialiser le LLM
llm = Ollama(model="llama3.2:3b")

# Créer le processeur
processor = ScreenplayProcessor(llm)

# Traiter un chunk de scénario
screenplay = """
EXT. PARKING - NUIT
Luc sort un pistolet et le pose sur le capot.
Sarah regarde de loin.
"""

triples, success, errors = processor.process_screenplay_chunk(screenplay)

print(f"✅ {success} requêtes Cypher injectées")
print(f"📊 {len(triples)} triplets extraits")

for triple in triples:
    print(f"  • {triple.subject} -> {triple.relation.value} -> {triple.object}")
```

### Output Attendu

```
✅ 2 requêtes Cypher injectées
📊 2 triplets extraits
  • LUC -> APPEARS_IN -> PARKING_NIGHT
  • SARAH -> APPEARS_IN -> PARKING_NIGHT
```

---

## 2️⃣ Extraction avec Propriétés

### Scénario Détaillé

```python
screenplay_with_details = """
INT. BUREAU - JOUR

Jean, 45 ans, PDG de TechCorp, travaille à son ordinateur.
Sur son bureau: un stylo Montblanc vert et une photo de famille.
Marie, 32 ans, assistante, entre avec urgence.

MARIE
C'est urgent. Les documents du contrat sont signés.

JEAN
Excellente nouvelle. Où sont-ils?

Marie pose une clé USB "Top Secret" sur le bureau.
"""

processor = ScreenplayProcessor(llm)
triples, _, _ = processor.process_screenplay_chunk(screenplay_with_details)

# Afficher les triplets avec propriétés
for triple in triples:
    print(f"{triple.subject}")
    if triple.subject_properties:
        print(f"  Propriétés: {triple.subject_properties}")
    print(f"  └─ {triple.relation.value} ─> {triple.object}")
    if triple.object_properties:
        print(f"     Propriétés: {triple.object_properties}")
```

### Résultat

```
JEAN
  Propriétés: {'age': '45', 'role': 'PDG'}
  └─ APPEARS_IN ─> BUREAU_DAY
     Propriétés: {'time_of_day': 'DAY', 'interior_exterior': 'INT'}

MARIE
  └─ APPEARS_IN ─> BUREAU_DAY

STYLO
  Propriétés: {'category': 'objet de valeur', 'description': 'Montblanc vert'}
  └─ PRESENT_IN ─> BUREAU_DAY

CLÉ_USB
  Propriétés: {'security_level': 'Top Secret'}
  └─ USED_BY ─> MARIE
```

---

## 3️⃣ Requêtes sur le Graphe

### Récupérer Tous les Personnages

```python
query = "MATCH (c:Character) RETURN c.name, c.role"
results = processor.query_graph(query)
print("Personnages trouvés:")
for result in results:
    print(f"  - {result[0]} ({result[1]})")
```

### Requête: Tous les Props d'une Scène

```python
query = """
MATCH (p:Prop)-[:PRESENT_IN]->(s:Scene {id: 'BUREAU_DAY'})
RETURN p.name, p.category
"""
results = processor.query_graph(query)
print("Props dans BUREAU_DAY:")
for prop_name, category in results:
    print(f"  - {prop_name} ({category})")
```

### Requête: Qui utilise quel Objet?

```python
query = """
MATCH (p:Prop)-[:USED_BY]->(c:Character)-[:APPEARS_IN]->(s:Scene)
RETURN c.name, p.name, s.id
"""
results = processor.query_graph(query)
print("Qui utilise quoi:")
for character, prop, scene in results:
    print(f"  {character} utilise {prop} dans {scene}")
```

### Requête: Graphe Complet d'une Scène

```python
scene_id = "BUREAU_DAY"
structure = processor.get_scene_structure(scene_id)
print(f"Structure de {scene_id}:")
print(f"  Personnages: {structure['characters']}")
print(f"  Props: {structure['props']}")
print(f"  Lieu: {structure['location']}")
print(f"  Heure: {structure['time']}")
```

---

## 4️⃣ Traiter un Fichier Complet

### Code

```python
from pathlib import Path

# Traiter le script Fight Club
screenplay_file = Path("./retriever_doc/fight_club_script.txt")

processor = ScreenplayProcessor(llm)
all_triples, total_success, total_errors = processor.process_screenplay_file(
    str(screenplay_file)
)

print(f"📚 Fichier: {screenplay_file.name}")
print(f"📊 Statistiques:")
print(f"   - Triplets extraits: {len(all_triples)}")
print(f"   - Injections réussies: {total_success}")
print(f"   - Erreurs: {total_errors}")
```

### Analysé

```
📚 Fichier: fight_club_script.txt
📊 Statistiques:
   - Triplets extraits: 324
   - Injections réussies: 324
   - Erreurs: 0
```

---

## 5️⃣ Normalisation des Noms

### Avant/Après

```python
from ontology import Ontology, NodeType

examples = [
    "Jean",
    "M. Jean",
    "le pistolet",
    "L'épée",
    "Un couteau",
    "Des stylos",
    "Mme Marie",
    "Dr. Dupont"
]

print("Normalisation des noms:")
for name in examples:
    normalized = Ontology.normalize_entity_name(name)
    print(f"  '{name}' → '{normalized}'")
```

### Output

```
Normalisation des noms:
  'Jean' → 'JEAN'
  'M. Jean' → 'JEAN'
  'le pistolet' → 'PISTOLET'
  'L'épée' → 'ÉPÉE'
  'Un couteau' → 'COUTEAU'
  'Des stylos' → 'STYLOS'
  'Mme Marie' → 'MARIE'
  'Dr. Dupont' → 'DUPONT'
```

---

## 6️⃣ Validation de l'Ontologie

### Détection de Relations Invalides

```python
from ontology import Triple, NodeType, RelationType, Ontology

# Tentative de créer une relation invalide
invalid_triple = Triple(
    subject="JEAN",
    subject_type=NodeType.CHARACTER,
    relation=RelationType.LOCATED_AT,  # ❌ CHARACTER ne peut pas LOCATED_AT
    object="BUREAU",
    object_type=NodeType.LOCATION
)

print(f"Relation valide? {invalid_triple.is_valid()}")

# Afficher les relations autorisées pour CHARACTER
valid_relations = Ontology.get_valid_targets(NodeType.CHARACTER, RelationType.APPEARS_IN)
print(f"CHARACTER peut APPEARS_IN: {valid_relations}")
```

### Output

```
Relation valide? False
CHARACTER peut APPEARS_IN: {<NodeType.SCENE: 'Scene'>}
```

---

## 7️⃣ Déduplication

### Avant/Après

```python
from entity_extractor import EntityDeduplicator

# Créer des triplets en doublon
triple1 = Triple(
    subject="Jean",
    subject_type=NodeType.CHARACTER,
    relation=RelationType.APPEARS_IN,
    object="BUREAU_DAY",
    object_type=NodeType.SCENE
)

triple2 = Triple(
    subject="JEAN",  # Même personne, différente casse
    subject_type=NodeType.CHARACTER,
    relation=RelationType.APPEARS_IN,
    object="bureau_day",  # Même scène, différente casse
    object_type=NodeType.SCENE
)

triple3 = Triple(
    subject="Marie",
    subject_type=NodeType.CHARACTER,
    relation=RelationType.APPEARS_IN,
    object="BUREAU_DAY",
    object_type=NodeType.SCENE
)

all_triples = [triple1, triple2, triple3]

# Normaliser
for t in all_triples:
    t.normalize()

# Dédupliquer
deduplicator = EntityDeduplicator()
deduped = deduplicator.deduplicate_triples(all_triples)

print(f"Avant dédup: {len(all_triples)} triplets")
print(f"Après dédup: {len(deduped)} triplets")
```

### Output

```
Avant dédup: 3 triplets
Après dédup: 2 triplets
```

---

## 8️⃣ Générer Cypher Manuellement

### Code

```python
from falkordb_connector import CypherGenerator
from ontology import Triple, NodeType, RelationType

triples = [
    Triple(
        subject="LUC",
        subject_type=NodeType.CHARACTER,
        relation=RelationType.APPEARS_IN,
        object="PARKING_NIGHT",
        object_type=NodeType.SCENE,
        subject_properties={"role": "Protagonist"},
        object_properties={"description": "Dark parking"}
    )
]

queries = CypherGenerator.generate_merge_queries(triples)

for i, query in enumerate(queries, 1):
    print(f"Query {i}:\n{query}\n")
```

### Output

```
Query 1:
MERGE (n:Character {name: 'LUC'}) SET n += {role: 'Protagonist'} 
MERGE (n:Scene {id: 'PARKING_NIGHT'}) SET n += {name: 'PARKING_NIGHT', description: 'Dark parking'} 
MATCH (s:Character {name: 'LUC'}) MATCH (t:Scene {id: 'PARKING_NIGHT'}) 
MERGE (s)-[:APPEARS_IN]->(t)
```

---

## 9️⃣ Mode Simulation (Sans FalkorDB)

### Code

```python
from screenplay_processor import ScreenplayProcessor

# LLM mock
class MockLLM:
    def invoke(self, prompt):
        return '{"triples": []}'

llm = MockLLM()

# Processeur en mode simulation
processor = ScreenplayProcessor(llm)

if not processor.db_available:
    print("⚠️  Mode simulation (FalkorDB non disponible)")
    print("Les requêtes Cypher seront affichées mais non exécutées")

screenplay = "EXT. PARKING - NUIT\nLuc sort un pistolet."
triples, success, _ = processor.process_screenplay_chunk(screenplay)
```

---

## 🔟 Intégration avec Agent Réalisateur

### Dans le Graphe LangGraph

```python
from screenplay_integration import screenplay_extraction_node
from screenplay_processor import ScreenplayProcessor

# Initialiser le processeur
llm = Ollama(model="llama3.2:3b")
processor = ScreenplayProcessor(llm)

# Ajouter un nœud au graphe existant
workflow.add_node(
    "screenplay_extraction",
    lambda state: screenplay_extraction_node(state, processor)
)

# Router sémantique
def route_message(state):
    if "scène" in str(state["messages"][-1]).lower():
        return "screenplay_extraction"
    return "conversation"

workflow.add_conditional_edges("conversation", route_message)
```

---

## 📊 Cas d'Usage Avancés

### Analyser les Relations Entre Personnages

```python
query = """
MATCH (c1:Character)-[:APPEARS_IN]->(s:Scene)<-[:APPEARS_IN]-(c2:Character)
WHERE c1.name < c2.name
RETURN c1.name, c2.name, s.id, count(*) as co_appearances
ORDER BY co_appearances DESC
"""
results = processor.query_graph(query)
print("Duos les plus fréquents:")
for c1, c2, scene, count in results:
    print(f"  {c1} & {c2}: {count} scènes ensemble")
```

### Trouver les Props Critiques

```python
query = """
MATCH (p:Prop)-[:USED_BY]->(c:Character)-[:APPEARS_IN]->(s:Scene)
RETURN p.name, count(DISTINCT c) as characters, count(DISTINCT s) as scenes
ORDER BY characters DESC, scenes DESC
LIMIT 10
"""
results = processor.query_graph(query)
print("Props les plus importants:")
for prop, char_count, scene_count in results:
    print(f"  {prop}: {char_count} personnages, {scene_count} scènes")
```

### Chronologie des Scènes

```python
query = """
MATCH (s:Scene)-[:HAPPENS_DURING]->(t:Time)
WHERE t.type = 'NIGHT'
MATCH (c:Character)-[:APPEARS_IN]->(s)
RETURN s.id, collect(c.name) as characters, s.description
"""
results = processor.query_graph(query)
print("Scènes nocturnes:")
for scene_id, characters, desc in results:
    print(f"  {scene_id}: {', '.join(characters)}")
```

---

## 🎬 Complet: Pipeline Fin à Fin

```python
#!/usr/bin/env python3
"""Pipeline complet: scénario → FalkorDB → Analyse"""

from screenplay_processor import ScreenplayProcessor
from langchain_community.llms import Ollama
from pathlib import Path

def main():
    # 1. Initialisation
    print("🎬 Pipeline Scénario Complet\n")
    
    llm = Ollama(model="llama3.2:3b")
    processor = ScreenplayProcessor(llm)
    
    # 2. Traiter le fichier
    script_file = Path("./retriever_doc/fight_club_script.txt")
    print(f"📖 Traitement: {script_file.name}")
    
    triples, success, errors = processor.process_screenplay_file(str(script_file))
    
    # 3. Statistiques
    print(f"\n📊 Résultats:")
    print(f"   Triplets: {len(triples)}")
    print(f"   Injections: {success} ✅ {errors} ❌")
    
    # 4. Analyses
    print(f"\n🔍 Analyses:")
    
    # Personnages
    chars = processor.query_graph("MATCH (c:Character) RETURN count(c) as count")
    print(f"   Personnages: {chars[0][0] if chars else 0}")
    
    # Lieux
    locs = processor.query_graph("MATCH (l:Location) RETURN count(l) as count")
    print(f"   Lieux: {locs[0][0] if locs else 0}")
    
    # Scènes
    scenes = processor.query_graph("MATCH (s:Scene) RETURN count(s) as count")
    print(f"   Scènes: {scenes[0][0] if scenes else 0}")
    
    # Props
    props = processor.query_graph("MATCH (p:Prop) RETURN count(p) as count")
    print(f"   Accessoires: {props[0][0] if props else 0}")
    
    # 5. Fermeture
    processor.close()
    print("\n✅ Terminé")

if __name__ == "__main__":
    main()
```

---

## 🚀 Tips & Tricks

### 1. Optimiser le LLM

```python
# Utiliser un modèle plus puissant pour extraction complexe
llm = Ollama(model="llama2:70b")  # Plus lent mais meilleur

# Ou utiliser un API commercial
# from langchain.llms import OpenAI
# llm = OpenAI(api_key="sk-...", model="gpt-4")
```

### 2. Batch Processing

```python
def process_screenplay_batch(processor, screenplay_file, chunk_size=1000):
    with open(screenplay_file) as f:
        text = f.read()
    
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
    all_triples = []
    for chunk in chunks:
        triples, _, _ = processor.process_screenplay_chunk(chunk)
        all_triples.extend(triples)
    
    return all_triples
```

### 3. Caching LLM

```python
from langchain.cache import InMemoryCache
import langchain

langchain.llm_cache = InMemoryCache()

# Identiques requêtes → résultats cachés
processor = ScreenplayProcessor(llm)
```

### 4. Logging Détaillé

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# Maintenant tous les détails sont affichés
processor.process_screenplay_chunk(screenplay)
```

---

Fin de la documentation des exemples! 🎉
