import os
import psycopg2
from dotenv import load_dotenv

# Carrega a variável DATABASE_URL do arquivo .env
load_dotenv()


def init_table():
    """Cria a tabela 'filmes' no Neon caso não exista."""

    # Pega a URL de conexão do arquivo .env
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        print("Erro: Variável DATABASE_URL não encontrada no arquivo .env")
        return

    try:
        print("Conectando ao banco de dados no Neon...")
        # Conecta no banco usando a URL do Neon
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        # Criação da tabela
        sql = """
        CREATE TABLE IF NOT EXISTS filmes (
            id SERIAL PRIMARY KEY,
            titulo VARCHAR(255) NOT NULL,
            genero VARCHAR(100),
            ano DATE,
            url_capa TEXT
        );
        """
        cursor.execute(sql)
        conn.commit()
        print("Tabela 'filmes' criada com sucesso no banco de dados!")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao inicializar tabela: {e}")


if __name__ == "__main__":
    print("Iniciando migração na nuvem...")
    init_table()
    print("Migração finalizada.")