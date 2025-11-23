"""Modelo de Avaliação de Receita"""
from db import get_connection, dict_cursor
from datetime import datetime

class RecipeRating:
    """Classe que gerencia as avaliações de receitas"""

    @staticmethod
    def get_by_recipe(recipe_id):
        """Retorna todas as avaliações de uma receita com informações do usuário."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            cur.execute(
                """
                SELECT rr.*, u.nome as user_name
                FROM recipe_ratings rr
                JOIN users u ON rr.user_email = u.email
                WHERE rr.recipe_id = %s
                ORDER BY rr.data_avaliacao DESC
                """,
                (recipe_id,)
            )
            return cur.fetchall()
        except Exception as e:
            print("Erro em RecipeRating.get_by_recipe:", e)
            return []
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    @staticmethod
    def get_user_rating(recipe_id, user_email):
        """Retorna a avaliação de um usuário específico para uma receita."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            cur.execute(
                "SELECT * FROM recipe_ratings WHERE recipe_id = %s AND user_email = %s",
                (recipe_id, user_email)
            )
            return cur.fetchone()
        except Exception as e:
            print("Erro em RecipeRating.get_user_rating:", e)
            return None
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    @staticmethod
    def create_or_update(recipe_id, user_email, nota, comentario=None):
        """
        Cria uma nova avaliação ou atualiza se já existir.
        Retorna (True, None) em caso de sucesso ou (False, mensagem_erro).
        """
        try:
            if not (1 <= nota <= 5):
                return False, 'A nota deve estar entre 1 e 5!'
            
            conn = get_connection()
            cur = dict_cursor(conn)
            
            # Verifica se já existe avaliação
            existing = RecipeRating.get_user_rating(recipe_id, user_email)
            
            if existing:
                # Atualiza avaliação existente
                cur.execute(
                    """
                    UPDATE recipe_ratings
                    SET nota = %s, comentario = %s, data_avaliacao = CURRENT_TIMESTAMP
                    WHERE recipe_id = %s AND user_email = %s
                    """,
                    (nota, comentario, recipe_id, user_email)
                )
            else:
                # Cria nova avaliação
                cur.execute(
                    """
                    INSERT INTO recipe_ratings (recipe_id, user_email, nota, comentario)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (recipe_id, user_email, nota, comentario)
                )
            
            conn.commit()
            return True, None
        except Exception as e:
            print("Erro em RecipeRating.create_or_update:", e)
            if 'conn' in locals() and conn.is_connected():
                conn.rollback()
            return False, f'Erro ao salvar avaliação: {str(e)}'
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    @staticmethod
    def delete(recipe_id, user_email):
        """Remove a avaliação de um usuário para uma receita."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            cur.execute(
                "DELETE FROM recipe_ratings WHERE recipe_id = %s AND user_email = %s",
                (recipe_id, user_email)
            )
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            print("Erro em RecipeRating.delete:", e)
            return False
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    @staticmethod
    def get_stats(recipe_id):
        """Retorna estatísticas de avaliações de uma receita."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            cur.execute(
                """
                SELECT 
                    COALESCE(AVG(nota), 0) as media,
                    COUNT(*) as total,
                    SUM(CASE WHEN nota = 5 THEN 1 ELSE 0 END) as cinco_estrelas,
                    SUM(CASE WHEN nota = 4 THEN 1 ELSE 0 END) as quatro_estrelas,
                    SUM(CASE WHEN nota = 3 THEN 1 ELSE 0 END) as tres_estrelas,
                    SUM(CASE WHEN nota = 2 THEN 1 ELSE 0 END) as duas_estrelas,
                    SUM(CASE WHEN nota = 1 THEN 1 ELSE 0 END) as uma_estrela
                FROM recipe_ratings
                WHERE recipe_id = %s
                """,
                (recipe_id,)
            )
            result = cur.fetchone()
            return {
                'media': float(result['media']) if result and result['media'] else 0.0,
                'total': int(result['total']) if result and result['total'] else 0,
                'cinco_estrelas': int(result['cinco_estrelas']) if result and result['cinco_estrelas'] else 0,
                'quatro_estrelas': int(result['quatro_estrelas']) if result and result['quatro_estrelas'] else 0,
                'tres_estrelas': int(result['tres_estrelas']) if result and result['tres_estrelas'] else 0,
                'duas_estrelas': int(result['duas_estrelas']) if result and result['duas_estrelas'] else 0,
                'uma_estrela': int(result['uma_estrela']) if result and result['uma_estrela'] else 0
            }
        except Exception as e:
            print("Erro em RecipeRating.get_stats:", e)
            return {
                'media': 0.0,
                'total': 0,
                'cinco_estrelas': 0,
                'quatro_estrelas': 0,
                'tres_estrelas': 0,
                'duas_estrelas': 0,
                'uma_estrela': 0
            }
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

