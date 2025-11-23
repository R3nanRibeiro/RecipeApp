# recife/setup_db.py
import mysql.connector
from mysql.connector import Error
from config import Config

def create_database_and_tables():
    """Cria o banco de dados e as tabelas usando o script SQL."""
    try:
        # 1. Conectar ao servidor MySQL (sem especificar o banco de dados)
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        cursor = conn.cursor()

        # 2. Criar o banco de dados se não existir
        print(f"Verificando/Criando banco de dados: {Config.DB_NAME}")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.database = Config.DB_NAME # Mudar para o banco de dados recém-criado/existente

        # 3. Executar o script SQL para criar as tabelas
        print("Executando script SQL para criar tabelas e inserir dados iniciais...")
        with open('recife/create_db.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # O script contém múltiplos comandos, então precisamos executá-los um por um
        # O conector MySQL para Python tem um método `split_statements` para isso
        for result in cursor.execute(sql_script, multi=True):
            # Apenas iterar sobre os resultados para garantir que todos os comandos sejam executados
            # DDL/DML não retornam linhas, então não precisamos de fetchall()
            pass
        
        conn.commit()
        print("Banco de dados e tabelas criados/atualizados com sucesso!")

    except Error as e:
        print(f"Erro ao configurar o banco de dados: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    create_database_and_tables()