"""Controlador de autenticação"""
from flask import request, session, render_template, redirect, url_for, flash
from models.user import User
from utils import check_password

class AuthController:
    """Controlador para operações de autenticação"""
    
    @staticmethod
    def login():
        """Processa o login do usuário"""
        if request.method == 'POST':
            email = request.form['email'].strip().lower()
            senha = request.form['senha']
            lembrar = 'lembrar' in request.form
            
            user = User.get_by_email(email)
            
            if user and check_password(senha, user['senha']):
                # Verificar se usuário está ativo
                if not user.get('ativo', True):
                    flash('Sua conta está desativada. Entre em contato com o suporte.', 'error')
                    return render_template('login.html', lembrar_checked=user.get('lembrar', False))
                
                session['user_email'] = email
                session['user_name'] = user['nome']
                
                # Atualizar preferência de lembrar senha no banco de dados
                User.update_lembrar(email, lembrar)
                
                # Atualizar último acesso
                User.update_last_access(email)
                
                # Configurar sessão permanente se lembrar estiver marcado
                if lembrar:
                    session.permanent = True
                else:
                    session.permanent = False
                
                flash(f'Bem-vindo(a), {user["nome"]}!', 'success')
                return redirect(url_for('index'))
            else:
                flash('E-mail ou senha incorretos!', 'error')
                # Tentar carregar preferência de lembrar se o email existir
                user = User.get_by_email(email)
                lembrar_checked = user.get('lembrar', False) if user else False
                return render_template('login.html', lembrar_checked=lembrar_checked)
        
        # GET: verificar se há email na query string e pré-marcar lembrar se aplicável
        email_prefill = request.args.get('email', '').strip().lower()
        lembrar_checked = False
        if email_prefill:
            user = User.get_by_email(email_prefill)
            if user:
                lembrar_checked = user.get('lembrar', False)
        
        return render_template('login.html', lembrar_checked=lembrar_checked)
    
    @staticmethod
    def cadastro():
        """Processa o cadastro de novos usuários"""
        if request.method == 'POST':
            nome = request.form['nome'].strip()
            email = request.form['email'].strip().lower()
            senha = request.form['senha']
            lembrar = 'lembrar' in request.form
            
            # Validações
            if not nome or not email or not senha:
                flash('Todos os campos são obrigatórios!', 'error')
                return render_template('cadastro.html')
            
            if len(senha) < 6:
                flash('A senha deve ter no mínimo 6 caracteres!', 'error')
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
    def require_login(message='Faça login para acessar esta página!'):
        """Verifica se o usuário está logado"""
        if 'user_email' not in session:
            flash(message, 'error')
            return redirect(url_for('login'))
        return None

