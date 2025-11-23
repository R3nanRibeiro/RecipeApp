"""Modelo de Comentário"""
from db import get_connection, dict_cursor

class Comment:
    """Classe que representa um comentário em uma receita"""

    @staticmethod
    def get_by_recipe(recipe_id):
        """Retorna todos os comentários ativos de uma receita."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            cur.execute(
                """
                SELECT c.*, u.nome as user_name
                FROM comments c
                JOIN users u ON c.user_email = u.email
                WHERE c.recipe_id = %s AND c.ativo = 1
                ORDER BY c.data_comentario DESC
                """,
                (recipe_id,)
            )
            return cur.fetchall()
        except Exception as e:
            print("Erro em Comment.get_by_recipe:", e)
            return []
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    @staticmethod
    def create(recipe_id, user_email, conteudo):
        """Cria um novo comentário."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            cur.execute(
                "INSERT INTO comments (recipe_id, user_email, conteudo) VALUES (%s, %s, %s)",
                (recipe_id, user_email, conteudo)
            )
            conn.commit()
            return cur.lastrowid
        except Exception as e:
            print("Erro em Comment.create:", e)
            return None
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()