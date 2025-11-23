import mysql.connector
from mysql.connector import Error
from config import Config

def get_connection():
    """Abre e retorna uma conexão com o MySQL."""
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='20162540',
        database='recipe_app',
        port='3306'
    )

def dict_cursor(conn):
    """Retorna um cursor que devolve dict em vez de tupla."""
    return conn.cursor(dictionary=True)