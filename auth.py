

from flask import logging, session
from models import Users


def configure_auth(app, login_manager):
    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))

def fetch_user_stores(user):
    if user.is_authenticated:
        try:
            user_stores = user.stores.all()
            selected_store_id = session.get('selected_store', None)
            selected_store = next((store for store in user_stores if store.id == selected_store_id), None)
            return user_stores, selected_store
        except Exception as e:
            logging.error(f"Error in fetch_user_stores for user {user.id}: {e}")
            return [], None
    return [], None

def get_selected_store_for_user(user):
    if user.is_authenticated:
        _, selected_store = fetch_user_stores(user)
        return selected_store
    return None

def get_user_stores(user):
    if user and user.is_authenticated:
        try:
            stores = user.stores.all() or []
            print("Debug: Stores fetched for user", user.id, ":", stores)
            return stores
        except Exception as e:
            print("Error fetching stores for user", user.id, ":", e)
            return []
    return []
