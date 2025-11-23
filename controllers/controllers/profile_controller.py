"""Controlador de perfil do usuário"""
from flask import request, session, redirect, url_for, render_template, flash
from models.user import User
from models.user_profile import UserProfile
from models.recipe import Recipe
from utils import check_password, allowed_file
from werkzeug.utils import secure_filename
from config import Config
import os
import time
from controllers.auth_controller import AuthController

class ProfileController:
    """Controlador para operações de perfil"""
    
    @staticmethod
    def perfil():
        """Exibe e edita o perfil do usuário"""
        login_check = AuthController.require_login()
        if login_check:
            return login_check
        
        user = User.get_by_email(session['user_email'])
        
        if not user:
            session.clear()
            return AuthController.require_login('Usuário não encontrado!')
        
        # Buscar perfil do usuário
        profile = UserProfile.get_by_email(session['user_email'])
        if not profile:
            # Criar perfil vazio se não existir
            UserProfile.create(session['user_email'])
            profile = UserProfile.get_by_email(session['user_email'])
        
        # Contar receitas do usuário (usando JOIN - atende requisito)
        user_recipes = Recipe.get_by_author(session['user_email'])
        total_receitas = len(user_recipes)
        
        if request.method == 'POST':
            nome = request.form.get('nome', '').strip()
            senha_atual = request.form.get('senha_atual', '')
            nova_senha = request.form.get('nova_senha', '')
            confirmar_senha = request.form.get('confirmar_senha', '')
            
            # Dados do perfil
            bio = request.form.get('bio', '').strip() or None
            telefone = request.form.get('telefone', '').strip() or None
            data_nascimento = request.form.get('data_nascimento', '').strip() or None
            cidade = request.form.get('cidade', '').strip() or None
            estado = request.form.get('estado', '').strip() or None
            pais = request.form.get('pais', '').strip() or 'Brasil'
            
            # Validações
            if not nome:
                flash('Nome é obrigatório!', 'error')
                return render_template('perfil.html', user=user, profile=profile, total_receitas=total_receitas)
            
            # Validação de senha se tentar alterar
            if nova_senha:
                if not senha_atual:
                    flash('Para alterar a senha, é necessário informar a senha atual!', 'error')
                    return render_template('perfil.html', user=user, profile=profile, total_receitas=total_receitas)
                
                if not check_password(senha_atual, user['senha']):
                    flash('Senha atual incorreta!', 'error')
                    return render_template('perfil.html', user=user, profile=profile, total_receitas=total_receitas)
                
                if len(nova_senha) < 6:
                    flash('A nova senha deve ter no mínimo 6 caracteres!', 'error')
                    return render_template('perfil.html', user=user, profile=profile, total_receitas=total_receitas)
                
                if nova_senha != confirmar_senha:
                    flash('As senhas não coincidem!', 'error')
                    return render_template('perfil.html', user=user, profile=profile, total_receitas=total_receitas)
            
            # Processar upload de foto de perfil
            foto_perfil = profile.get('foto_perfil') if profile else None
            if 'foto_perfil' in request.files:
                file = request.files['foto_perfil']
                if file and file.filename and allowed_file(file.filename):
                    # Remover foto antiga se existir
                    if foto_perfil and os.path.exists(os.path.join(Config.UPLOAD_FOLDER, foto_perfil)):
                        os.remove(os.path.join(Config.UPLOAD_FOLDER, foto_perfil))
                    
                    # Salvar nova foto
                    filename = secure_filename(file.filename)
                    # Adicionar prefixo único para evitar conflitos
                    filename = f"profile_{session['user_email'].replace('@', '_').replace('.', '_')}_{int(time.time())}_{filename}"
                    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
                    file.save(filepath)
                    foto_perfil = filename
            
            # Atualizar dados do usuário
            success, error = User.update(
                email=session['user_email'],
                nome=nome,
                senha=nova_senha if nova_senha else None
            )
            
            if error:
                flash(error, 'error')
                return render_template('perfil.html', user=user, profile=profile, total_receitas=total_receitas)
            
            # Atualizar perfil do usuário
            profile_success = UserProfile.update(
                email=session['user_email'],
                bio=bio,
                foto_perfil=foto_perfil,
                telefone=telefone,
                data_nascimento=data_nascimento,
                cidade=cidade,
                estado=estado,
                pais=pais
            )
            
            if not profile_success:
                flash('Erro ao atualizar perfil!', 'error')
                return render_template('perfil.html', user=user, profile=profile, total_receitas=total_receitas)
            
            session['user_name'] = nome
            flash('Perfil atualizado com sucesso!', 'success')
            return redirect(url_for('perfil'))
        
        return render_template('perfil.html', user=user, profile=profile, total_receitas=total_receitas)
    
    @staticmethod
    def excluir_conta():
        """Exclui a conta do usuário"""
        login_check = AuthController.require_login()
        if login_check:
            return login_check
        
        user_email = session['user_email']
        
        # Remover receitas do usuário
        user_recipes = Recipe.get_by_author(user_email)
        for receita in user_recipes:
            if receita.get('imagem'):
                image_path = os.path.join(Config.UPLOAD_FOLDER, receita['imagem'])
                if os.path.exists(image_path):
                    os.remove(image_path)
        
        Recipe.delete_by_author(user_email)
        
        # Remover usuário
        User.delete(user_email)
        
        session.clear()
        flash('Sua conta foi excluída com sucesso!', 'success')
        return redirect(url_for('index'))

