"""Modelo de Usuário - agora usando MySQL"""
from utils import hash_password
from db import get_connection, dict_cursor

class User:
    """Classe que representa um usuário"""

    @staticmethod
    def create(email, nome, senha, lembrar=False):
        """
        Cria um novo usuário no banco.
        Retorna (user_dict, erro) – mesmo contrato que antes.
        """
        try:
            conn = get_connection()
            cur = dict_cursor(conn)

            # Verifica se já existe
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            existing = cur.fetchone()
            if existing:
                return None, 'Este e-mail já está cadastrado!'

            hashed = hash_password(senha)
            cur.execute(
                """
                INSERT INTO users (email, nome, senha, lembrar)
                VALUES (%s, %s, %s, %s)
                """,
                (email, nome, hashed, int(bool(lembrar)))
            )
            
            # Faz commit do usuário primeiro para evitar deadlock
            conn.commit()
            
            # Cria perfil básico para o usuário (após commit para evitar deadlock)
            # Usa mesma conexão se ainda válida, senão cria nova conexão
            try:
                if conn.is_connected():
                    # Verifica se já existe perfil (não deveria, mas por segurança)
                    cur.execute("SELECT 1 FROM user_profiles WHERE user_email = %s", (email,))
                    if not cur.fetchone():
                        cur.execute(
                            """
                            INSERT INTO user_profiles 
                            (user_email, bio, foto_perfil, telefone, data_nascimento, cidade, estado, pais)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (email, None, None, None, None, None, None, 'Brasil')
                        )
                        conn.commit()
                else:
                    # Se conexão foi fechada, cria nova conexão apenas para o perfil
                    from models.user_profile import UserProfile
                    UserProfile.create(email)
            except Exception as e:
                print(f"Erro ao criar perfil: {e}")
                # Se falhar ao criar perfil, não é crítico, pode ser criado depois
                # Tenta criar usando método separado como fallback
                try:
                    from models.user_profile import UserProfile
                    UserProfile.create(email)
                except:
                    pass

            user = {
                'nome': nome,
                'senha': hashed,
                'lembrar': bool(lembrar)
            }
            return user, None

        except Exception as e:
            print("Erro em User.create:", e)
            if 'conn' in locals():
                try:
                    if conn.is_connected():
                        conn.rollback()
                except:
                    pass
            error_msg = str(e)
            # Mensagens de erro mais amigáveis
            if 'Duplicate entry' in error_msg or '1062' in error_msg:
                return None, 'Este e-mail já está cadastrado!'
            elif 'Connection' in error_msg or '2003' in error_msg:
                return None, 'Erro ao conectar com o banco de dados. Verifique se o MySQL está rodando.'
            return None, f'Erro ao criar usuário: {error_msg}'
        finally:
            if 'cur' in locals():
                try:
                    cur.close()
                except:
                    pass
            if 'conn' in locals():
                try:
                    if conn.is_connected():
                        conn.close()
                except:
                    pass

    @staticmethod
    def get_by_email(email):
        """
        Busca um usuário pelo email (case-insensitive).
        Retorna um dict com as chaves 'nome', 'senha', 'lembrar'
        igual era no JSON.
        """
        try:
            conn = get_connection()
            cur = dict_cursor(conn)

            # Primeiro tenta email exato
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            row = cur.fetchone()

            # Se não achar, tenta case-insensitive
            if not row:
                cur.execute(
                    "SELECT * FROM users WHERE LOWER(email) = LOWER(%s)",
                    (email,)
                )
                row = cur.fetchone()

            if not row:
                return None

            return {
                'nome': row['nome'],
                'senha': row['senha'],
                'lembrar': bool(row['lembrar']),
                'ativo': bool(row.get('ativo', 1)),
                'email': row['email']
            }

        except Exception as e:
            print("Erro em User.get_by_email:", e)
            return None
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()
    
    @staticmethod
    def update_last_access(email):
        """Atualiza o último acesso do usuário."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            cur.execute(
                "UPDATE users SET ultimo_acesso = CURRENT_TIMESTAMP WHERE email = %s",
                (email,)
            )
            conn.commit()
            return True
        except Exception as e:
            print("Erro em User.update_last_access:", e)
            return False
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    @staticmethod
    def update(email, nome=None, senha=None):
        """
        Atualiza dados do usuário (nome e/ou senha).
        Retorna (True, None) em caso de sucesso ou (False, msg_erro).
        """
        try:
            conn = get_connection()
            cur = dict_cursor(conn)

            # Carrega usuário atual
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            row = cur.fetchone()
            if not row:
                return False, 'Usuário não encontrado!'

            novo_nome = nome if nome else row['nome']
            nova_senha = row['senha']
            if senha:
                nova_senha = hash_password(senha)

            cur.execute(
                """
                UPDATE users
                SET nome = %s, senha = %s
                WHERE email = %s
                """,
                (novo_nome, nova_senha, email)
            )
            conn.commit()
            return True, None

        except Exception as e:
            print("Erro em User.update:", e)
            return False, 'Erro ao atualizar usuário!'
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    @staticmethod
    def update_lembrar(email, lembrar):
        """
        Atualiza a preferência de lembrar senha do usuário.
        Retorna True em caso de sucesso, False caso contrário.
        """
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            cur.execute(
                "UPDATE users SET lembrar = %s WHERE email = %s",
                (int(bool(lembrar)), email)
            )
            conn.commit()
            return True
        except Exception as e:
            print("Erro em User.update_lembrar:", e)
            return False
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    @staticmethod
    def delete(email):
        """
        Exclui um usuário pelo email.
        Retorna True se encontrou e excluiu, False caso contrário.
        """
        try:
            conn = get_connection()
            cur = dict_cursor(conn)

            cur.execute("DELETE FROM users WHERE email = %s", (email,))
            conn.commit()
            return cur.rowcount > 0

        except Exception as e:
            print("Erro em User.delete:", e)
            return False
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()
