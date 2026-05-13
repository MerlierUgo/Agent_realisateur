"""
Module de sauvegarde et récupération des messages dans Supabase.
"""

from typing import List, Tuple
from supabase import Client
from datetime import datetime


class MessageStorage:
    """Gère la persistence des messages dans Supabase."""
    
    def __init__(self, supabase_client: Client):
        """
        Initialise le gestionnaire de messages.
        
        Args:
            supabase_client: Client Supabase initialisé
        """
        self.client = supabase_client
        self.table_name = "messages"
    
    def save_message(self, session_id: str, role: str, content: str) -> bool:
        """
        Sauvegarde un message dans Supabase.
        
        Args:
            session_id: ID unique de la session/conversation
            role: Rôle du message ('user' ou 'assistant')
            content: Contenu du message
            
        Returns:
            True si la sauvegarde a réussi, False sinon
        """
        try:
            response = self.client.table(self.table_name).insert({
                "session_id": session_id,
                "role": role,
                "content": content,
                "created_at": datetime.now().isoformat()
            }).execute()
            
            print(f"✅ Message sauvegardé (role: {role})")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde du message: {e}")
            return False
    
    def save_batch_messages(self, session_id: str, messages: List[Tuple[str, str]]) -> bool:
        """
        Sauvegarde un lot de messages en une seule requête.
        
        Args:
            session_id: ID unique de la session/conversation
            messages: Liste de tuples (role, content)
            
        Returns:
            True si la sauvegarde a réussi, False sinon
        """
        try:
            batch_data = [
                {
                    "session_id": session_id,
                    "role": role,
                    "content": content,
                    "created_at": datetime.now().isoformat()
                }
                for role, content in messages
            ]
            
            response = self.client.table(self.table_name).insert(batch_data).execute()
            print(f"✅ {len(batch_data)} message(s) sauvegardé(s) en batch")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde en batch: {e}")
            return False
    
    def get_session_messages(self, session_id: str, limit: int = 50) -> List[dict]:
        """
        Récupère tous les messages d'une session.
        
        Args:
            session_id: ID unique de la session/conversation
            limit: Nombre maximum de messages à récupérer
            
        Returns:
            Liste des messages triés par date de création
        """
        try:
            response = self.client.table(self.table_name).select(
                "id, role, content, created_at"
            ).eq("session_id", session_id).order(
                "created_at", desc=False
            ).limit(limit).execute()
            
            messages = response.data
            print(f"📖 {len(messages)} message(s) récupéré(s) pour la session {session_id}")
            return messages
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des messages: {e}")
            return []
    
    def get_latest_messages(self, session_id: str, limit: int = 10) -> List[dict]:
        """
        Récupère les messages récents d'une session.
        
        Args:
            session_id: ID unique de la session/conversation
            limit: Nombre de messages récents à récupérer
            
        Returns:
            Liste des messages triés du plus récent au plus ancien
        """
        try:
            response = self.client.table(self.table_name).select(
                "id, role, content, created_at"
            ).eq("session_id", session_id).order(
                "created_at", desc=True
            ).limit(limit).execute()
            
            # Inverser pour avoir l'ordre chronologique
            messages = list(reversed(response.data))
            return messages
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des messages récents: {e}")
            return []
    
    def delete_session_messages(self, session_id: str) -> bool:
        """
        Supprime tous les messages d'une session.
        
        Args:
            session_id: ID unique de la session/conversation
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        try:
            response = self.client.table(self.table_name).delete().eq(
                "session_id", session_id
            ).execute()
            
            print(f"🗑️  Session {session_id} supprimée")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la suppression de la session: {e}")
            return False
    
    def clear_old_messages(self, days_old: int = 30) -> bool:
        """
        Supprime les messages plus anciens que X jours.
        
        Args:
            days_old: Nombre de jours au-delà duquel supprimer les messages
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        try:
            from datetime import timedelta
            cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()
            
            response = self.client.table(self.table_name).delete().lt(
                "created_at", cutoff_date
            ).execute()
            
            print(f"🗑️  Messages antérieurs au {cutoff_date} supprimés")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du nettoyage des anciens messages: {e}")
            return False
