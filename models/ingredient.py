"""Modelo de Ingrediente"""
from db import get_connection, dict_cursor

class Ingredient:
    """Classe que representa um ingrediente"""

    @staticmethod
    def get_all():
        """Retorna todos os ingredientes."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            cur.execute("SELECT * FROM ingredients ORDER BY nome")
            return cur.fetchall()
        except Exception as e:
            print("Erro em Ingredient.get_all:", e)
            return []
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    @staticmethod
    def get_by_id(ingredient_id):
        """Busca um ingrediente pelo ID."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            cur.execute("SELECT * FROM ingredients WHERE id = %s", (ingredient_id,))
            return cur.fetchone()
        except Exception as e:
            print("Erro em Ingredient.get_by_id:", e)
            return None
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    @staticmethod
    def create(nome, unidade_medida):
        """Cria um novo ingrediente."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            cur.execute(
                "INSERT INTO ingredients (nome, unidade_medida) VALUES (%s, %s)",
                (nome, unidade_medida)
            )
            conn.commit()
            return cur.lastrowid
        except Exception as e:
            print("Erro em Ingredient.create:", e)
            return None
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()