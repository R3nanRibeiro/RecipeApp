"""Modelo de Perfil de Usuário"""
from db import get_connection, dict_cursor

class UserProfile:
    """Classe que representa o perfil de um usuário"""

    @staticmethod
    def get_by_email(email):
        """Busca o perfil de um usuário pelo email."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            cur.execute("SELECT * FROM user_profiles WHERE user_email = %s", (email,))
            return cur.fetchone()
        except Exception as e:
            print("Erro em UserProfile.get_by_email:", e)
            return None
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    @staticmethod
    def create(email, bio=None, foto_perfil=None, telefone=None, 
               data_nascimento=None, cidade=None, estado=None, pais='Brasil'):
        """Cria um novo perfil de usuário (ou retorna True se já existir)."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            # Verifica se já existe
            cur.execute("SELECT 1 FROM user_profiles WHERE user_email = %s", (email,))
            if cur.fetchone():
                return True  # Já existe, não precisa criar
            cur.execute(
                """
                INSERT INTO user_profiles 
                (user_email, bio, foto_perfil, telefone, data_nascimento, cidade, estado, pais)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (email, bio, foto_perfil, telefone, data_nascimento, cidade, estado, pais)
            )
            conn.commit()
            return True
        except Exception as e:
            print("Erro em UserProfile.create:", e)
            return False
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    @staticmethod
    def update(email, bio=None, foto_perfil=None, telefone=None,
               data_nascimento=None, cidade=None, estado=None, pais=None):
        """Atualiza o perfil de um usuário."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            
            # Carrega perfil atual
            profile = UserProfile.get_by_email(email)
            
            if not profile:
                # Se não existe, cria um novo
                return UserProfile.create(email, bio, foto_perfil, telefone, 
                                        data_nascimento, cidade, estado, pais or 'Brasil')
            
            # Atualiza apenas campos fornecidos
            novo_bio = bio if bio is not None else profile.get('bio')
            novo_foto = foto_perfil if foto_perfil is not None else profile.get('foto_perfil')
            novo_telefone = telefone if telefone is not None else profile.get('telefone')
            nova_data = data_nascimento if data_nascimento is not None else profile.get('data_nascimento')
            nova_cidade = cidade if cidade is not None else profile.get('cidade')
            novo_estado = estado if estado is not None else profile.get('estado')
            novo_pais = pais if pais is not None else profile.get('pais')
            
            cur.execute(
                """
                UPDATE user_profiles
                SET bio = %s, foto_perfil = %s, telefone = %s,
                    data_nascimento = %s, cidade = %s, estado = %s, pais = %s
                WHERE user_email = %s
                """,
                (novo_bio, novo_foto, novo_telefone, nova_data, nova_cidade, novo_estado, novo_pais, email)
            )
            conn.commit()
            return True
        except Exception as e:
            print("Erro em UserProfile.update:", e)
            return False
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    @staticmethod
    def delete(email):
        """Exclui o perfil de um usuário (geralmente usado via CASCADE)."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            cur.execute("DELETE FROM user_profiles WHERE user_email = %s", (email,))
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            print("Erro em UserProfile.delete:", e)
            return False
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

