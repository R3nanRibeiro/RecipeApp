"""Modelo para tokens de recuperação de senha - usando MySQL"""
import secrets
from datetime import datetime, timedelta
from db import get_connection, dict_cursor

class PasswordReset:
    """Classe para gerenciar tokens de recuperação de senha"""
    
    TOKEN_EXPIRY_HOURS = 24  # Token expira em 24 horas
    
    @staticmethod
    def generate_token():
        """Gera um token único e seguro"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def create_token(email):
        """Cria um novo token de recuperação para um email"""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            
            # Remove tokens antigos do mesmo email
            cur.execute("""
                DELETE FROM password_resets 
                WHERE user_email = %s OR data_expiracao < NOW()
            """, (email,))
            
            # Gera novo token
            token = PasswordReset.generate_token()
            expiry = datetime.now() + timedelta(hours=PasswordReset.TOKEN_EXPIRY_HOURS)
            
            # Insere novo token
            cur.execute("""
                INSERT INTO password_resets (user_email, token, data_expiracao)
                VALUES (%s, %s, %s)
            """, (email, token, expiry))
            
            conn.commit()
            return token
        except Exception as e:
            print("Erro em PasswordReset.create_token:", e)
            return None
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()
    
    @staticmethod
    def get_token_info(token):
        """Obtém informações de um token"""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            cur.execute("""
                SELECT * FROM password_resets 
                WHERE token = %s
            """, (token,))
            return cur.fetchone()
        except Exception as e:
            print("Erro em PasswordReset.get_token_info:", e)
            return None
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()
    
    @staticmethod
    def is_token_valid(token):
        """Verifica se um token é válido e não expirou"""
        token_info = PasswordReset.get_token_info(token)
        
        if not token_info:
            return False
        
        # Verifica se foi usado
        if token_info.get('usado'):
            return False
        
        # Verifica expiração
        data_expiracao = token_info['data_expiracao']
        # Se for datetime do MySQL, comparar diretamente
        if isinstance(data_expiracao, datetime):
            if datetime.now() > data_expiracao:
                PasswordReset.delete_token(token)
                return False
        else:
            # Se for string, converter
            try:
                if isinstance(data_expiracao, str):
                    data_expiracao = datetime.fromisoformat(data_expiracao.replace('Z', '+00:00'))
                if datetime.now() > data_expiracao:
                    PasswordReset.delete_token(token)
                    return False
            except:
                return False
        
        return True
    
    @staticmethod
    def get_email_from_token(token):
        """Obtém o email associado a um token válido"""
        if not PasswordReset.is_token_valid(token):
            return None
        
        token_info = PasswordReset.get_token_info(token)
        return token_info.get('user_email') if token_info else None
    
    @staticmethod
    def delete_token(token):
        """Remove um token"""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            cur.execute("DELETE FROM password_resets WHERE token = %s", (token,))
            conn.commit()
        except Exception as e:
            print("Erro em PasswordReset.delete_token:", e)
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()
    
    @staticmethod
    def mark_token_as_used(token):
        """Marca um token como usado"""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            cur.execute("""
                UPDATE password_resets 
                SET usado = 1 
                WHERE token = %s
            """, (token,))
            conn.commit()
        except Exception as e:
            print("Erro em PasswordReset.mark_token_as_used:", e)
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()
    
    @staticmethod
    def cleanup_expired_tokens():
        """Remove tokens expirados usando procedimento armazenado"""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            # Usa procedimento armazenado (atende requisito)
            cur.callproc('sp_limpar_tokens_expirados')
            conn.commit()
        except Exception as e:
            print("Erro ao limpar tokens:", e)
            # Fallback para DELETE direto
            try:
                cur.execute("""
                    DELETE FROM password_resets 
                    WHERE data_expiracao < NOW() OR usado = 1
                """)
                conn.commit()
            except:
                pass
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()
