"""Modelo de Categoria"""
from db import get_connection, dict_cursor

class Category:
    """Classe que representa uma categoria de receita"""

    @staticmethod
    def get_all():
        """Retorna todas as categorias."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            cur.execute("SELECT * FROM categories ORDER BY nome")
            return cur.fetchall()
        except Exception as e:
            print("Erro em Category.get_all:", e)
            return []
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    @staticmethod
    def get_by_id(category_id):
        """Busca uma categoria pelo ID."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            cur.execute("SELECT * FROM categories WHERE id = %s", (category_id,))
            return cur.fetchone()
        except Exception as e:
            print("Erro em Category.get_by_id:", e)
            return None
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    @staticmethod
    def get_by_name(name):
        """Busca uma categoria pelo nome."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            cur.execute("SELECT * FROM categories WHERE nome = %s", (name,))
            return cur.fetchone()
        except Exception as e:
            print("Erro em Category.get_by_name:", e)
            return None
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    @staticmethod
    def create(nome, descricao=None):
        """Cria uma nova categoria."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            cur.execute(
                "INSERT INTO categories (nome, descricao) VALUES (%s, %s)",
                (nome, descricao)
            )
            conn.commit()
            return cur.lastrowid
        except Exception as e:
            print("Erro em Category.create:", e)
            return None
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()