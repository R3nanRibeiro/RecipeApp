"""Modelo de Favorito"""
from db import get_connection, dict_cursor

class Favorite:
    """Classe que gerencia as receitas favoritas dos usuários"""

    @staticmethod
    def is_favorite(recipe_id, user_email):
        """Verifica se uma receita está nos favoritos do usuário."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            cur.execute(
                "SELECT 1 FROM favorites WHERE recipe_id = %s AND user_email = %s",
                (recipe_id, user_email)
            )
            return cur.fetchone() is not None
        except Exception as e:
            print("Erro em Favorite.is_favorite:", e)
            return False
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    @staticmethod
    def add_favorite(recipe_id, user_email):
        """Adiciona uma receita aos favoritos."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            cur.execute(
                "INSERT IGNORE INTO favorites (recipe_id, user_email) VALUES (%s, %s)",
                (recipe_id, user_email)
            )
            conn.commit()
            return True
        except Exception as e:
            print("Erro em Favorite.add_favorite:", e)
            return False
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    @staticmethod
    def remove_favorite(recipe_id, user_email):
        """Remove uma receita dos favoritos."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            cur.execute(
                "DELETE FROM favorites WHERE recipe_id = %s AND user_email = %s",
                (recipe_id, user_email)
            )
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            print("Erro em Favorite.remove_favorite:", e)
            return False
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    @staticmethod
    def get_user_favorites(user_email):
        """Retorna todas as receitas favoritas de um usuário."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            cur.execute(
                """
                SELECT r.*
                FROM recipes r
                JOIN favorites f ON r.id = f.recipe_id
                WHERE f.user_email = %s
                ORDER BY r.data_criacao DESC
                """,
                (user_email,)
            )
            # Retorna as receitas como dicionários, mas sem a conversão de ingredientes/modo_preparo
            # A conversão deve ser feita no controller/view se necessário
            return cur.fetchall()
        except Exception as e:
            print("Erro em Favorite.get_user_favorites:", e)
            return []
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()