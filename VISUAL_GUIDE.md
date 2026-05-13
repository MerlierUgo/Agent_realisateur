# 🎬 Screenplay Pipeline - Visual Guide

Représentations visuelles du pipeline complet.

## System Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        SCREENPLAY PROCESSING PIPELINE                      │
└────────────────────────────────────────────────────────────────────────────┘

                            INPUT: Screenplay Text
                                     ▼
                    ┌─────────────────────────────────┐
                    │   ScreenplayProcessor           │
                    │   (Orchestration)               │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │  1. EXTRACTION               │
                    │  EntityExtractor + LLM       │
                    │  Returns: List[Triple]       │
                    └──────────────┬────────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │  2. NORMALIZATION            │
                    │  Ontology.normalize()        │
                    │  "M. Jean" → "JEAN"          │
                    └──────────────┬────────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │  3. VALIDATION               │
                    │  Ontology.is_valid()         │
                    │  Reject invalid relations    │
                    └──────────────┬────────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │  4. DEDUPLICATION            │
                    │  EntityDeduplicator          │
                    │  Remove duplicates           │
                    └──────────────┬────────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │  5. CYPHER GENERATION        │
                    │  CypherGenerator             │
                    │  MERGE queries               │
                    └──────────────┬────────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │  6. DATABASE INJECTION       │
                    │  FalkorDBConnector           │
                    │  Execute Cypher             │
                    └──────────────┬────────────────┘
                                   │
                              OUTPUT
                    ┌──────────────▼───────────────┐
                    │  Knowledge Graph (FalkorDB)  │
                    │  Nodes: S, C, L, P, T        │
                    │  Relations: 5 types          │
                    └───────────────────────────────┘
```

## Module Dependency Graph

```
                          QuickStart/Tests
                                 ▼
                    ┌────────────────────────┐
                    │ ScreenplayProcessor    │
                    │ (Main API)             │
                    └────┬────────────────┬──┘
                         │                │
                ┌────────▼────┐  ┌───────▼────────┐
                │  Entity     │  │  FalkorDB      │
                │ Extractor   │  │  Connector     │
                └────┬────────┘  └───┬────────┬───┘
                     │               │        │
                ┌────▼────┐  ┌───────▼──┐  ┌─▼──────┐
                │ LLM     │  │ Cypher   │  │ Cypher │
                │ (Ollama)│  │Generator │  │Validator
                └─────────┘  └──────────┘  └────────┘
                     ▲
                     │
                     └──────────┬────────────────┐
                          Ontology             Tests
                          (Validation,         (Unit,
                           Normalization)      Integration)
```

## Data Flow Diagram

```
Triple Creation & Processing:

┌──────────────────────────────────────────────────────────────┐
│                      INPUT TRIPLE                            │
│  subject: "Jean" → "M. Jean" → normalize → "JEAN"           │
│  relation: APPEARS_IN                                       │
│  object: "bureau" → normalize → "BUREAU"                    │
│  properties: {role: "Manager"}                              │
└──────────────────────────────────────────────────────────────┘
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                ONTOLOGY VALIDATION                           │
│  ✓ CHARACTER can APPEARS_IN SCENE?                          │
│  ✓ Scene type exists?                                       │
│  ✓ Relation type exists?                                    │
└──────────────────────────────────────────────────────────────┘
                         ▼
┌──────────────────────────────────────────────────────────────┐
│              DEDUPLICATION CHECK                             │
│  Key: (JEAN, CHARACTER, APPEARS_IN, BUREAU, SCENE)          │
│  Already exists? Skip : Keep                                │
└──────────────────────────────────────────────────────────────┘
                         ▼
┌──────────────────────────────────────────────────────────────┐
│           CYPHER QUERY GENERATION                           │
│  MERGE (n:Character {name: 'JEAN'})                         │
│  MERGE (n:Scene {id: 'BUREAU_DAY'})                         │
│  MATCH (s) MATCH (t) MERGE (s)-[:APPEARS_IN]->(t)          │
└──────────────────────────────────────────────────────────────┘
                         ▼
┌──────────────────────────────────────────────────────────────┐
│           FALKORDB EXECUTION                                │
│  Execute Cypher → FalkorDB Redis                            │
│  Result: Nodes & Relationships in Graph                     │
└──────────────────────────────────────────────────────────────┘
```

## Knowledge Graph Schema

```
                         Time
                          ▲
                          │
                   HAPPENS_DURING
                          │
        ┌──────────────────┴──────────────────┐
        │                                     │
       Scene ◄───── LOCATED_AT ────► Location
        │ ▲
        │ │
APPEARS_IN │ PRESENT_IN (reverse)
        │ │
        ▼ │
     Character ◄─── USED_BY ─── Prop
```

### Propriétés par Type

```
Scene {
  id: "PARKING_NIGHT"
  name: "EXT. PARKING"
  description: "..."
  number: 1
  interior_exterior: "EXT"
  time_of_day: "NIGHT"
}

Character {
  name: "JEAN"
  role: "PDG"
  description: "..."
}

Location {
  name: "PARKING"
  description: "..."
  type: "exterior"
}

Prop {
  name: "PISTOLET"
  description: "..."
  category: "weapon"
}

Time {
  name: "NIGHT"
  type: "NIGHT"
}
```

## LLM Interaction Flow

```
User Screenplay:
"EXT. PARKING - NUIT
Luc sort un pistolet."
        │
        ▼
┌─────────────────────────────────────────┐
│  System Prompt + Screenplay             │
│  "Extract entities as JSON triplets"    │
└─────────────────────┬───────────────────┘
                      │ invoke()
                      ▼
              ┌───────────────┐
              │  LLM (Ollama) │
              └───────┬───────┘
                      │
                      ▼ JSON Response
        ┌─────────────────────────────┐
        │ {                           │
        │   "triples": [              │
        │     {                       │
        │       "subject": "Luc",     │
        │       "subject_type": "CHARACTER",
        │       "relation": "APPEARS_IN",
        │       "object": "PARKING_NIGHT",
        │       "object_type": "SCENE"
        │     }                       │
        │   ]                         │
        │ }                           │
        └────────┬────────────────────┘
                 │
                 ▼ Parse & Validate
        ┌─────────────────────────────┐
        │ List[Triple] (validated)    │
        │ Ready for DB injection      │
        └─────────────────────────────┘
```

## Class Hierarchy

```
Enums:
├─ NodeType
│  ├─ SCENE
│  ├─ CHARACTER
│  ├─ LOCATION
│  ├─ PROP
│  └─ TIME
└─ RelationType
   ├─ APPEARS_IN
   ├─ LOCATED_AT
   ├─ USED_BY
   ├─ PRESENT_IN
   └─ HAPPENS_DURING

DataClasses:
├─ RelationshipRule
│  ├─ relation_type: RelationType
│  ├─ source_type: NodeType
│  └─ target_type: NodeType
└─ Triple
   ├─ subject: str
   ├─ subject_type: NodeType
   ├─ relation: RelationType
   ├─ object: str
   ├─ object_type: NodeType
   ├─ subject_properties: Dict
   └─ object_properties: Dict

Static Classes:
├─ Ontology
│  ├─ is_valid_relationship()
│  ├─ normalize_entity_name()
│  └─ sanitize_property_value()
├─ EntityExtractor
│  ├─ extract_entities()
│  └─ extract_scenes_from_screenplay()
├─ EntityDeduplicator
│  └─ deduplicate_triples()
├─ CypherGenerator
│  ├─ generate_merge_queries()
│  ├─ _generate_node_merge()
│  └─ _generate_relation_merge()
├─ CypherValidator
│  └─ validate_merge_query()
└─ FalkorDBConnector
   ├─ execute_query()
   ├─ inject_triples()
   ├─ get_all_nodes()
   └─ get_all_relationships()

Main Classes:
└─ ScreenplayProcessor
   ├─ process_screenplay_chunk()
   ├─ process_screenplay_file()
   ├─ query_graph()
   └─ get_scene_structure()
```

## State Transitions

```
Triple State Machine:

┌─────────────────┐
│   Raw Triple    │  (From LLM extraction)
│  (Not validated)│
└────────┬────────┘
         │ normalize()
         ▼
┌─────────────────┐
│ Normalized      │  (Names uppercase, cleaned)
│  Triple         │
└────────┬────────┘
         │ is_valid()
         ▼
    ┌────────────────┐
    │ Valid?         │
    └─┬──────────┬───┘
      │ Yes      │ No
      ▼          ▼
  ┌───────┐  ┌─────────┐
  │ Keep  │  │ Discard │
  └───┬───┘  └─────────┘
      │
      ▼
┌──────────────────────┐
│ Deduplicated         │  (Duplicates removed)
│ Triples             │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Cypher Generated     │  (SQL-like queries)
│ Queries             │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Injected in          │  (Nodes & Relations
│ FalkorDB Graph       │   created/updated)
└──────────────────────┘
```

## Integration Points

```
Existing Project:

┌────────────────────────────┐
│  Agent Réalisateur         │
│  (LangGraph + LLMs)        │
└────────┬───────────────────┘
         │
         │ Uses
         ▼
┌────────────────────────────┐
│  Screenplay Processor      │  ◄─── NEW
│  (Knowledge Graph)         │
└────────┬────────┬──────────┘
         │        │
         │        └─ Query FalkorDB
         │
    Nodes:
    ├─ screenplay_extraction_node
    ├─ scene_structure_query_node
    └─ custom_graph_query_node
```

## Error Handling Flow

```
         Operation
              │
              ▼
        ┌──────────┐
        │ Try      │
        └────┬─────┘
             │
    ┌────────┴────────┐
    │ Success?        │
    └─┬──────────┬────┘
      │ Yes      │ No
      ▼          ▼
  ┌────────┐  ┌───────────────────┐
  │ Count  │  │ Log Error         │
  │ Success│  │ Increment errors  │
  └────────┘  │ Continue (skip)   │
              └───────────────────┘
              
              ▼
         ┌─────────────────┐
         │ Final Counts:   │
         │ (success, err)  │
         └─────────────────┘
```

## Performance Profile

```
Operation              Time          Count
──────────────────────────────────────────
Extract (LLM)         2-5s           1 per chunk
Normalize             <1ms           per triple
Validate              <1ms           per triple
Deduplicate           <1ms           per chunk
Generate Cypher       <1ms           per triple
Execute Cypher        50-200ms       per triple
──────────────────────────────────────────
Total per chunk       2-5s           + DB I/O
Total per file        ~10-30s        (depends on LLM)
```

## Configuration Hierarchy

```
Default Values (hardcoded)
       ▲
       │ Override with
       │
Environment Variables (.env)
       ▲
       │ Override with
       │
Function Parameters
       ▲
       │ Runtime changes
       │
Runtime Configuration
```

Example:
```
LLM_MODEL: "llama3.2:3b"     (env)
ScreenplayProcessor(
    llm,
    falkordb_host="localhost" (param)
)
logging.basicConfig(          (runtime)
    level=logging.DEBUG
)
```

---

## 📚 Legend

```
Box Types:
┌─────────┐
│ Process │  = Operation/Module
└─────────┘

Connections:
    ▼      = Data flow
    ◄──►   = Bidirectional
    ◀──    = Reference

Symbols:
✓  = Valid
✗  = Invalid
→  = Transforms to
```

---

**Visual Guide Complete! 🎨**
