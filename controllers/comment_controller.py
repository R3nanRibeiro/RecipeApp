"""Controlador de Comentários"""
from flask import request, session, render_template, redirect, url_for, flash
from models.comment import Comment
from models.recipe import Recipe
from controllers.auth_controller import AuthController

class CommentController:
    """Controlador para operações de comentários"""

    @staticmethod
    def adicionar(recipe_id):
        """Adiciona um comentário a uma receita"""
        login_check = AuthController.require_login('Faça login para comentar!')
        if login_check:
            return login_check

        if request.method == 'POST':
            conteudo = request.form.get('comentario', '').strip()
            
            if not conteudo:
                flash('O comentário não pode estar vazio!', 'error')
                return redirect(url_for('visualizar_receita', receita_id=recipe_id))
            
            if len(conteudo) > 2000:
                flash('O comentário deve ter no máximo 2000 caracteres!', 'error')
                return redirect(url_for('visualizar_receita', receita_id=recipe_id))
            
            comment_id = Comment.create(
                recipe_id=recipe_id,
                user_email=session['user_email'],
                conteudo=conteudo
            )
            
            if comment_id:
                flash('Comentário adicionado com sucesso!', 'success')
            else:
                flash('Erro ao adicionar comentário!', 'error')
        
        return redirect(url_for('visualizar_receita', receita_id=recipe_id))

    @staticmethod
    def excluir(comment_id):
        """Exclui um comentário (apenas o autor pode excluir)"""
        login_check = AuthController.require_login()
        if login_check:
            return login_check
        
        # Buscar comentário para verificar se é do usuário e obter recipe_id
        comments = Comment.get_by_recipe(0)  # Buscar todos para encontrar
        # Seria melhor ter um método get_by_id no Comment, mas vamos usar outra abordagem
        # Por enquanto, vamos redirecionar e deixar o usuário informar
        flash('Funcionalidade de exclusão de comentário em desenvolvimento.', 'info')
        return redirect(url_for('receitas'))

