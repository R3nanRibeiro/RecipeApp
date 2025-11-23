"""Configurações da aplicação"""
import os

class Config:
    """Configurações gerais da aplicação"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua_chave_secreta_aqui'
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # >>> AGORA NÃO VAMOS MAIS USAR JSON PARA USERS/RECIPES <<<
    # (esses caminhos só ficam aqui se você ainda quiser manter compatibilidade)
    USERS_FILE = 'users.json'
    RECIPES_FILE = 'recipes.json'
    
    # Configurações de Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or ''
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or ''
    MAIL_FROM = os.environ.get('MAIL_FROM') or MAIL_USERNAME

    # === Configurações do MySQL ===
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '20162540')
    DB_NAME = os.environ.get('DB_NAME', 'recipe_app')
