"""Modelo de Log de Acesso"""
from db import get_connection, dict_cursor

class AccessLog:
    """Classe que gerencia os logs de acesso à aplicação"""

    @staticmethod
    def create(endpoint, metodo, ip_address, user_email=None):
        """Registra um novo log de acesso."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            cur.execute(
                """
                INSERT INTO access_logs (user_email, endpoint, metodo, ip_address)
                VALUES (%s, %s, %s, %s)
                """,
                (user_email, endpoint, metodo, ip_address)
            )
            conn.commit()
            return True
        except Exception as e:
            print("Erro em AccessLog.create:", e)
            return False
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    @staticmethod
    def get_latest(limit=10):
        """Retorna os logs de acesso mais recentes."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            cur.execute(
                """
                SELECT * FROM access_logs
                ORDER BY data_acesso DESC
                LIMIT %s
                """,
                (limit,)
            )
            return cur.fetchall()
        except Exception as e:
            print("Erro em AccessLog.get_latest:", e)
            return []
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()