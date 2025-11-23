"""Controlador de Favoritos"""
from flask import request, session, redirect, url_for, flash, jsonify
from models.favorite import Favorite
from controllers.auth_controller import AuthController

class FavoriteController:
    """Controlador para operações de favoritos"""

    @staticmethod
    def toggle(recipe_id):
        """Adiciona ou remove uma receita dos favoritos"""
        login_check = AuthController.require_login('Faça login para favoritar receitas!')
        if login_check:
            return login_check

        if Favorite.is_favorite(recipe_id, session['user_email']):
            # Remove dos favoritos
            success = Favorite.remove_favorite(recipe_id, session['user_email'])
            if success:
                flash('Receita removida dos favoritos!', 'info')
            else:
                flash('Erro ao remover dos favoritos!', 'error')
        else:
            # Adiciona aos favoritos
            success = Favorite.add_favorite(recipe_id, session['user_email'])
            if success:
                flash('Receita adicionada aos favoritos!', 'success')
            else:
                flash('Erro ao adicionar aos favoritos!', 'error')
        
        return redirect(url_for('visualizar_receita', receita_id=recipe_id))

    @staticmethod
    def api_toggle(recipe_id):
        """API para favoritar/desfavoritar (AJAX)"""
        if 'user_email' not in session:
            return jsonify({'success': False, 'error': 'Faça login para favoritar!'}), 401
        
        try:
            is_favorite = Favorite.is_favorite(recipe_id, session['user_email'])
            
            if is_favorite:
                success = Favorite.remove_favorite(recipe_id, session['user_email'])
                message = 'Removido dos favoritos!'
            else:
                success = Favorite.add_favorite(recipe_id, session['user_email'])
                message = 'Adicionado aos favoritos!'
            
            if success:
                return jsonify({
                    'success': True,
                    'is_favorite': not is_favorite,
                    'message': message
                })
            else:
                return jsonify({'success': False, 'error': 'Erro ao atualizar favoritos!'}), 400
        except Exception as e:
            print(f"Erro na API de favoritos: {e}")
            return jsonify({'success': False, 'error': 'Erro ao processar!'}), 500

    @staticmethod
    def listar():
        """Lista todas as receitas favoritas do usuário"""
        login_check = AuthController.require_login()
        if login_check:
            return login_check
        
        from flask import render_template
        from models.recipe import Recipe
        
        favorites = Favorite.get_user_favorites(session['user_email'])
        # Converter para o formato esperado
        receitas = []
        for fav in favorites:
            receita = Recipe.get_by_id(fav['id'])
            if receita:
                # Garantir que tenha média de avaliação
                if not receita.get('media_avaliacao'):
                    media, total = Recipe.get_media_avaliacoes(receita['id'])
                    receita['media_avaliacao'] = float(media) if media else 0.0
                    receita['total_avaliacoes'] = total
                receitas.append(receita)
        
        return render_template('favoritos.html', receitas=receitas)

