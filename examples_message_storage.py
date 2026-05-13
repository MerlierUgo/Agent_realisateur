"""
Exemples d'utilisation avancée du MessageStorage
"""

from message_storage import MessageStorage
from supabase import create_client
import os

# Configuration
supabase = create_client(
    os.getenv("REACT_APP_SUPABASE_URL"),
    os.getenv("REACT_APP__ANON_KEY")
)

storage = MessageStorage(supabase)

# ============ EXEMPLE 1: Charger et afficher l'historique ============
def afficher_historique(session_id: str):
    """Affiche l'historique formaté d'une session."""
    messages = storage.get_session_messages(session_id)
    
    print(f"\n📖 Historique de la session {session_id}:")
    print("=" * 60)
    
    for msg in messages:
        role = "👤" if msg['role'] == 'user' else "🤖"
        print(f"\n{role} {msg['role'].upper()}")
        print(f"   {msg['content']}")
        print(f"   ⏰ {msg['created_at']}")
    
    print("\n" + "=" * 60)


# ============ EXEMPLE 2: Exporter une session en fichier ============
def exporter_session(session_id: str, filename: str = None):
    """Exporte une session complète en fichier texte."""
    if filename is None:
        filename = f"session_{session_id[:8]}.txt"
    
    messages = storage.get_session_messages(session_id)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Session ID: {session_id}\n")
        f.write(f"Messages: {len(messages)}\n")
        f.write("=" * 60 + "\n\n")
        
        for msg in messages:
            f.write(f"[{msg['role'].upper()}]\n")
            f.write(f"{msg['content']}\n")
            f.write(f"Time: {msg['created_at']}\n")
            f.write("-" * 40 + "\n\n")
    
    print(f"✅ Session exportée dans {filename}")


# ============ EXEMPLE 3: Statistiques de conversation ============
def stats_session(session_id: str):
    """Affiche des statistiques sur une session."""
    messages = storage.get_session_messages(session_id)
    
    user_count = sum(1 for m in messages if m['role'] == 'user')
    assistant_count = sum(1 for m in messages if m['role'] == 'assistant')
    
    total_user_chars = sum(len(m['content']) for m in messages if m['role'] == 'user')
    total_assistant_chars = sum(len(m['content']) for m in messages if m['role'] == 'assistant')
    
    print(f"\n📊 Statistiques de la session {session_id}")
    print(f"   Messages utilisateur: {user_count}")
    print(f"   Réponses assistant: {assistant_count}")
    print(f"   Caractères utilisateur: {total_user_chars}")
    print(f"   Caractères assistant: {total_assistant_chars}")
    
    if messages:
        first_msg = messages[0]['created_at']
        last_msg = messages[-1]['created_at']
        print(f"   Durée: {first_msg} → {last_msg}")


# ============ EXEMPLE 4: Chercher des messages ============
def chercher_messages(session_id: str, keyword: str):
    """Cherche des messages contenant un mot-clé."""
    messages = storage.get_session_messages(session_id)
    
    results = [m for m in messages if keyword.lower() in m['content'].lower()]
    
    print(f"\n🔍 {len(results)} message(s) contenant '{keyword}':")
    for msg in results:
        print(f"   [{msg['role']}] {msg['content'][:100]}...")


# ============ EXEMPLE 5: Sauvegarder plusieurs messages à la fois ============
def bulk_save_messages(session_id: str, conversation_history: list):
    """
    Sauvegarde plusieurs messages rapidement.
    
    Args:
        session_id: ID de la session
        conversation_history: Liste de tuples (role, content)
    """
    storage.save_batch_messages(session_id, conversation_history)


# ============ EXEMPLE 6: Importer depuis JSON ============
def importer_conversation_json(json_file: str, session_id: str):
    """Importe une conversation depuis un fichier JSON."""
    import json
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    messages = [(msg['role'], msg['content']) for msg in data.get('messages', [])]
    storage.save_batch_messages(session_id, messages)
    
    print(f"✅ {len(messages)} messages importés depuis {json_file}")


# ============ EXEMPLE 7: Archiver une session ============
def archiver_session(session_id: str, archive_filename: str = None):
    """Exporte et supprime une session."""
    if archive_filename is None:
        archive_filename = f"archive_{session_id[:8]}.txt"
    
    # Exporter
    exporter_session(session_id, archive_filename)
    
    # Supprimer
    storage.delete_session_messages(session_id)
    
    print(f"✅ Session archivée et supprimée de la base")


# ============ EXEMPLE 8: Nettoyer les anciennes sessions ============
def nettoyer_anciennes_sessions(days: int = 30):
    """Supprime les messages plus anciens que X jours."""
    storage.clear_old_messages(days_old=days)
    print(f"✅ Messages plus anciens que {days} jours supprimés")


# ============ EXEMPLE 9: Comparer deux sessions ============
def comparer_sessions(session_id_1: str, session_id_2: str):
    """Compare deux sessions."""
    msgs1 = storage.get_session_messages(session_id_1)
    msgs2 = storage.get_session_messages(session_id_2)
    
    print(f"\n📊 Comparaison")
    print(f"   Session 1: {len(msgs1)} messages")
    print(f"   Session 2: {len(msgs2)} messages")
    
    # Messages uniques (résumés)
    content1 = [m['content'][:50] for m in msgs1 if m['role'] == 'user']
    content2 = [m['content'][:50] for m in msgs2 if m['role'] == 'user']
    
    print(f"\n   Messages utilisateur uniques: {len(set(content1) & set(content2))} en commun")


# ============ EXEMPLE 10: Requête directe Supabase ============
def requete_personnalisee():
    """Exemple de requête directe Supabase pour cas particuliers."""
    # Récupérer les sessions avec le plus de messages
    response = supabase.table("messages").select(
        "session_id, COUNT(*) as count"
    ).execute()
    
    print("\n📊 Sessions les plus actives:")
    for item in response.data:
        print(f"   {item['session_id']}: {item['count']} messages")


# ============ EXÉCUTION DES EXEMPLES ============
if __name__ == "__main__":
    import uuid
    
    # Créer une session de test
    session_id = str(uuid.uuid4())
    print(f"Session de test: {session_id}\n")
    
    # Exemple 5: Sauvegarder plusieurs messages
    print("1️⃣  Sauvegarde en batch...")
    conversation = [
        ("user", "Qu'est-ce qu'un réalisateur?"),
        ("assistant", "Un réalisateur est une personne qui dirige un film."),
        ("user", "Comment débuter dans ce métier?"),
        ("assistant", "Il faut étudier le cinéma et pratiquer.")
    ]
    bulk_save_messages(session_id, conversation)
    
    # Exemple 1: Afficher l'historique
    print("\n2️⃣  Affichage de l'historique...")
    afficher_historique(session_id)
    
    # Exemple 3: Statistiques
    print("\n3️⃣  Statistiques...")
    stats_session(session_id)
    
    # Exemple 4: Chercher
    print("\n4️⃣  Recherche...")
    chercher_messages(session_id, "réalisateur")
    
    # Exemple 2: Exporter
    print("\n5️⃣  Export...")
    exporter_session(session_id)
    
    print("\n✅ Exemples terminés!")
