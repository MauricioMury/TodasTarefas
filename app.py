import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Tarefa, Categoria
from datetime import datetime, date, time
from notificacoes import enviar_email, enviar_whatsapp, montar_notificacao

# ------------------------------------------------------------------
# HELPER (adicionar junto às funções helper no topo do app.py)
# ------------------------------------------------------------------
 
def parse_notif_datetime(valor_str):
    """
    Converte string de datetime-local ('YYYY-MM-DDTHH:MM') para objeto datetime.
    Retorna None se vazio ou inválido.
    """
    if not valor_str:
        return None
    try:
        return datetime.strptime(valor_str, '%Y-%m-%dT%H:%M')
    except ValueError:
        return None

# ==========================================
# FUNÇÕES HELPER PARA FILTROS
# ==========================================

def get_filtros_ativos():
    """Captura filtros ativos da URL ou sessão"""
    # Priorizar URL sobre sessão
    filtros = {
        'categoria': request.args.get('categoria', session.get('filtro_categoria', '')),
        'prioridade': request.args.get('prioridade', session.get('filtro_prioridade', '')),
        'status': request.args.get('status', session.get('filtro_status', '')),
        'data': request.args.get('data', session.get('filtro_data', '')),
        'busca': request.args.get('busca', session.get('filtro_busca', '')),
        'page': request.args.get('page', session.get('filtro_page', 1), type=int),
        'per_page': request.args.get('per_page', session.get('filtro_per_page', 10), type=int)
    }
    
    # Salvar na sessão para persistir
    session['filtro_categoria'] = filtros['categoria']
    session['filtro_prioridade'] = filtros['prioridade']
    session['filtro_status'] = filtros['status']
    session['filtro_data'] = filtros['data']
    session['filtro_busca'] = filtros['busca']
    session['filtro_page'] = filtros['page']
    session['filtro_per_page'] = filtros['per_page']
    
    return filtros

def limpar_filtros_sessao():
    """Limpa todos os filtros da sessão"""
    session.pop('filtro_categoria', None)
    session.pop('filtro_prioridade', None)
    session.pop('filtro_status', None)
    session.pop('filtro_data', None)
    session.pop('filtro_busca', None)
    session.pop('filtro_page', None)
    session.pop('filtro_per_page', None)


def redirect_com_filtros(rota, **kwargs):
    """Redireciona mantendo os filtros ativos"""
    filtros = get_filtros_ativos()
    filtros.update(kwargs)
    
    # Remover valores vazios para não poluir a URL
    filtros_limpos = {k: v for k, v in filtros.items() if v}
    
    return redirect(url_for(rota, **filtros_limpos))

# ==========================================
# CONFIGURAÇÃO DA APLICAÇÃO
# ==========================================

app = Flask(__name__)
#app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui-mude-em-producao'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tarefas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = None

# =============================================================
# ESTÁGIO 5 — TRIGGER before_request
# Arquivo: app.py
#
# INSTRUÇÕES:
#   Adicione o bloco abaixo no app.py, logo após a definição
#   do login_manager (após a linha login_manager.login_message = None).
#   O decorador @app.before_request já cuida do registro automático.
# =============================================================

@app.before_request
def verificar_notificacoes():
    if not current_user or not current_user.is_authenticated:
        return

    # Só processa se o usuário tiver e-mail configurado
    if not current_user.email_notif:
        return

    agora = datetime.now()
    MAX_POR_REQUEST = 5

    tem_whatsapp = bool(current_user.whatsapp_numero and current_user.whatsapp_apikey)

    try:
        # ── Notificação 1 ────────────────────────────────────────
        pendentes_1 = Tarefa.query.filter(
            Tarefa.user_id               == current_user.id,
            Tarefa.notif_datetime_1      != None,
            Tarefa.notif_datetime_1      <= agora,
            db.or_(
                Tarefa.notif_email_enviada_1     == False,
                Tarefa.notif_whatsapp_enviada_1  == False,
            )
        ).limit(MAX_POR_REQUEST).all()

        for tarefa in pendentes_1:
            assunto, corpo = montar_notificacao(tarefa)

            if current_user.email_notif and not tarefa.notif_email_enviada_1:
                sucesso_email = enviar_email(current_user.email_notif, assunto, corpo)
                if sucesso_email:
                    tarefa.notif_email_enviada_1 = True

            if tem_whatsapp and not tarefa.notif_whatsapp_enviada_1:
                sucesso_zap = enviar_whatsapp(
                    current_user.whatsapp_numero,
                    current_user.whatsapp_apikey,
                    f'{assunto}\n\n{corpo}'
                )
                if sucesso_zap:
                    tarefa.notif_whatsapp_enviada_1 = True

            db.session.commit()

        # ── Notificação 2 ────────────────────────────────────────
        pendentes_2 = Tarefa.query.filter(
            Tarefa.user_id               == current_user.id,
            Tarefa.notif_datetime_2      != None,
            Tarefa.notif_datetime_2      <= agora,
            db.or_(
                Tarefa.notif_email_enviada_2     == False,
                Tarefa.notif_whatsapp_enviada_2  == False,
            )
        ).limit(MAX_POR_REQUEST).all()

        for tarefa in pendentes_2:
            assunto, corpo = montar_notificacao(tarefa)

            if current_user.email_notif and not tarefa.notif_email_enviada_2:
                sucesso_email = enviar_email(current_user.email_notif, assunto, corpo)
                if sucesso_email:
                    tarefa.notif_email_enviada_2 = True

            if tem_whatsapp and not tarefa.notif_whatsapp_enviada_2:
                sucesso_zap = enviar_whatsapp(
                    current_user.whatsapp_numero,
                    current_user.whatsapp_apikey,
                    f'{assunto}\n\n{corpo}'
                )
                if sucesso_zap:
                    tarefa.notif_whatsapp_enviada_2 = True

            db.session.commit()

    except Exception as e:
        app.logger.error(f'verificar_notificacoes: erro inesperado: {e}')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==========================================
# INICIALIZAÇÃO DO BANCO
# ==========================================

def init_db():
    """Inicializa o banco de dados e cria usuário admin"""
    with app.app_context():
        db.create_all()
        
        # Criar usuário admin se não existir
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password=generate_password_hash('admin')
            )
            db.session.add(admin)
            db.session.commit()
            print('✅ Usuário admin criado com sucesso!')
            
            # Criar categorias padrão para o admin
            categorias_padrao = [
                {'nome': 'Família', 'cor': 'success'},
                {'nome': 'Trabalho', 'cor': 'primary'},
                {'nome': 'Casa', 'cor': 'warning'},
                {'nome': 'Amigos', 'cor': 'info'},
                {'nome': 'Estudo', 'cor': 'secondary'},
                {'nome': 'Financeiro', 'cor': 'danger'},
                {'nome': 'Espiritual', 'cor': 'light'},
                {'nome': 'Saúde', 'cor': 'success'},
            ]
            
            for cat_data in categorias_padrao:
                categoria = Categoria(
                    nome=cat_data['nome'],
                    cor=cat_data['cor'],
                    user_id=admin.id
                )
                db.session.add(categoria)
            
            db.session.commit()
            print('✅ Categorias padrão criadas!')

# ==========================================
# ROTAS DE AUTENTICAÇÃO
# ==========================================

@app.route('/')
@login_required
def index():
    """Dashboard principal"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login de usuário"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha inválidos!', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Cadastro de novo usuário"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('As senhas não coincidem!', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Usuário já existe!', 'danger')
            return render_template('register.html')
        
        new_user = User(
            username=username,
            password=generate_password_hash(password)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Criar categorias padrão para o novo usuário
        categorias_padrao = [
            {'nome': 'Família', 'cor': 'success'},
            {'nome': 'Trabalho', 'cor': 'primary'},
            {'nome': 'Casa', 'cor': 'warning'},
            {'nome': 'Amigos', 'cor': 'info'},
            {'nome': 'Estudo', 'cor': 'secondary'},
            {'nome': 'Financeiro', 'cor': 'danger'},
            {'nome': 'Espiritual', 'cor': 'light'},
            {'nome': 'Saúde', 'cor': 'success'},
        ]
        
        for cat_data in categorias_padrao:
            categoria = Categoria(
                nome=cat_data['nome'],
                cor=cat_data['cor'],
                user_id=new_user.id
            )
            db.session.add(categoria)
        
        db.session.commit()
        
        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    logout_user()
    return redirect(url_for('login'))

# ------------------------------------------------------------------
# ROTA: /perfil   (adicionar no app.py)
# ------------------------------------------------------------------
 
@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    if request.method == 'POST':
        email = request.form.get('email_notif', '').strip()
        current_user.email_notif = email or None
        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('perfil'))

    return render_template('perfil.html')

# ==========================================
# ROTAS DE CATEGORIAS
# ==========================================

@app.route('/categorias')
@login_required
def lista_categorias():
    """Lista todas as categorias do usuário"""
    categorias = Categoria.query.filter_by(user_id=current_user.id).order_by(Categoria.nome).all()
    return render_template('lista_categorias.html', categorias=categorias)

@app.route('/cadastro_categoria', methods=['GET', 'POST'])
@login_required
def cadastro_categoria():
    """Cadastro de nova categoria"""
    if request.method == 'POST':
        try:
            nome = request.form.get('nome')
            cor = request.form.get('cor', 'info')
            
            # Verificar se já existe
            existe = Categoria.query.filter_by(
                nome=nome, 
                user_id=current_user.id
            ).first()
            
            if existe:
                flash(f'A categoria "{nome}" já existe!', 'warning')
                return render_template('cadastro_categoria.html')
            
            nova_categoria = Categoria(
                nome=nome,
                cor=cor,
                user_id=current_user.id
            )
            
            db.session.add(nova_categoria)
            db.session.commit()
            
            flash(f'Categoria "{nome}" criada com sucesso!', 'success')
            return redirect(url_for('lista_categorias'))
            
        except Exception as e:
            flash(f'Erro ao cadastrar categoria: {str(e)}', 'danger')
    
    return render_template('cadastro_categoria.html')

@app.route('/editar_categoria/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_categoria(id):
    """Editar categoria existente"""
    categoria = Categoria.query.get_or_404(id)
    
    if categoria.user_id != current_user.id:
        flash('Você não tem permissão para editar esta categoria!', 'danger')
        return redirect(url_for('lista_categorias'))
    
    if request.method == 'POST':
        try:
            nome = request.form.get('nome')
            cor = request.form.get('cor', 'info')
            
            # Verificar se já existe outra categoria com esse nome
            existe = Categoria.query.filter(
                Categoria.nome == nome,
                Categoria.user_id == current_user.id,
                Categoria.id != id
            ).first()
            
            if existe:
                flash(f'Já existe outra categoria com o nome "{nome}"!', 'warning')
                return render_template('editar_categoria.html', categoria=categoria)
            
            categoria.nome = nome
            categoria.cor = cor
            
            db.session.commit()
            flash(f'Categoria "{nome}" atualizada com sucesso!', 'success')
            return redirect(url_for('lista_categorias'))
            
        except Exception as e:
            flash(f'Erro ao atualizar categoria: {str(e)}', 'danger')
    
    return render_template('editar_categoria.html', categoria=categoria)

@app.route('/deletar_categoria/<int:id>', methods=['POST'])
@login_required
def deletar_categoria(id):
    """Deletar categoria"""
    categoria = Categoria.query.get_or_404(id)
    
    if categoria.user_id != current_user.id:
        flash('Você não tem permissão para deletar esta categoria!', 'danger')
        return redirect(url_for('lista_categorias'))
    
    # Verificar se há tarefas usando esta categoria
    tarefas_com_categoria = Tarefa.query.filter_by(
        user_id=current_user.id,
        categoria=categoria.nome
    ).count()
    
    if tarefas_com_categoria > 0:
        flash(f'Não é possível deletar "{categoria.nome}" pois há {tarefas_com_categoria} tarefa(s) usando esta categoria!', 'danger')
        return redirect(url_for('lista_categorias'))
    
    nome = categoria.nome
    db.session.delete(categoria)
    db.session.commit()
    
    flash(f'Categoria "{nome}" deletada com sucesso!', 'success')
    return redirect(url_for('lista_categorias'))

# ==========================================
# ROTAS DE TAREFAS
# ==========================================

@app.route('/cadastro_tarefa', methods=['GET', 'POST'])
@login_required
def cadastro_tarefa():
    """Cadastro de nova tarefa"""
    categorias = Categoria.query.filter_by(user_id=current_user.id).order_by(Categoria.nome).all()
    
    if request.method == 'POST':
        try:
            tarefa = request.form.get('tarefa')
            comentario = request.form.get('comentario', '')
            data_meta = datetime.strptime(request.form.get('data_meta'), '%Y-%m-%d').date()
            data_realizado = request.form.get('data_realizado')
            hora_inicio = datetime.strptime(request.form.get('hora_inicio'), '%H:%M').time()
            
            hora_fim_str = request.form.get('hora_fim')
            hora_fim = datetime.strptime(hora_fim_str, '%H:%M').time() if hora_fim_str else None
            
            prioridade = request.form.get('prioridade')
            recorrencia = request.form.get('recorrencia')
            categoria = request.form.get('categoria')
            
            if data_realizado:
                data_realizado = datetime.strptime(data_realizado, '%Y-%m-%d').date()
            else:
                data_realizado = None
            
            if hora_fim:
                if hora_fim <= hora_inicio:
                    flash('A hora de fim deve ser posterior à hora de início!', 'danger')
                    return render_template('cadastro_tarefa.html', categorias=categorias)
            
            # 🆕 Notificações
            notif_dt_1 = parse_notif_datetime(request.form.get('notif_datetime_1'))
            notif_dt_2 = parse_notif_datetime(request.form.get('notif_datetime_2'))


            nova_tarefa = Tarefa(
                tarefa=tarefa,
                comentario=comentario,
                data_meta=data_meta,
                data_realizado=data_realizado,
                hora_inicio=hora_inicio,
                hora_fim=hora_fim,
                prioridade=prioridade,
                recorrencia=recorrencia,
                categoria=categoria,
                status='Concluída' if data_realizado else 'Pendente',
                user_id=current_user.id,

                # 🆕
                notif_datetime_1=notif_dt_1,
                notif_email_enviada_1=False,
                notif_whatsapp_enviada_1=False,
                notif_datetime_2=notif_dt_2,
                notif_email_enviada_2=False,
                notif_whatsapp_enviada_2=False,
            )
            
            db.session.add(nova_tarefa)
            db.session.commit()
            
            flash('Tarefa cadastrada com sucesso!', 'success')
            return redirect_com_filtros('lista_tarefas')
            
        except Exception as e:
            flash(f'Erro ao cadastrar tarefa: {str(e)}', 'danger')
    
    # GET - Pode vir de duplicação
    duplicate_id = request.args.get('duplicate')
    tarefa_nome = request.args.get('tarefa', '')
    comentario = request.args.get('comentario', '')
    hora_inicio = request.args.get('hora_inicio', '')
    prioridade = request.args.get('prioridade', '')
    recorrencia = request.args.get('recorrencia', '')
    categoria = request.args.get('categoria', '')
    
    # Capturar filtros ativos para o botão "Voltar"
    filtros = get_filtros_ativos()
    
    return render_template('cadastro_tarefa.html',
                        categorias=categorias,
                        duplicate_id=duplicate_id,
                        tarefa=tarefa_nome,
                        comentario=comentario,
                        hora_inicio=hora_inicio,
                        prioridade=prioridade,
                        recorrencia=recorrencia,
                        categoria=categoria,
                        filtros=filtros)

@app.route('/lista_tarefas')
@login_required
def lista_tarefas():
    """Lista de tarefas com filtros e paginação"""
    
    # 🔧 CORREÇÃO: Verificar se é uma requisição de limpeza
    limpar = request.args.get('limpar')
    if limpar:
        # Limpar filtros da sessão
        limpar_filtros_sessao()
        # Redireciona sem parâmetros (exceto per_page)
        per_page = request.args.get('per_page', 10, type=int)
        return redirect(url_for('lista_tarefas', per_page=per_page))
    
    # Capturar filtros
    filtros = get_filtros_ativos()
    
    page = filtros['page']
    per_page = filtros['per_page']
    categoria_filtro = filtros['categoria']
    prioridade_filtro = filtros['prioridade']
    status_filtro = filtros['status']
    data_filtro = filtros['data']
    busca_filtro = filtros['busca']
    
    # Buscar categorias do usuário para o dropdown
    categorias = Categoria.query.filter_by(user_id=current_user.id).order_by(Categoria.nome).all()
    
    query = Tarefa.query.filter_by(user_id=current_user.id)
    
    # Aplicar filtros
    if categoria_filtro:
        query = query.filter_by(categoria=categoria_filtro)
    if prioridade_filtro:
        query = query.filter_by(prioridade=prioridade_filtro)
    if status_filtro:
        query = query.filter_by(status=status_filtro)
    if data_filtro:
        data_obj = datetime.strptime(data_filtro, '%Y-%m-%d').date()
        query = query.filter_by(data_meta=data_obj)
    if busca_filtro:
        termo = f'%{busca_filtro}%'
        from sqlalchemy import func
        query = query.filter(
            db.or_(
                Tarefa.tarefa.ilike(termo),
                func.coalesce(Tarefa.comentario, '').ilike(termo)
            )
        )
    
    tarefas = query.all()
    
    # Ordena por data, depois por hora
    tarefas_ordenadas = sorted(tarefas, key=lambda x: (x.data_meta, x.hora_inicio))
    
    total = len(tarefas_ordenadas)
    start = (page - 1) * per_page
    end = start + per_page
    tarefas_paginadas = tarefas_ordenadas[start:end]
    
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('lista_tarefas.html', 
                        tarefas=tarefas_paginadas,
                        categorias=categorias,
                        page=page,
                        per_page=per_page,
                        total_pages=total_pages,
                        total=total,
                        categoria_filtro=categoria_filtro,
                        prioridade_filtro=prioridade_filtro,
                        status_filtro=status_filtro,
                        data_filtro=data_filtro,
                        busca_filtro=busca_filtro)

@app.route('/editar_tarefa/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_tarefa(id):
    """Editar tarefa existente"""
    tarefa = Tarefa.query.get_or_404(id)
    categorias = Categoria.query.filter_by(user_id=current_user.id).order_by(Categoria.nome).all()
    
    if tarefa.user_id != current_user.id:
        flash('Você não tem permissão para editar esta tarefa!', 'danger')
        return redirect_com_filtros('lista_tarefas')
    
    if request.method == 'POST':
        try:
            tarefa.tarefa = request.form.get('tarefa')
            tarefa.comentario = request.form.get('comentario', '')
            tarefa.data_meta = datetime.strptime(request.form.get('data_meta'), '%Y-%m-%d').date()
            
            data_realizado = request.form.get('data_realizado')
            if data_realizado:
                tarefa.data_realizado = datetime.strptime(data_realizado, '%Y-%m-%d').date()
                tarefa.status = 'Concluída'
            else:
                tarefa.data_realizado = None
                tarefa.status = 'Pendente'
            
            tarefa.hora_inicio = datetime.strptime(request.form.get('hora_inicio'), '%H:%M').time()
            
            hora_fim_str = request.form.get('hora_fim')
            tarefa.hora_fim = datetime.strptime(hora_fim_str, '%H:%M').time() if hora_fim_str else None
            
            if tarefa.hora_fim:
                if tarefa.hora_fim <= tarefa.hora_inicio:
                    flash('A hora de fim deve ser posterior à hora de início!', 'danger')
                    return render_template('editar_tarefa.html', tarefa=tarefa, categorias=categorias)
            
            tarefa.prioridade = request.form.get('prioridade')
            tarefa.recorrencia = request.form.get('recorrencia')
            tarefa.categoria = request.form.get('categoria')
            
            novo_dt_1 = parse_notif_datetime(request.form.get('notif_datetime_1'))
            novo_dt_2 = parse_notif_datetime(request.form.get('notif_datetime_2'))

            # Se o datetime mudou, reseta flags de e-mail e WhatsApp (reativa a notificação)
            if novo_dt_1 != tarefa.notif_datetime_1:
                tarefa.notif_email_enviada_1    = False
                tarefa.notif_whatsapp_enviada_1 = False
            tarefa.notif_datetime_1 = novo_dt_1

            if novo_dt_2 != tarefa.notif_datetime_2:
                tarefa.notif_email_enviada_2    = False
                tarefa.notif_whatsapp_enviada_2 = False
            tarefa.notif_datetime_2 = novo_dt_2

            db.session.commit()
            flash('Tarefa atualizada com sucesso!', 'success')
            return redirect_com_filtros('lista_tarefas')
            
        except Exception as e:
            flash(f'Erro ao atualizar tarefa: {str(e)}', 'danger')
    
    # Capturar filtros ativos para o botão "Voltar"
    filtros = get_filtros_ativos()
    
    return render_template('editar_tarefa.html', tarefa=tarefa, categorias=categorias, filtros=filtros)

@app.route('/duplicar_tarefa/<int:id>')
@login_required
def duplicar_tarefa(id):
    """Duplica uma tarefa existente para facilitar recriação"""
    tarefa = Tarefa.query.get_or_404(id)
    
    if tarefa.user_id != current_user.id:
        flash('Você não tem permissão para duplicar esta tarefa!', 'danger')
        return redirect_com_filtros('lista_tarefas')
    
    # Redireciona para cadastro com dados da tarefa
    return redirect(url_for('cadastro_tarefa',
                            duplicate=id,
                            tarefa=tarefa.tarefa,
                            comentario=tarefa.comentario,
                            hora_inicio=tarefa.hora_inicio.strftime('%H:%M'),
                            prioridade=tarefa.prioridade,
                            recorrencia=tarefa.recorrencia,
                            categoria=tarefa.categoria))

@app.route('/deletar_tarefa/<int:id>', methods=['POST'])
@login_required
def deletar_tarefa(id):
    """Deletar tarefa"""
    tarefa = Tarefa.query.get_or_404(id)
    
    if tarefa.user_id != current_user.id:
        flash('Você não tem permissão para deletar esta tarefa!', 'danger')
        return redirect_com_filtros('lista_tarefas')
    
    db.session.delete(tarefa)
    db.session.commit()
    
    flash('Tarefa deletada com sucesso!', 'success')
    return redirect_com_filtros('lista_tarefas')

@app.route('/marcar_concluida/<int:id>', methods=['POST'])
@login_required
def marcar_concluida(id):
    """Marcar tarefa como concluída"""
    tarefa = Tarefa.query.get_or_404(id)
    
    if tarefa.user_id != current_user.id:
        flash('Você não tem permissão para modificar esta tarefa!', 'danger')
        return redirect_com_filtros('lista_tarefas')
    
    tarefa.status = 'Concluída'
    tarefa.data_realizado = date.today()
    db.session.commit()
    
    flash('Tarefa marcada como concluída!', 'success')
    return redirect_com_filtros('lista_tarefas')

# ==========================================
# ROTA DO CALENDÁRIO
# ==========================================

@app.route('/calendario')
@login_required
def calendario():
    """Calendário de tarefas"""
    import json

    tarefas = Tarefa.query.filter_by(user_id=current_user.id).all()
    categorias = Categoria.query.filter_by(user_id=current_user.id).order_by(Categoria.nome).all()

    # Serializar tarefas para JSON (apenas campos necessários)
    tarefas_json = json.dumps([{
        'id':          t.id,
        'tarefa':      t.tarefa,
        'comentario':  t.comentario or '',
        'data_meta':   t.data_meta.strftime('%Y-%m-%d'),
        'hora_inicio': t.hora_inicio.strftime('%H:%M'),
        'hora_fim':    t.hora_fim.strftime('%H:%M') if t.hora_fim else '',
        'prioridade':  t.prioridade,
        'categoria':   t.categoria,
        'status':      t.status,
    } for t in tarefas], ensure_ascii=False)

    categorias_json = json.dumps([{
        'nome': c.nome,
        'cor':  c.cor,
    } for c in categorias], ensure_ascii=False)

    return render_template('calendario.html',
                           tarefas_json=tarefas_json,
                           categorias_json=categorias_json)

# ── Rota entrada rápida ──────────────────

@app.route('/entrada_rapida')
@login_required
def entrada_rapida():
    """Página de entrada rápida de tarefa por texto livre"""
    import json
    categorias = Categoria.query.filter_by(user_id=current_user.id).order_by(Categoria.nome).all()
    categorias_json = json.dumps([{'nome': c.nome, 'cor': c.cor} for c in categorias], ensure_ascii=False)
    return render_template('entrada_rapida.html', categorias_json=categorias_json)

# ── Rota mover tarefas ──────────────────

@app.route('/mover_tarefa/<int:id>', methods=['POST'])
@login_required
def mover_tarefa(id):
    """Move a data_meta de uma tarefa (usado pelo drag & drop do calendário)"""
    from flask import jsonify
    import json

    tarefa = Tarefa.query.get_or_404(id)

    if tarefa.user_id != current_user.id:
        return jsonify({'ok': False, 'erro': 'Sem permissão'}), 403

    data = request.get_json()
    nova_data_str = data.get('data_meta')

    if not nova_data_str:
        return jsonify({'ok': False, 'erro': 'Data inválida'}), 400

    try:
        nova_data = datetime.strptime(nova_data_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'ok': False, 'erro': 'Formato de data inválido'}), 400

    tarefa.data_meta = nova_data

    # Se tinha data_realizado e era a data antiga, não altera — é decisão do usuário
    # Se estava Concluída, mantém o status (só mudou a data planejada)

    db.session.commit()
    return jsonify({'ok': True})

# ==========================================
# INICIALIZAÇÃO
# ==========================================

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5050)