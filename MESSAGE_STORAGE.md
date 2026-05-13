# 💾 Sauvegarde des Messages dans Supabase

## 📋 Vue d'ensemble

La sauvegarde des messages est maintenant intégrée à l'Agent Réalisateur. Tous les messages utilisateur et assistant sont automatiquement sauvegardés dans Supabase.

## 🔧 Configuration requise

### 1. Mettre à jour le schéma Supabase

Exécutez le SQL mis à jour dans `supabase_setup.sql`:

```sql
-- Cette commande crée la table 'messages'
CREATE TABLE IF NOT EXISTS messages (
  id bigserial primary key,
  session_id text NOT NULL,
  role text NOT NULL,
  content text NOT NULL,
  created_at timestamp default now()
);
```

**Steps:**
- Allez dans **SQL Editor** de votre dashboard Supabase
- Collez le contenu complet de `supabase_setup.sql`
- Exécutez-la

### 2. Les messages sont sauvegardés automatiquement

Une fois le code déployé, **tous les messages** seront automatiquement sauvegardés:
- Messages de l'utilisateur (`role: 'user'`)
- Réponses de l'assistant (`role: 'assistant'`)

## 📖 Utilisation

### Sauvegarde automatique

Lors d'une conversation, les messages sont sauvegardés automatiquement:

```
👤 Réalisateur: Bonjour!
✅ Message sauvegardé (role: user)

🤖 Assistant: Bonjour! Comment puis-je vous aider?
✅ Message sauvegardé (role: assistant)
```

Chaque session a un ID unique (`session_id`) qui permet de regrouper les messages.

### Utilisation manuelle du MessageStorage

Si vous voulez interagir directement avec les messages:

```python
from message_storage import MessageStorage
from supabase import create_client, Client

# Initialiser
supabase = create_client(url, key)
storage = MessageStorage(supabase)

# Sauvegarder un message
storage.save_message("session_123", "user", "Bonjour!")

# Récupérer tous les messages d'une session
messages = storage.get_session_messages("session_123")

# Récupérer les 10 derniers messages
recent = storage.get_latest_messages("session_123", limit=10)

# Supprimer une session
storage.delete_session_messages("session_123")

# Nettoyer les anciens messages (>30 jours)
storage.clear_old_messages(days_old=30)
```

## 🗂️ Structure de la table messages

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | bigint (PK) | Identifiant unique |
| `session_id` | text | ID de la session/conversation |
| `role` | text | 'user' ou 'assistant' |
| `content` | text | Contenu du message |
| `created_at` | timestamp | Date/heure de création |

## 🔐 Sécurité (RLS)

Les Row Level Security (RLS) sont activées:
- ✅ INSERT autorisé (sauvegarde des messages)
- ✅ SELECT autorisé (lecture des messages)

## 📊 Cas d'usage

### Historique de conversation
```python
# Charger l'historique complet d'une session
history = storage.get_session_messages(thread_id)
for msg in history:
    print(f"{msg['role'].upper()}: {msg['content']}")
```

### Analyse de données
```python
# Récupérer tous les messages pour analyse
from supabase import create_client
supabase = create_client(url, key)

# Requête directe Supabase
response = supabase.table("messages").select("*").execute()
messages = response.data
```

### Nettoyage périodique
```python
# Supprimer les messages plus anciens que 60 jours
storage.clear_old_messages(days_old=60)
```

## 🚀 Fichiers modifiés

- `supabase_setup.sql` - Ajout de la table messages
- `message_storage.py` - Nouveau module de gestion des messages
- `main.py` - Intégration de la sauvegarde automatique

## 📝 Notes

- Chaque session a un `thread_id` unique affiché au démarrage
- Les messages sont sauvegardés **après** que l'assistant génère sa réponse
- Le système est conçu pour supporter le multi-utilisateur (via session_id)

## ⚠️ Troubleshooting

### Les messages ne se sauvegardent pas
1. Vérifiez que le SQL a été exécuté dans Supabase
2. Vérifiez vos variables d'environnement (.env)
3. Vérifiez les permissions RLS dans Supabase

### Erreur de connexion Supabase
Assurez-vous que `REACT_APP_SUPABASE_URL` et `REACT_APP__ANON_KEY` sont correctement définis dans `.env`
