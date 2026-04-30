import os
import psycopg2
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()


def get_connection():
    # Pega a URL inteira do Neon que configuramos no .env (e depois no Render)
    db_url = os.getenv("DATABASE_URL")

    # Conecta usando apenas a URL
    conn = psycopg2.connect(db_url)

    return conn