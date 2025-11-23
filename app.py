"""Aplicação Flask - RecipeApp"""
from flask import Flask
from datetime import timedelta
from config import Config
from controllers.auth_controller import AuthController
from controllers.recipe_controller import RecipeController
from controllers.profile_controller import ProfileController
from controllers.rating_controller import RatingController
from controllers.comment_controller import CommentController
from controllers.favorite_controller import FavoriteController
import os

# Inicializar aplicação Flask
app = Flask(__name__, template_folder='views/templates')  # Templates em views/templates/
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)  # Sessão permanente por 30 dias

# Garantir que a pasta de uploads existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# === Rotas de Autenticação ===
@app.route('/')
def index():
    """Página inicial"""
    return RecipeController.index()

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    """Cadastro de novos usuários"""
    return AuthController.cadastro()

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login de usuários"""
    return AuthController.login()

@app.route('/logout')
def logout():
    """Logout do usuário"""
    return AuthController.logout()

@app.route('/esqueci_senha', methods=['GET', 'POST'])
def esqueci_senha():
    """Recuperação de senha"""
    return AuthController.esqueci_senha()

@app.route('/redefinir_senha', methods=['GET', 'POST'])
@app.route('/redefinir_senha/<token>', methods=['GET', 'POST'])
def redefinir_senha(token=None):
    """Redefinição de senha"""
    return AuthController.redefinir_senha(token)

# === Rotas de Receitas ===
@app.route('/receitas')
def receitas():
    """Lista todas as receitas"""
    return RecipeController.listar()

@app.route('/visualizar_receita/<int:receita_id>')
def visualizar_receita(receita_id):
    """Visualiza uma receita específica"""
    return RecipeController.visualizar(receita_id)

@app.route('/adicionar_receita', methods=['GET', 'POST'])
def adicionar_receita():
    """Adiciona uma nova receita"""
    return RecipeController.adicionar()

@app.route('/editar_receita/<int:receita_id>', methods=['GET', 'POST'])
def editar_receita(receita_id):
    """Edita uma receita existente"""
    return RecipeController.editar(receita_id)

@app.route('/excluir_receita/<int:receita_id>', methods=['POST'])
def excluir_receita(receita_id):
    """Exclui uma receita"""
    return RecipeController.excluir(receita_id)

@app.route('/download_receita/<int:receita_id>')
def download_receita(receita_id):
    """Gera PDF da receita para download"""
    return RecipeController.download(receita_id)

# === Rotas de Perfil ===
@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    """Edição do perfil do usuário"""
    return ProfileController.perfil()

@app.route('/excluir_conta', methods=['POST'])
def excluir_conta():
    """Exclui a conta do usuário"""
    return ProfileController.excluir_conta()

# === Rotas de Avaliações ===
@app.route('/avaliar_receita/<int:recipe_id>', methods=['POST'])
def avaliar_receita(recipe_id):
    """Avalia uma receita"""
    return RatingController.avaliar(recipe_id)

@app.route('/remover_avaliacao/<int:recipe_id>', methods=['POST'])
def remover_avaliacao(recipe_id):
    """Remove a avaliação de uma receita"""
    return RatingController.remover_avaliacao(recipe_id)

@app.route('/api/avaliar/<int:recipe_id>', methods=['POST'])
def api_avaliar_receita(recipe_id):
    """API para avaliar receita (AJAX)"""
    return RatingController.api_avaliar(recipe_id)

# === Rotas de Comentários ===
@app.route('/comentar/<int:recipe_id>', methods=['POST'])
def comentar(recipe_id):
    """Adiciona um comentário a uma receita"""
    return CommentController.adicionar(recipe_id)

@app.route('/excluir_comentario/<int:comment_id>', methods=['POST'])
def excluir_comentario(comment_id):
    """Exclui um comentário"""
    return CommentController.excluir(comment_id)

# === Rotas de Favoritos ===
@app.route('/favoritar/<int:recipe_id>', methods=['POST'])
def favoritar(recipe_id):
    """Adiciona ou remove uma receita dos favoritos"""
    return FavoriteController.toggle(recipe_id)

@app.route('/api/favoritar/<int:recipe_id>', methods=['POST'])
def api_favoritar(recipe_id):
    """API para favoritar/desfavoritar (AJAX)"""
    return FavoriteController.api_toggle(recipe_id)

@app.route('/favoritos')
def favoritos():
    """Lista as receitas favoritas do usuário"""
    return FavoriteController.listar()

if __name__ == '__main__':
    app.run(debug=True)
