"""Controlador de Avaliações"""
from flask import request, session, render_template, redirect, url_for, flash, jsonify
from models.recipe_rating import RecipeRating
from models.recipe import Recipe
from controllers.auth_controller import AuthController

class RatingController:
    """Controlador para operações de avaliações"""

    @staticmethod
    def avaliar(recipe_id):
        """Processa a avaliação de uma receita"""
        login_check = AuthController.require_login('Faça login para avaliar receitas!')
        if login_check:
            return login_check

        if request.method == 'POST':
            try:
                nota = int(request.form.get('nota', 0))
                comentario = request.form.get('comentario', '').strip()
                
                if not (1 <= nota <= 5):
                    flash('A nota deve estar entre 1 e 5!', 'error')
                    return redirect(url_for('visualizar_receita', receita_id=recipe_id))
                
                success, error = RecipeRating.create_or_update(
                    recipe_id=recipe_id,
                    user_email=session['user_email'],
                    nota=nota,
                    comentario=comentario if comentario else None
                )
                
                if success:
                    flash('Avaliação salva com sucesso!', 'success')
                else:
                    flash(error or 'Erro ao salvar avaliação!', 'error')
                
                return redirect(url_for('visualizar_receita', receita_id=recipe_id))
            except ValueError:
                flash('Nota inválida!', 'error')
                return redirect(url_for('visualizar_receita', receita_id=recipe_id))
            except Exception as e:
                print(f"Erro ao avaliar receita: {e}")
                flash('Erro ao processar avaliação!', 'error')
                return redirect(url_for('visualizar_receita', receita_id=recipe_id))
        
        return redirect(url_for('visualizar_receita', receita_id=recipe_id))

    @staticmethod
    def remover_avaliacao(recipe_id):
        """Remove a avaliação de um usuário"""
        login_check = AuthController.require_login()
        if login_check:
            return login_check
        
        success = RecipeRating.delete(recipe_id, session['user_email'])
        
        if success:
            flash('Avaliação removida com sucesso!', 'success')
        else:
            flash('Erro ao remover avaliação!', 'error')
        
        return redirect(url_for('visualizar_receita', receita_id=recipe_id))

    @staticmethod
    def api_avaliar(recipe_id):
        """API para avaliar receita (AJAX)"""
        if 'user_email' not in session:
            return jsonify({'success': False, 'error': 'Faça login para avaliar!'}), 401
        
        try:
            data = request.get_json()
            nota = int(data.get('nota', 0))
            comentario = data.get('comentario', '').strip()
            
            if not (1 <= nota <= 5):
                return jsonify({'success': False, 'error': 'Nota deve estar entre 1 e 5!'}), 400
            
            success, error = RecipeRating.create_or_update(
                recipe_id=recipe_id,
                user_email=session['user_email'],
                nota=nota,
                comentario=comentario if comentario else None
            )
            
            if success:
                stats = RecipeRating.get_stats(recipe_id)
                user_rating = RecipeRating.get_user_rating(recipe_id, session['user_email'])
                return jsonify({
                    'success': True,
                    'stats': stats,
                    'user_rating': user_rating
                })
            else:
                return jsonify({'success': False, 'error': error or 'Erro ao salvar avaliação!'}), 400
        except Exception as e:
            print(f"Erro na API de avaliação: {e}")
            return jsonify({'success': False, 'error': 'Erro ao processar avaliação!'}), 500

