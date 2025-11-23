"""Controlador de autenticação"""
from flask import request, session, render_template, redirect, url_for, flash
from models.user import User
from models.password_reset import PasswordReset
from utils import check_password

# Importa o módulo de email
try:
    from email_sender import send_password_reset_email
except ImportError as e:
    # Fallback se não conseguir importar
    print(f"Erro ao importar email_sender: {e}")
    def send_password_reset_email(*args, **kwargs):
        print("⚠️ Email não configurado. Configure MAIL_USERNAME e MAIL_PASSWORD nas variáveis de ambiente.")
        return False

class AuthController:
    """Controlador para operações de autenticação"""
    
    @staticmethod
    def login():
        """Processa o login do usuário"""
        if request.method == 'POST':
            email = request.form['email'].strip()
            senha = request.form['senha']
            lembrar = 'lembrar' in request.form
            
            user = User.get_by_email(email)
            
            if user and check_password(senha, user['senha']):
                # Verificar se usuário está ativo
                if not user.get('ativo', True):
                    flash('Sua conta está desativada. Entre em contato com o suporte.', 'error')
                    return render_template('login.html')
                
                session['user_email'] = email
                session['user_name'] = user['nome']
                
                # Atualizar último acesso
                User.update_last_access(email)
                
                if lembrar:
                    session.permanent = True
                
                flash(f'Bem-vindo(a), {user["nome"]}!', 'success')
                return redirect(url_for('index'))
            else:
                flash('E-mail ou senha incorretos!', 'error')
        
        return render_template('login.html')
    
    @staticmethod
    def cadastro():
        """Processa o cadastro de novos usuários"""
        if request.method == 'POST':
            nome = request.form['nome'].strip()
            email = request.form['email'].strip()
            senha = request.form['senha']
            lembrar = 'lembrar' in request.form
            
            # Validações
            if not nome or not email or not senha:
                flash('Todos os campos são obrigatórios!', 'error')
                return render_template('cadastro.html')
            
            user, error = User.create(email, nome, senha, lembrar)
            
            if error:
                flash(error, 'error')
                return render_template('cadastro.html')
            
            flash('Conta criada com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('login'))
        
        return render_template('cadastro.html')
    
    @staticmethod
    def logout():
        """Processa o logout do usuário"""
        session.clear()
        flash('Você saiu da sua conta.', 'info')
        return redirect(url_for('index'))
    
    @staticmethod
    def esqueci_senha():
        """Processa a recuperação de senha"""
        if request.method == 'POST':
            email = request.form['email'].strip().lower()
            
            if not email:
                flash('Por favor, informe seu e-mail!', 'error')
                return render_template('esqueci_senha.html')
            
            user = User.get_by_email(email)
            
            # Por segurança, sempre mostramos a mesma mensagem, independente se o email existe
            # Se o email existir, geramos o token e enviamos o email
            if user:
                # Limpa tokens expirados
                PasswordReset.cleanup_expired_tokens()
                
                # Gera token de recuperação
                token = PasswordReset.create_token(email)
                
                # Cria a URL de redefinição
                reset_url = request.url_root.rstrip('/') + url_for('redefinir_senha', token=token)
                
                # Envia email com o link de recuperação
                email_sent = send_password_reset_email(
                    to_email=email,
                    reset_url=reset_url,
                    user_name=user.get('nome')
                )
                
                if not email_sent:
                    # Se não conseguir enviar email, mostra o link na tela (fallback)
                    flash('Se o e-mail estiver cadastrado, você receberá um link para redefinir sua senha.', 'info')
                    return render_template('esqueci_senha.html', 
                                         show_dev_link=True, 
                                         reset_url=reset_url,
                                         email=email)
            
            # Sempre mostra a mesma mensagem por segurança
            flash('Se o e-mail estiver cadastrado, você receberá um link para redefinir sua senha.', 'info')
        
        return render_template('esqueci_senha.html')
    
    @staticmethod
    def redefinir_senha(token=None):
        """Processa a redefinição de senha usando token"""
        # Verifica se o token foi fornecido
        if not token:
            token = request.args.get('token')
        
        if not token:
            flash('Link inválido ou expirado. Por favor, solicite a recuperação de senha novamente.', 'error')
            return redirect(url_for('esqueci_senha'))
        
        # Valida o token
        if not PasswordReset.is_token_valid(token):
            flash('Link inválido ou expirado. Por favor, solicite a recuperação de senha novamente.', 'error')
            return redirect(url_for('esqueci_senha'))
        
        # Obtém o email do token
        email = PasswordReset.get_email_from_token(token)
        
        if not email:
            flash('Link inválido. Por favor, solicite a recuperação de senha novamente.', 'error')
            return redirect(url_for('esqueci_senha'))
        
        user = User.get_by_email(email)
        
        if not user:
            PasswordReset.delete_token(token)
            flash('Usuário não encontrado!', 'error')
            return redirect(url_for('esqueci_senha'))
        
        if request.method == 'POST':
            nova_senha = request.form['nova_senha']
            confirmar_senha = request.form['confirmar_senha']
            
            if not nova_senha or not confirmar_senha:
                flash('Preencha todos os campos!', 'error')
                return render_template('redefinir_senha.html', email=email, token=token)
            
            if len(nova_senha) < 6:
                flash('A senha deve ter no mínimo 6 caracteres!', 'error')
                return render_template('redefinir_senha.html', email=email, token=token)
            
            if nova_senha != confirmar_senha:
                flash('As senhas não coincidem!', 'error')
                return render_template('redefinir_senha.html', email=email, token=token)
            
            # Atualizar senha
            success, error = User.update(email=email, senha=nova_senha)
            
            if error:
                flash(error, 'error')
                return render_template('redefinir_senha.html', email=email, token=token)
            
            # Marca o token como usado após uso bem-sucedido
            PasswordReset.mark_token_as_used(token)
            
            flash('Senha redefinida com sucesso! Faça login com sua nova senha.', 'success')
            return redirect(url_for('login'))
        
        return render_template('redefinir_senha.html', email=email, token=token)
    
    @staticmethod
    def require_login(message='Faça login para acessar esta página!'):
        """Verifica se o usuário está logado"""
        if 'user_email' not in session:
            flash(message, 'error')
            return redirect(url_for('login'))
        return None

