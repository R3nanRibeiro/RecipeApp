"""Controlador de receitas"""
from flask import request, session, send_file, render_template, redirect, url_for, flash
import os
import io
from reportlab.pdfgen import canvas
from werkzeug.utils import secure_filename
from models.recipe import Recipe
from config import Config
from utils import allowed_file
from controllers.auth_controller import AuthController

class RecipeController:
    """Controlador para operações de receitas"""
    
    @staticmethod
    def index():
        """Página inicial com receitas em destaque"""
        recipes = Recipe.get_all()
        featured_recipes = recipes[:3] if len(recipes) >= 3 else recipes
        # Garantir que todas as receitas tenham média de avaliação
        for receita in featured_recipes:
            if not receita.get('media_avaliacao'):
                media, total = Recipe.get_media_avaliacoes(receita['id'])
                receita['media_avaliacao'] = float(media) if media else 0.0
                receita['total_avaliacoes'] = total
        return render_template('index.html', featured_recipes=featured_recipes)
    
    @staticmethod
    def listar():
        """Lista todas as receitas com filtro opcional por categoria"""
        categoria = request.args.get('categoria', 'todos')
        receitas = Recipe.get_by_category(categoria)
        # Garantir que todas as receitas tenham média de avaliação
        for receita in receitas:
            if not receita.get('media_avaliacao'):
                media, total = Recipe.get_media_avaliacoes(receita['id'])
                receita['media_avaliacao'] = float(media) if media else 0.0
                receita['total_avaliacoes'] = total
        return render_template('receitas.html', receitas=receitas, categoria_atual=categoria)
    
    @staticmethod
    def visualizar(receita_id):
        """Visualiza uma receita específica"""
        receita = Recipe.get_by_id(receita_id)
        if not receita:
            flash('Receita não encontrada!', 'error')
            return redirect(url_for('receitas'))
        
        # Usar procedimento armazenado para obter média de avaliações (atende requisito)
        media, total = Recipe.get_media_avaliacoes(receita_id)
        receita['media_avaliacao'] = float(media) if media else 0.0
        receita['total_avaliacoes'] = total
        
        # Buscar avaliações detalhadas e estatísticas
        from models.recipe_rating import RecipeRating
        from models.comment import Comment
        from models.favorite import Favorite
        
        avaliacoes = RecipeRating.get_by_recipe(receita_id)
        comentarios = Comment.get_by_recipe(receita_id)
        stats_avaliacoes = RecipeRating.get_stats(receita_id)
        
        # Verificar se usuário já avaliou e se está favoritada
        user_rating = None
        is_favorite = False
        if 'user_email' in session:
            user_rating = RecipeRating.get_user_rating(receita_id, session['user_email'])
            is_favorite = Favorite.is_favorite(receita_id, session['user_email'])
        
        # Registrar acesso (access_logs)
        from models.access_log import AccessLog
        AccessLog.create(
            endpoint=f'/visualizar_receita/{receita_id}',
            metodo=request.method,
            ip_address=request.remote_addr,
            user_email=session.get('user_email')
        )
        
        return render_template(
            'visualizar_receita.html',
            receita=receita,
            receita_id=receita_id,
            avaliacoes=avaliacoes,
            comentarios=comentarios,
            stats_avaliacoes=stats_avaliacoes,
            user_rating=user_rating,
            is_favorite=is_favorite
        )
    
    @staticmethod
    def adicionar():
        """Adiciona uma nova receita"""
        login_check = AuthController.require_login()
        if login_check:
            return login_check
        
        if request.method == 'POST':
            # Coletar dados do formulário
            titulo = request.form['titulo'].strip()
            descricao = request.form['descricao'].strip()
            categoria = request.form['categoria']
            tempo_preparo = request.form['tempo_preparo'].strip()
            porcoes_str = request.form['porcoes'].strip()
            # Extrair número de porcoes (ex: "8 porções" -> 8)
            try:
                porcoes = ''.join(filter(str.isdigit, porcoes_str)) or porcoes_str
            except:
                porcoes = porcoes_str
            dificuldade = request.form['dificuldade']
            ingredientes = [i.strip() for i in request.form['ingredientes'].split('\n') if i.strip()]
            modo_preparo = [p.strip() for p in request.form['modo_preparo'].split('\n') if p.strip()]
            
            # Validações
            if not all([titulo, descricao, categoria, tempo_preparo, porcoes, dificuldade]):
                flash('Preencha todos os campos obrigatórios!', 'error')
                return render_template('adicionar_receita.html')
            
            if not ingredientes:
                flash('Adicione pelo menos um ingrediente!', 'error')
                return render_template('adicionar_receita.html')
            
            if not modo_preparo:
                flash('Adicione pelo menos um passo no modo de preparo!', 'error')
                return render_template('adicionar_receita.html')
            
            # Processar upload de imagem
            imagem = None
            if 'imagem' in request.files:
                file = request.files['imagem']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
                    file.save(filepath)
                    imagem = filename
            
            # Criar nova receita
            try:
                recipe_id = Recipe.create(
                    titulo=titulo,
                    descricao=descricao,
                    categoria=categoria,
                    tempo_preparo=tempo_preparo,
                    porcoes=porcoes,
                    dificuldade=dificuldade,
                    ingredientes=ingredientes,
                    modo_preparo=modo_preparo,
                    autor=session['user_name'],
                    autor_email=session['user_email'],
                    imagem=imagem
                )
                
                if not recipe_id:
                    flash('Erro ao criar receita! Por favor, tente novamente.', 'error')
                    return render_template('adicionar_receita.html')
                
                flash('Receita adicionada com sucesso!', 'success')
                return redirect(url_for('receitas'))
            except ValueError as e:
                # Erro de validação (ex: categoria não encontrada)
                flash(str(e), 'error')
                return render_template('adicionar_receita.html')
            except Exception as e:
                print(f"Erro ao criar receita: {e}")
                flash('Erro ao criar receita! Por favor, verifique os dados e tente novamente.', 'error')
                return render_template('adicionar_receita.html')
        
        return render_template('adicionar_receita.html')
    
    @staticmethod
    def editar(receita_id):
        """Edita uma receita existente"""
        login_check = AuthController.require_login()
        if login_check:
            return login_check
        
        receita = Recipe.get_by_id(receita_id)
        
        if not receita:
            flash('Receita não encontrada!', 'error')
            return redirect(url_for('receitas'))
        
        # Verificar se o usuário é o autor
        if receita.get('autor_email') != session['user_email']:
            flash('Você só pode editar suas próprias receitas!', 'error')
            return redirect(url_for('visualizar_receita', receita_id=receita_id))
        
        if request.method == 'POST':
            # Coletar dados atualizados
            titulo = request.form['titulo'].strip()
            descricao = request.form['descricao'].strip()
            categoria = request.form['categoria']
            tempo_preparo = request.form['tempo_preparo'].strip()
            porcoes_str = request.form['porcoes'].strip()
            # Extrair número de porcoes (ex: "8 porções" -> 8)
            try:
                porcoes = ''.join(filter(str.isdigit, porcoes_str)) or porcoes_str
            except:
                porcoes = porcoes_str
            dificuldade = request.form['dificuldade']
            ingredientes = [i.strip() for i in request.form['ingredientes'].split('\n') if i.strip()]
            modo_preparo = [p.strip() for p in request.form['modo_preparo'].split('\n') if p.strip()]
            
            # Validações
            if not all([titulo, descricao, categoria, tempo_preparo, porcoes, dificuldade]):
                flash('Preencha todos os campos obrigatórios!', 'error')
                return render_template('editar_receita.html', receita=receita, receita_id=receita_id)
            
            if not ingredientes:
                flash('Adicione pelo menos um ingrediente!', 'error')
                return render_template('editar_receita.html', receita=receita, receita_id=receita_id)
            
            if not modo_preparo:
                flash('Adicione pelo menos um passo no modo de preparo!', 'error')
                return render_template('editar_receita.html', receita=receita, receita_id=receita_id)
            
            # Processar upload de nova imagem
            imagem = receita.get('imagem')  # Manter imagem atual por padrão
            if 'imagem' in request.files:
                file = request.files['imagem']
                if file and file.filename and allowed_file(file.filename):
                    # Remover imagem antiga se existir
                    if receita.get('imagem'):
                        old_path = os.path.join(Config.UPLOAD_FOLDER, receita['imagem'])
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    
                    # Salvar nova imagem
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
                    file.save(filepath)
                    imagem = filename
            
            # Atualizar receita
            Recipe.update(
                receita_id=receita_id,
                titulo=titulo,
                descricao=descricao,
                categoria=categoria,
                tempo_preparo=tempo_preparo,
                porcoes=porcoes,
                dificuldade=dificuldade,
                ingredientes=ingredientes,
                modo_preparo=modo_preparo,
                imagem=imagem
            )
            
            flash('Receita atualizada com sucesso!', 'success')
            return redirect(url_for('visualizar_receita', receita_id=receita_id))
        
        return render_template('editar_receita.html', receita=receita, receita_id=receita_id)
    
    @staticmethod
    def excluir(receita_id):
        """Exclui uma receita"""
        login_check = AuthController.require_login()
        if login_check:
            return login_check
        
        receita = Recipe.get_by_id(receita_id)
        
        if not receita:
            flash('Receita não encontrada!', 'error')
            return redirect(url_for('receitas'))
        
        # Verificar se o usuário é o autor
        if receita.get('autor_email') != session['user_email']:
            flash('Você só pode excluir suas próprias receitas!', 'error')
            return redirect(url_for('visualizar_receita', receita_id=receita_id))
        
        # Remover imagem se existir
        if receita.get('imagem'):
            image_path = os.path.join(Config.UPLOAD_FOLDER, receita['imagem'])
            if os.path.exists(image_path):
                os.remove(image_path)
        
        # Remover receita
        Recipe.delete(receita_id)
        
        flash('Receita excluída com sucesso!', 'success')
        return redirect(url_for('receitas'))
    
    @staticmethod
    def download(receita_id):
        """Gera PDF da receita para download"""
        receita = Recipe.get_by_id(receita_id)
        
        if not receita:
            flash('Receita não encontrada!', 'error')
            return redirect(url_for('receitas'))
        
        # Criar PDF em memória
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        
        # Adicionar conteúdo ao PDF
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, 800, receita['titulo'])
        
        p.setFont("Helvetica", 12)
        p.drawString(50, 770, f"Por: {receita['autor']}")
        p.drawString(50, 750, f"Tempo de preparo: {receita['tempo_preparo']}")
        p.drawString(50, 730, f"Porções: {receita['porcoes']}")
        p.drawString(50, 710, f"Dificuldade: {receita['dificuldade']}")
        
        p.drawString(50, 680, "Ingredientes:")
        y = 660
        for ingrediente in receita['ingredientes']:
            p.drawString(70, y, f"• {ingrediente}")
            y -= 20
            if y < 100:  # Nova página se necessário
                p.showPage()
                y = 800
        
        y -= 20
        p.drawString(50, y, "Modo de Preparo:")
        y -= 20
        
        for i, passo in enumerate(receita['modo_preparo'], 1):
            p.drawString(70, y, f"{i}. {passo}")
            y -= 20
            if y < 100:  # Nova página se necessário
                p.showPage()
                y = 800
        
        p.save()
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"{receita['titulo']}.pdf",
            mimetype='application/pdf'
        )

