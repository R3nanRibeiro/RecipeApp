"""Modelo de Receita - agora usando MySQL com estrutura normalizada"""
from db import get_connection, dict_cursor

class Recipe:
    """Classe que representa uma receita"""

    # ================== helpers internos ==================

    @staticmethod
    def _row_to_dict(row):
        """Converte uma linha do banco em um dict no formato esperado pela view."""
        receita_id = row.get('id')
        
        # Buscar ingredientes da tabela normalizada
        ingredientes_list = []
        if receita_id:
            try:
                conn = get_connection()
                cur = dict_cursor(conn)
                cur.execute("""
                    SELECT ri.quantidade, ri.unidade, ri.observacao, 
                           COALESCE(i.nome, '') as nome_ingrediente
                    FROM recipe_ingredients ri
                    LEFT JOIN ingredients i ON ri.ingredient_id = i.id
                    WHERE ri.recipe_id = %s
                    ORDER BY ri.ordem
                """, (receita_id,))
                ingredientes_rows = cur.fetchall()
                for ing in ingredientes_rows:
                    if ing.get('nome_ingrediente'):
                        qtd = f"{ing.get('quantidade') or ''} {ing.get('unidade') or ''}".strip()
                        obs = f" ({ing.get('observacao')})" if ing.get('observacao') else ""
                        ingredientes_list.append(f"{qtd} {ing.get('nome_ingrediente')}{obs}".strip())
                    elif ing.get('observacao'):
                        ingredientes_list.append(ing.get('observacao'))
                cur.close()
                conn.close()
            except Exception as e:
                print(f"Erro ao buscar ingredientes: {e}")
        
        # Se não encontrou ingredientes normalizados, tenta formato antigo (compatibilidade)
        if not ingredientes_list and row.get('ingredientes'):
            ingredientes_str = row.get('ingredientes') or ''
            ingredientes_list = [i.strip() for i in ingredientes_str.split('\n') if i.strip()]
        
        # Buscar passos do modo de preparo da tabela normalizada
        modo_preparo_list = []
        if receita_id:
            try:
                conn = get_connection()
                cur = dict_cursor(conn)
                cur.execute("""
                    SELECT passo_numero, descricao
                    FROM recipe_steps
                    WHERE recipe_id = %s
                    ORDER BY passo_numero
                """, (receita_id,))
                passos_rows = cur.fetchall()
                modo_preparo_list = [p.get('descricao', '') for p in passos_rows]
                cur.close()
                conn.close()
            except Exception as e:
                print(f"Erro ao buscar passos: {e}")
        
        # Se não encontrou passos normalizados, tenta formato antigo (compatibilidade)
        if not modo_preparo_list and row.get('modo_preparo'):
            modo_preparo_str = row.get('modo_preparo') or ''
            modo_preparo_list = [p.strip() for p in modo_preparo_str.split('\n') if p.strip()]

        return {
            'id': row['id'],
            'titulo': row['titulo'],
            'descricao': row.get('descricao'),
            'categoria': row.get('categoria_nome') or row.get('categoria'),  # Suporta ambos
            'categoria_id': row.get('categoria_id'),
            'tempo_preparo': row.get('tempo_preparo'),
            'porcoes': row.get('porcoes'),
            'dificuldade': row.get('dificuldade'),
            'ingredientes': ingredientes_list,
            'modo_preparo': modo_preparo_list,
            'autor': row.get('autor'),
            'autor_email': row.get('autor_email'),
            'imagem': row.get('imagem'),
            'visualizacoes': row.get('visualizacoes', 0),
            'media_avaliacao': row.get('media_avaliacao'),
            'total_avaliacoes': row.get('total_avaliacoes', 0),
            'total_comentarios': row.get('total_comentarios', 0),
            'total_favoritos': row.get('total_favoritos', 0)
        }

    # ================== métodos públicos (usados nos controllers) ==================

    @staticmethod
    def get_all():
        """Retorna todas as receitas usando a view com JOIN e subqueries."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            # Usa a view que já tem JOINs e subqueries
            cur.execute("SELECT * FROM vw_receitas_completas ORDER BY id DESC")
            rows = cur.fetchall()
            return [Recipe._row_to_dict(r) for r in rows]
        except Exception as e:
            print("Erro em Recipe.get_all:", e)
            # Fallback para consulta direta se a view não existir
            try:
                conn = get_connection()
                cur = dict_cursor(conn)
                cur.execute("""
                    SELECT r.*, c.nome AS categoria_nome
                    FROM recipes r
                    LEFT JOIN categories c ON r.categoria_id = c.id
                    WHERE r.ativa = 1
                    ORDER BY r.id DESC
                """)
                rows = cur.fetchall()
                return [Recipe._row_to_dict(r) for r in rows]
            except Exception as e2:
                print("Erro no fallback:", e2)
                return []
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    @staticmethod
    def get_by_id(receita_id):
        """Busca uma receita pelo ID usando JOIN."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            # Consulta com JOIN e subquery (atende requisito)
            cur.execute("""
                SELECT 
                    r.*,
                    c.nome AS categoria_nome,
                    (SELECT COALESCE(AVG(nota), 0) FROM recipe_ratings WHERE recipe_id = r.id) AS media_avaliacao,
                    (SELECT COUNT(*) FROM recipe_ratings WHERE recipe_id = r.id) AS total_avaliacoes,
                    (SELECT COUNT(*) FROM comments WHERE recipe_id = r.id AND ativo = 1) AS total_comentarios,
                    (SELECT COUNT(*) FROM favorites WHERE recipe_id = r.id) AS total_favoritos
                FROM recipes r
                LEFT JOIN categories c ON r.categoria_id = c.id
                WHERE r.id = %s AND r.ativa = 1
            """, (receita_id,))
            row = cur.fetchone()
            if not row:
                return None
            
            # Incrementar visualizações
            cur.execute("UPDATE recipes SET visualizacoes = visualizacoes + 1 WHERE id = %s", (receita_id,))
            conn.commit()
            
            return Recipe._row_to_dict(row)
        except Exception as e:
            print("Erro em Recipe.get_by_id:", e)
            return None
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    @staticmethod
    def get_by_category(categoria):
        """Busca receitas por categoria usando JOIN."""
        if categoria == 'todos':
            return Recipe.get_all()

        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            # Consulta com JOIN (atende requisito)
            cur.execute("""
                SELECT 
                    r.*,
                    c.nome AS categoria_nome,
                    (SELECT COALESCE(AVG(nota), 0) FROM recipe_ratings WHERE recipe_id = r.id) AS media_avaliacao,
                    (SELECT COUNT(*) FROM recipe_ratings WHERE recipe_id = r.id) AS total_avaliacoes,
                    (SELECT COUNT(*) FROM comments WHERE recipe_id = r.id AND ativo = 1) AS total_comentarios,
                    (SELECT COUNT(*) FROM favorites WHERE recipe_id = r.id) AS total_favoritos
                FROM recipes r
                INNER JOIN categories c ON r.categoria_id = c.id
                WHERE c.nome = %s AND r.ativa = 1
                ORDER BY r.id DESC
            """, (categoria,))
            rows = cur.fetchall()
            return [Recipe._row_to_dict(r) for r in rows]
        except Exception as e:
            print("Erro em Recipe.get_by_category:", e)
            return []
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    @staticmethod
    def get_by_author(author_email):
        """Busca receitas por autor usando JOIN."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            # Consulta com JOIN (atende requisito)
            cur.execute("""
                SELECT 
                    r.*,
                    c.nome AS categoria_nome,
                    (SELECT COALESCE(AVG(nota), 0) FROM recipe_ratings WHERE recipe_id = r.id) AS media_avaliacao,
                    (SELECT COUNT(*) FROM recipe_ratings WHERE recipe_id = r.id) AS total_avaliacoes
                FROM recipes r
                LEFT JOIN categories c ON r.categoria_id = c.id
                WHERE r.autor_email = %s AND r.ativa = 1
                ORDER BY r.id DESC
            """, (author_email,))
            rows = cur.fetchall()
            return [Recipe._row_to_dict(r) for r in rows]
        except Exception as e:
            print("Erro em Recipe.get_by_author:", e)
            return []
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    @staticmethod
    def create(titulo, descricao, categoria, tempo_preparo, porcoes,
               dificuldade, ingredientes, modo_preparo, autor,
               autor_email, imagem=None):
        """Cria uma nova receita com ingredientes e passos normalizados."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)

            # Buscar categoria_id pelo nome
            from models.category import Category
            categoria_obj = Category.get_by_name(categoria)
            if not categoria_obj:
                raise ValueError(f'Categoria "{categoria}" não encontrada! Verifique se a categoria existe no banco de dados.')
            categoria_id = categoria_obj['id']

            # Converter porcoes para int
            try:
                porcoes_int = int(porcoes) if porcoes else None
            except:
                porcoes_int = None

            # Inserir receita
            cur.execute(
                """
                INSERT INTO recipes
                (titulo, descricao, categoria_id, tempo_preparo, porcoes,
                 dificuldade, autor, autor_email, imagem)
                VALUES (%s, %s, %s, %s, %s,
                        %s, %s, %s, %s)
                """,
                (
                    titulo, descricao, categoria_id, tempo_preparo, porcoes_int,
                    dificuldade, autor, autor_email, imagem
                )
            )
            recipe_id = cur.lastrowid

            # Inserir ingredientes na tabela normalizada
            if isinstance(ingredientes, list):
                for ordem, ingrediente in enumerate(ingredientes, 1):
                    ingrediente_str = str(ingrediente).strip() if ingrediente else ""
                    if ingrediente_str:
                        # Tentar encontrar ingrediente existente ou criar novo
                        cur.execute("SELECT id FROM ingredients WHERE nome = %s", (ingrediente_str,))
                        ing_row = cur.fetchone()
                        ingredient_id = ing_row['id'] if ing_row else None
                        
                        # Se não encontrou, criar novo ingrediente genérico
                        if not ingredient_id:
                            cur.execute(
                                "INSERT INTO ingredients (nome) VALUES (%s)",
                                (ingrediente_str,)
                            )
                            ingredient_id = cur.lastrowid
                        
                        # Inserir relação
                        cur.execute("""
                            INSERT INTO recipe_ingredients 
                            (recipe_id, ingredient_id, observacao, ordem)
                            VALUES (%s, %s, %s, %s)
                        """, (recipe_id, ingredient_id, ingrediente_str, ordem))

            # Inserir passos do modo de preparo na tabela normalizada
            if isinstance(modo_preparo, list):
                for passo_num, passo in enumerate(modo_preparo, 1):
                    passo_str = str(passo).strip() if passo else ""
                    if passo_str:
                        cur.execute("""
                            INSERT INTO recipe_steps 
                            (recipe_id, passo_numero, descricao)
                            VALUES (%s, %s, %s)
                        """, (recipe_id, passo_num, passo_str))

            conn.commit()
            return recipe_id

        except ValueError as e:
            # Erro de validação (ex: categoria não encontrada)
            print("Erro de validação em Recipe.create:", e)
            if 'conn' in locals() and conn.is_connected():
                conn.rollback()
            raise e  # Re-raise para que o controller possa capturar
        except Exception as e:
            print("Erro em Recipe.create:", e)
            if 'conn' in locals() and conn.is_connected():
                conn.rollback()
            raise e  # Re-raise para que o controller possa capturar
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    @staticmethod
    def update(receita_id, titulo=None, descricao=None, categoria=None,
               tempo_preparo=None, porcoes=None, dificuldade=None,
               ingredientes=None, modo_preparo=None, imagem=None):
        """Atualiza uma receita existente."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            
            # Carrega receita atual
            receita_atual = Recipe.get_by_id(receita_id)
            if not receita_atual:
                return False, 'Receita não encontrada!'

            # Preparar valores para atualização
            novo_titulo = titulo if titulo else receita_atual['titulo']
            nova_descricao = descricao if descricao else receita_atual.get('descricao')
            novo_tempo_preparo = tempo_preparo if tempo_preparo else receita_atual.get('tempo_preparo')
            nova_porcoes = porcoes if porcoes else receita_atual.get('porcoes')
            nova_dificuldade = dificuldade if dificuldade else receita_atual.get('dificuldade')
            nova_imagem = imagem if imagem is not None else receita_atual.get('imagem')

            # Converter porcoes para int
            try:
                nova_porcoes_int = int(nova_porcoes) if nova_porcoes else None
            except:
                nova_porcoes_int = None

            # Atualizar categoria se necessário
            categoria_id = receita_atual.get('categoria_id')
            if categoria:
                from models.category import Category
                categoria_obj = Category.get_by_name(categoria)
                if categoria_obj:
                    categoria_id = categoria_obj['id']

            # Atualizar receita
            cur.execute(
                """
                UPDATE recipes
                SET titulo = %s,
                    descricao = %s,
                    categoria_id = %s,
                    tempo_preparo = %s,
                    porcoes = %s,
                    dificuldade = %s,
                    imagem = %s
                WHERE id = %s
                """,
                (
                    novo_titulo, nova_descricao, categoria_id, novo_tempo_preparo,
                    nova_porcoes_int, nova_dificuldade, nova_imagem, receita_id
                )
            )

            # Atualizar ingredientes se fornecidos
            if ingredientes is not None:
                # Remover ingredientes antigos
                cur.execute("DELETE FROM recipe_ingredients WHERE recipe_id = %s", (receita_id,))
                
                # Inserir novos ingredientes
                if isinstance(ingredientes, list):
                    for ordem, ingrediente in enumerate(ingredientes, 1):
                        if ingrediente.strip():
                            cur.execute("SELECT id FROM ingredients WHERE nome = %s", (ingrediente.strip(),))
                            ing_row = cur.fetchone()
                            ingredient_id = ing_row['id'] if ing_row else None
                            
                            if not ingredient_id:
                                cur.execute("INSERT INTO ingredients (nome) VALUES (%s)", (ingrediente.strip(),))
                                ingredient_id = cur.lastrowid
                            
                            cur.execute("""
                                INSERT INTO recipe_ingredients 
                                (recipe_id, ingredient_id, observacao, ordem)
                                VALUES (%s, %s, %s, %s)
                            """, (receita_id, ingredient_id, ingrediente.strip(), ordem))

            # Atualizar passos se fornecidos
            if modo_preparo is not None:
                # Remover passos antigos
                cur.execute("DELETE FROM recipe_steps WHERE recipe_id = %s", (receita_id,))
                
                # Inserir novos passos
                if isinstance(modo_preparo, list):
                    for passo_num, passo in enumerate(modo_preparo, 1):
                        if passo.strip():
                            cur.execute("""
                                INSERT INTO recipe_steps 
                                (recipe_id, passo_numero, descricao)
                                VALUES (%s, %s, %s)
                            """, (receita_id, passo_num, passo.strip()))

            conn.commit()
            return True, None

        except Exception as e:
            print("Erro em Recipe.update:", e)
            conn.rollback()
            return False, 'Erro ao atualizar receita!'
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    @staticmethod
    def delete(receita_id):
        """Marca uma receita como inativa (soft delete) para preservar histórico."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            cur.execute("UPDATE recipes SET ativa = 0 WHERE id = %s", (receita_id,))
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            print("Erro em Recipe.delete:", e)
            return False
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    @staticmethod
    def delete_by_author(author_email):
        """Marca todas as receitas de um autor como inativas (soft delete)."""
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            cur.execute("UPDATE recipes SET ativa = 0 WHERE autor_email = %s", (author_email,))
            conn.commit()
            return True
        except Exception as e:
            print("Erro em Recipe.delete_by_author:", e)
            return False
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals() and conn.is_connected(): conn.close()

    @staticmethod
    def get_media_avaliacoes(receita_id):
        """Usa procedimento armazenado para calcular média de avaliações."""
        conn = None
        cur = None
        try:
            conn = get_connection()
            cur = dict_cursor(conn)
            # Chamar procedimento armazenado (atende requisito)
            # Os parâmetros OUT são passados como lista e depois lidos
            results = cur.callproc('sp_calcular_media_avaliacoes', [receita_id, 0, 0])
            # Para MySQL connector, os resultados OUT são retornados na lista
            # results[0] = receita_id (IN), results[1] = media (OUT), results[2] = total (OUT)
            media = float(results[1]) if results[1] else 0.0
            total = int(results[2]) if results[2] else 0
            return media, total
        except Exception as e:
            print("Erro ao chamar procedimento:", e)
            # Fallback para consulta direta
            try:
                if not conn or not conn.is_connected():
                    conn = get_connection()
                cur = dict_cursor(conn)
                cur.execute("""
                    SELECT COALESCE(AVG(nota), 0) as media, COUNT(*) as total
                    FROM recipe_ratings
                    WHERE recipe_id = %s
                """, (receita_id,))
                row = cur.fetchone()
                media = float(row['media']) if row and row['media'] else 0.0
                total = int(row['total']) if row and row['total'] else 0
                return media, total
            except Exception as e2:
                print("Erro no fallback:", e2)
                return 0.0, 0
        finally:
            if cur: cur.close()
            if conn and conn.is_connected(): conn.close()
