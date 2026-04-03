"""
Connexion et gestion Supabase
Client unique pour toutes les opérations de base de données
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Charge les variables du fichier .env
load_dotenv()

# Récupère les clés sans les afficher dans le code
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)
