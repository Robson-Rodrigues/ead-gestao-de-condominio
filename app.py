from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from sqlalchemy import or_, and_
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'condominio.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'

db = SQLAlchemy(app)

class Unidade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(10), nullable=False, unique=True)
    bloco = db.Column(db.String(10), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    vagas_garagem = db.Column(db.Integer, default=0)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    moradores = db.relationship('Morador', backref='unidade', lazy=True)

class Morador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), nullable=False, unique=True)
    telefone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    unidade_id = db.Column(db.Integer, db.ForeignKey('unidade.id'), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    reservas = db.relationship('Reserva', backref='morador', lazy=True)
    notificacoes = db.relationship('Notificacao', backref='morador', lazy=True)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    morador_id = db.Column(db.Integer, db.ForeignKey('morador.id'), nullable=True)
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    morador = db.relationship('Morador', backref='usuario', uselist=False)
    notificacoes_enviadas = db.relationship('Notificacao', backref='autor', lazy=True)
    notificacoes_lidas = db.relationship('NotificacaoLeitura', backref='usuario', lazy=True, cascade='all, delete-orphan')
    mensagens_enviadas = db.relationship('ChatMensagem', foreign_keys='ChatMensagem.remetente_id', backref='remetente', lazy=True, cascade='all, delete-orphan')
    mensagens_recebidas = db.relationship('ChatMensagem', foreign_keys='ChatMensagem.destinatario_id', backref='destinatario', lazy=True, cascade='all, delete-orphan')

class Visitante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), nullable=False)
    telefone = db.Column(db.String(15), nullable=False)
    unidade_id = db.Column(db.Integer, db.ForeignKey('unidade.id'), nullable=False)
    data_entrada = db.Column(db.DateTime, default=datetime.utcnow)
    data_saida = db.Column(db.DateTime, nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
    
    unidade = db.relationship('Unidade', backref='visitantes')

class Multa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    morador_id = db.Column(db.Integer, db.ForeignKey('morador.id'), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    data_vencimento = db.Column(db.Date, nullable=False)
    data_pagamento = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='Pendente')
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    morador = db.relationship('Morador', backref='multas')

class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    morador_id = db.Column(db.Integer, db.ForeignKey('morador.id'), nullable=False)
    area = db.Column(db.String(100), nullable=False)
    data = db.Column(db.Date, nullable=False)
    horario_inicio = db.Column(db.Time, nullable=False)
    horario_fim = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='Pendente')
    observacoes = db.Column(db.Text, nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

class Funcionario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    cargo = db.Column(db.String(80), nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    turno = db.Column(db.String(50), nullable=True)
    ativo = db.Column(db.Boolean, default=True)
    data_admissao = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    observacoes = db.Column(db.Text, nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

class Notificacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    morador_id = db.Column(db.Integer, db.ForeignKey('morador.id'), nullable=True)
    autor_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)
    
    leituras = db.relationship('NotificacaoLeitura', backref='notificacao', lazy=True, cascade='all, delete-orphan')

class NotificacaoLeitura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notificacao_id = db.Column(db.Integer, db.ForeignKey('notificacao.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    lida_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('notificacao_id', 'usuario_id', name='uq_notificacao_leitura'),
    )

class ChatMensagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    remetente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    destinatario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    enviada_em = db.Column(db.DateTime, default=datetime.utcnow)
    lida_em = db.Column(db.DateTime, nullable=True)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        usuario = Usuario.query.get(session['user_id'])
        if not usuario or usuario.tipo != 'Admin':
            flash('Acesso negado. Apenas administradores podem acessar esta página.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_badges():
    if 'user_id' not in session:
        return {'notificacoes_nao_lidas': 0, 'chat_nao_lidas': 0}
    
    usuario = Usuario.query.get(session['user_id'])
    if not usuario:
        return {'notificacoes_nao_lidas': 0, 'chat_nao_lidas': 0}
    
    notificacoes_query = Notificacao.query
    if usuario.tipo != 'Admin':
        notificacoes_query = notificacoes_query.filter(
            or_(Notificacao.morador_id == None, Notificacao.morador_id == usuario.morador_id)
        )
    
    notificacoes_nao_lidas = notificacoes_query.filter(
        ~Notificacao.leituras.any(NotificacaoLeitura.usuario_id == usuario.id)
    ).count()
    
    chat_nao_lidas = ChatMensagem.query.filter_by(destinatario_id=usuario.id, lida_em=None).count()
    
    return {
        'notificacoes_nao_lidas': notificacoes_nao_lidas,
        'chat_nao_lidas': chat_nao_lidas
    }

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    usuario = Usuario.query.get(session['user_id'])
    unidades = Unidade.query.all()
    moradores = Morador.query.all()
    
    if usuario.tipo == 'Admin':
        visitantes_ativos = Visitante.query.filter_by(data_saida=None).count()
        multas_pendentes = Multa.query.filter_by(status='Pendente').count()
        valor_multas = db.session.query(db.func.sum(Multa.valor)).filter_by(status='Pendente').scalar() or 0
        reservas_pendentes = Reserva.query.filter_by(status='Pendente').count()
        funcionarios_ativos = Funcionario.query.filter_by(ativo=True).count()
        notificacoes_totais = Notificacao.query.count()
        
        return render_template('index.html', 
                             unidades=unidades, 
                             moradores=moradores,
                             visitantes_ativos=visitantes_ativos,
                             multas_pendentes=multas_pendentes,
                             valor_multas=valor_multas,
                             reservas_pendentes=reservas_pendentes,
                             funcionarios_ativos=funcionarios_ativos,
                             notificacoes_totais=notificacoes_totais)
    
    else:
        moradores_unidade = Morador.query.filter_by(unidade_id=usuario.morador.unidade_id).count()
        visitantes_ativos = Visitante.query.filter_by(unidade_id=usuario.morador.unidade_id, data_saida=None).count()
        multas_abertas = Multa.query.filter_by(morador_id=usuario.morador_id, status='Pendente').count()
        valor_multas = db.session.query(db.func.sum(Multa.valor)).filter_by(morador_id=usuario.morador_id, status='Pendente').scalar() or 0
        reservas_realizadas = Reserva.query.filter_by(morador_id=usuario.morador_id).count()
        notificacoes_disponiveis = Notificacao.query.filter(or_(Notificacao.morador_id == None, Notificacao.morador_id == usuario.morador_id)).count()
        
        return render_template('index.html', 
                             unidades=unidades, 
                             moradores=moradores,
                             moradores_unidade=moradores_unidade,
                             visitantes_ativos=visitantes_ativos,
                             multas_abertas=multas_abertas,
                             valor_multas=valor_multas,
                             reservas_realizadas=reservas_realizadas,
                             notificacoes_disponiveis=notificacoes_disponiveis)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        senha = request.form.get('senha', '').strip()
        
        print(f"Tentativa de login: username='{username}', senha='{senha}'")
        
        if not username or not senha:
            flash('Por favor, preencha todos os campos!', 'error')
            return render_template('login.html')
        
        usuario = Usuario.query.filter_by(username=username, ativo=True).first()
        
        if usuario:
            print(f"Usuário encontrado: {usuario.username}, tipo: {usuario.tipo}")
            senha_valida = check_password_hash(usuario.senha_hash, senha)
            print(f"Senha válida: {senha_valida}")
            
            if senha_valida:
                session['user_id'] = usuario.id
                session['username'] = usuario.username
                session['tipo'] = usuario.tipo
                flash(f'Bem-vindo, {usuario.username}!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Senha incorreta!', 'error')
        else:
            print(f"Usuário não encontrado: {username}")
            flash('Usuário não encontrado!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('index'))

@app.route('/perfil')
@login_required
def perfil():
    usuario = Usuario.query.get(session['user_id'])
    return render_template('perfil.html', usuario=usuario)

@app.route('/cadastrar_unidade', methods=['GET', 'POST'])
def cadastrar_unidade():
    if request.method == 'POST':
        try:
            unidade = Unidade(
                numero=request.form['numero'],
                bloco=request.form['bloco'],
                tipo=request.form['tipo'],
                vagas_garagem=int(request.form['vagas_garagem'])
            )
            db.session.add(unidade)
            db.session.commit()
            flash('Unidade cadastrada com sucesso!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Erro ao cadastrar unidade: {str(e)}', 'error')
    
    return render_template('cadastrar_unidade.html')

@app.route('/cadastrar_morador', methods=['GET', 'POST'])
def cadastrar_morador():
    if request.method == 'POST':
        try:
            morador = Morador(
                nome=request.form['nome'],
                cpf=request.form['cpf'],
                telefone=request.form['telefone'],
                email=request.form['email'],
                tipo=request.form['tipo'],
                unidade_id=int(request.form['unidade_id'])
            )
            db.session.add(morador)
            db.session.commit()
            flash('Morador cadastrado com sucesso!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Erro ao cadastrar morador: {str(e)}', 'error')
    
    unidades = Unidade.query.all()
    return render_template('cadastrar_morador.html', unidades=unidades)

@app.route('/unidades')
def listar_unidades():
    unidades = Unidade.query.all()
    return render_template('unidades.html', unidades=unidades)

@app.route('/moradores')
def listar_moradores():
    moradores = Morador.query.join(Unidade).all()
    return render_template('moradores.html', moradores=moradores)

@app.route('/api/unidades')
def api_unidades():
    unidades = Unidade.query.all()
    return jsonify([{
        'id': u.id,
        'numero': u.numero,
        'bloco': u.bloco,
        'tipo': u.tipo,
        'vagas_garagem': u.vagas_garagem
    } for u in unidades])

@app.route('/api/moradores')
def api_moradores():
    moradores = Morador.query.join(Unidade).all()
    return jsonify([{
        'id': m.id,
        'nome': m.nome,
        'cpf': m.cpf,
        'telefone': m.telefone,
        'email': m.email,
        'tipo': m.tipo,
        'unidade': f"{m.unidade.bloco} - {m.unidade.numero}"
    } for m in moradores])

@app.route('/deletar_unidade/<int:unidade_id>', methods=['POST'])
def deletar_unidade(unidade_id):
    try:
        unidade = Unidade.query.get_or_404(unidade_id)
        
        if unidade.moradores:
            flash('Não é possível deletar unidade que possui moradores cadastrados!', 'error')
            return redirect(url_for('listar_unidades'))
        
        db.session.delete(unidade)
        db.session.commit()
        flash('Unidade removida com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao remover unidade: {str(e)}', 'error')
    
    return redirect(url_for('listar_unidades'))

@app.route('/deletar_morador/<int:morador_id>', methods=['POST'])
def deletar_morador(morador_id):
    try:
        morador = Morador.query.get_or_404(morador_id)
        db.session.delete(morador)
        db.session.commit()
        flash('Morador removido com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao remover morador: {str(e)}', 'error')
    
    return redirect(url_for('listar_moradores'))

@app.route('/cadastrar_visitante', methods=['GET', 'POST'])
@login_required
def cadastrar_visitante():
    usuario = Usuario.query.get(session['user_id'])
    
    if request.method == 'POST':
        try:
            unidade_id = int(request.form['unidade_id'])
            
            if usuario.tipo == 'Morador' and usuario.morador.unidade_id != unidade_id:
                flash('Você só pode cadastrar visitantes para sua própria unidade!', 'error')
                return redirect(url_for('cadastrar_visitante'))
            
            visitante = Visitante(
                nome=request.form['nome'],
                cpf=request.form['cpf'],
                telefone=request.form['telefone'],
                unidade_id=unidade_id,
                observacoes=request.form.get('observacoes', '')
            )
            db.session.add(visitante)
            db.session.commit()
            flash('Visitante cadastrado com sucesso!', 'success')
            return redirect(url_for('listar_visitantes'))
        except Exception as e:
            flash(f'Erro ao cadastrar visitante: {str(e)}', 'error')
    
    if usuario.tipo == 'Admin':
        unidades = Unidade.query.all()
    else:
        unidades = Unidade.query.filter_by(id=usuario.morador.unidade_id).all()
    
    return render_template('cadastrar_visitante.html', unidades=unidades)

@app.route('/visitantes')
@login_required
def listar_visitantes():
    usuario = Usuario.query.get(session['user_id'])
    
    if usuario.tipo == 'Admin':
        visitantes = Visitante.query.order_by(Visitante.data_entrada.desc()).all()
    else:
        visitantes = Visitante.query.filter_by(unidade_id=usuario.morador.unidade_id).order_by(Visitante.data_entrada.desc()).all()
    
    total_visitantes = len(visitantes)
    visitantes_ativos = len([v for v in visitantes if v.data_saida is None])
    visitantes_finalizados = len([v for v in visitantes if v.data_saida is not None])
    
    from datetime import datetime, date
    hoje = date.today()
    visitantes_hoje = len([v for v in visitantes if v.data_entrada.date() == hoje])
    
    return render_template('visitantes.html', 
                         visitantes=visitantes,
                         total_visitantes=total_visitantes,
                         visitantes_ativos=visitantes_ativos,
                         visitantes_finalizados=visitantes_finalizados,
                         visitantes_hoje=visitantes_hoje)

@app.route('/registrar_saida/<int:visitante_id>', methods=['POST'])
@login_required
def registrar_saida(visitante_id):
    try:
        visitante = Visitante.query.get_or_404(visitante_id)
        visitante.data_saida = datetime.utcnow()
        db.session.commit()
        flash('Saída registrada com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao registrar saída: {str(e)}', 'error')
    
    return redirect(url_for('listar_visitantes'))

@app.route('/cadastrar_multa', methods=['GET', 'POST'])
@admin_required
def cadastrar_multa():
    if request.method == 'POST':
        try:
            from datetime import datetime
            data_vencimento = datetime.strptime(request.form['data_vencimento'], '%Y-%m-%d').date()
            
            multa = Multa(
                morador_id=int(request.form['morador_id']),
                valor=float(request.form['valor']),
                descricao=request.form['descricao'],
                data_vencimento=data_vencimento
            )
            db.session.add(multa)
            db.session.commit()
            flash('Multa cadastrada com sucesso!', 'success')
            return redirect(url_for('listar_multas'))
        except Exception as e:
            flash(f'Erro ao cadastrar multa: {str(e)}', 'error')
    
    moradores = Morador.query.all()
    return render_template('cadastrar_multa.html', moradores=moradores)

@app.route('/multas')
@login_required
def listar_multas():
    usuario = Usuario.query.get(session['user_id'])
    
    if usuario.tipo == 'Admin':
        multas = Multa.query.order_by(Multa.data_vencimento.desc()).all()
    else:
        multas = Multa.query.filter_by(morador_id=usuario.morador_id).order_by(Multa.data_vencimento.desc()).all()
    
    return render_template('multas.html', multas=multas)

@app.route('/pagar_multa/<int:multa_id>', methods=['POST'])
@login_required
def pagar_multa(multa_id):
    try:
        multa = Multa.query.get_or_404(multa_id)
        multa.status = 'Pago'
        multa.data_pagamento = datetime.utcnow().date()
        db.session.commit()
        flash('Multa paga com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao pagar multa: {str(e)}', 'error')
    
    return redirect(url_for('listar_multas'))

@app.route('/reservas')
@login_required
def listar_reservas():
    usuario = Usuario.query.get(session['user_id'])
    
    if usuario.tipo == 'Admin':
        reservas = Reserva.query.order_by(Reserva.data.desc(), Reserva.horario_inicio).all()
    else:
        reservas = Reserva.query.filter_by(morador_id=usuario.morador_id).order_by(Reserva.data.desc(), Reserva.horario_inicio).all()
    
    return render_template('reservas.html', reservas=reservas, usuario=usuario)

@app.route('/cadastrar_reserva', methods=['GET', 'POST'])
@login_required
def cadastrar_reserva():
    usuario = Usuario.query.get(session['user_id'])
    
    if request.method == 'POST':
        try:
            area = request.form['area'].strip()
            data_reserva = datetime.strptime(request.form['data'], '%Y-%m-%d').date()
            horario_inicio = datetime.strptime(request.form['horario_inicio'], '%H:%M').time()
            horario_fim = datetime.strptime(request.form['horario_fim'], '%H:%M').time()
            observacoes = request.form.get('observacoes', '').strip()
            
            if horario_fim <= horario_inicio:
                flash('O horário de término deve ser posterior ao horário de início.', 'error')
                return redirect(url_for('cadastrar_reserva'))
            
            if usuario.tipo == 'Admin':
                morador_id = int(request.form['morador_id'])
            else:
                morador_id = usuario.morador_id
            
            conflito = Reserva.query.filter(
                Reserva.area == area,
                Reserva.data == data_reserva,
                Reserva.status.notin_(['Cancelada', 'Rejeitada'])
            ).filter(
                and_(Reserva.horario_inicio < horario_fim, Reserva.horario_fim > horario_inicio)
            ).first()
            
            if conflito:
                flash('Já existe uma reserva aprovada ou pendente para este período.', 'error')
                return redirect(url_for('cadastrar_reserva'))
            
            reserva = Reserva(
                morador_id=morador_id,
                area=area,
                data=data_reserva,
                horario_inicio=horario_inicio,
                horario_fim=horario_fim,
                observacoes=observacoes,
                status='Pendente' if usuario.tipo != 'Admin' else request.form.get('status', 'Pendente')
            )
            db.session.add(reserva)
            db.session.commit()
            flash('Reserva cadastrada com sucesso!', 'success')
            return redirect(url_for('listar_reservas'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar reserva: {str(e)}', 'error')
    
    if usuario.tipo == 'Admin':
        moradores = Morador.query.order_by(Morador.nome).all()
    else:
        moradores = [usuario.morador]
    
    return render_template('cadastrar_reserva.html', usuario=usuario, moradores=moradores)

@app.route('/reservas/<int:reserva_id>/status', methods=['POST'])
@admin_required
def atualizar_status_reserva(reserva_id):
    reserva = Reserva.query.get_or_404(reserva_id)
    novo_status = request.form.get('status')
    status_validos = ['Pendente', 'Aprovada', 'Rejeitada', 'Cancelada']
    
    if novo_status not in status_validos:
        flash('Status inválido para reserva.', 'error')
        return redirect(url_for('listar_reservas'))
    
    try:
        reserva.status = novo_status
        db.session.commit()
        flash('Status da reserva atualizado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar status da reserva: {str(e)}', 'error')
    
    return redirect(url_for('listar_reservas'))

@app.route('/reservas/<int:reserva_id>/cancelar', methods=['POST'])
@login_required
def cancelar_reserva(reserva_id):
    reserva = Reserva.query.get_or_404(reserva_id)
    usuario = Usuario.query.get(session['user_id'])
    
    if usuario.tipo != 'Admin' and reserva.morador_id != usuario.morador_id:
        flash('Você não tem permissão para cancelar esta reserva.', 'error')
        return redirect(url_for('listar_reservas'))
    
    try:
        reserva.status = 'Cancelada'
        db.session.commit()
        flash('Reserva cancelada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao cancelar reserva: {str(e)}', 'error')
    
    return redirect(url_for('listar_reservas'))

@app.route('/funcionarios')
@admin_required
def listar_funcionarios():
    funcionarios = Funcionario.query.order_by(Funcionario.nome).all()
    ativos = sum(1 for f in funcionarios if f.ativo)
    return render_template('funcionarios.html', funcionarios=funcionarios, ativos=ativos, total=len(funcionarios))

@app.route('/cadastrar_funcionario', methods=['GET', 'POST'])
@admin_required
def cadastrar_funcionario():
    if request.method == 'POST':
        try:
            nome = request.form['nome'].strip()
            cargo = request.form['cargo'].strip()
            telefone = request.form.get('telefone', '').strip() or None
            email = request.form.get('email', '').strip() or None
            turno = request.form.get('turno', '').strip() or None
            observacoes = request.form.get('observacoes', '').strip() or None
            data_admissao_str = request.form.get('data_admissao')
            data_admissao = datetime.strptime(data_admissao_str, '%Y-%m-%d').date() if data_admissao_str else datetime.utcnow().date()
            ativo = request.form.get('ativo') == 'on'
            
            funcionario = Funcionario(
                nome=nome,
                cargo=cargo,
                telefone=telefone,
                email=email,
                turno=turno,
                observacoes=observacoes,
                data_admissao=data_admissao,
                ativo=ativo
            )
            db.session.add(funcionario)
            db.session.commit()
            flash('Funcionário cadastrado com sucesso!', 'success')
            return redirect(url_for('listar_funcionarios'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar funcionário: {str(e)}', 'error')
    
    return render_template('cadastrar_funcionario.html')

@app.route('/funcionarios/<int:funcionario_id>/editar', methods=['GET', 'POST'])
@admin_required
def editar_funcionario(funcionario_id):
    funcionario = Funcionario.query.get_or_404(funcionario_id)
    
    if request.method == 'POST':
        try:
            funcionario.nome = request.form['nome'].strip()
            funcionario.cargo = request.form['cargo'].strip()
            funcionario.telefone = request.form.get('telefone', '').strip() or None
            funcionario.email = request.form.get('email', '').strip() or None
            funcionario.turno = request.form.get('turno', '').strip() or None
            funcionario.observacoes = request.form.get('observacoes', '').strip() or None
            data_admissao_str = request.form.get('data_admissao')
            if data_admissao_str:
                funcionario.data_admissao = datetime.strptime(data_admissao_str, '%Y-%m-%d').date()
            funcionario.ativo = request.form.get('ativo') == 'on'
            
            db.session.commit()
            flash('Funcionário atualizado com sucesso!', 'success')
            return redirect(url_for('listar_funcionarios'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar funcionário: {str(e)}', 'error')
    
    return render_template('editar_funcionario.html', funcionario=funcionario)

@app.route('/funcionarios/<int:funcionario_id>/status', methods=['POST'])
@admin_required
def alterar_status_funcionario(funcionario_id):
    funcionario = Funcionario.query.get_or_404(funcionario_id)
    try:
        funcionario.ativo = not funcionario.ativo
        db.session.commit()
        flash('Status do funcionário atualizado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar status do funcionário: {str(e)}', 'error')
    
    return redirect(url_for('listar_funcionarios'))

@app.route('/funcionarios/<int:funcionario_id>/excluir', methods=['POST'])
@admin_required
def excluir_funcionario(funcionario_id):
    funcionario = Funcionario.query.get_or_404(funcionario_id)
    try:
        db.session.delete(funcionario)
        db.session.commit()
        flash('Funcionário removido com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao remover funcionário: {str(e)}', 'error')
    
    return redirect(url_for('listar_funcionarios'))

@app.route('/notificacoes')
@login_required
def listar_notificacoes():
    usuario = Usuario.query.get(session['user_id'])
    
    if usuario.tipo == 'Admin':
        notificacoes_query = Notificacao.query.order_by(Notificacao.data_envio.desc())
    else:
        notificacoes_query = Notificacao.query.filter(
            or_(Notificacao.morador_id == None, Notificacao.morador_id == usuario.morador_id)
        ).order_by(Notificacao.data_envio.desc())
    
    notificacoes = notificacoes_query.all()
    
    leituras_usuario = {
        leitura.notificacao_id
        for leitura in NotificacaoLeitura.query.filter_by(usuario_id=usuario.id).all()
    }
    notificacoes_nao_lidas_ids = [n.id for n in notificacoes if n.id not in leituras_usuario]
    total_nao_lidas = len(notificacoes_nao_lidas_ids)
    
    if total_nao_lidas:
        for notificacao_id in notificacoes_nao_lidas_ids:
            db.session.add(NotificacaoLeitura(
                notificacao_id=notificacao_id,
                usuario_id=usuario.id
            ))
        db.session.commit()
    
    return render_template(
        'notificacoes.html',
        notificacoes=notificacoes,
        usuario=usuario,
        notificacoes_nao_lidas_pendentes=total_nao_lidas,
        notificacoes_ids_nao_lidas=notificacoes_nao_lidas_ids
    )

@app.route('/cadastrar_notificacao', methods=['GET', 'POST'])
@admin_required
def cadastrar_notificacao():
    if request.method == 'POST':
        try:
            titulo = request.form['titulo'].strip()
            mensagem = request.form['mensagem'].strip()
            destinatario = request.form.get('destinatario')
            morador_id = None if destinatario == 'todos' else int(destinatario)
            autor_id = session['user_id']
            
            notificacao = Notificacao(
                titulo=titulo,
                mensagem=mensagem,
                morador_id=morador_id,
                autor_id=autor_id
            )
            db.session.add(notificacao)
            db.session.commit()
            flash('Notificação enviada com sucesso!', 'success')
            return redirect(url_for('listar_notificacoes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao enviar notificação: {str(e)}', 'error')
    
    moradores = Morador.query.order_by(Morador.nome).all()
    return render_template('cadastrar_notificacao.html', moradores=moradores)

@app.route('/notificacoes/<int:notificacao_id>/excluir', methods=['POST'])
@admin_required
def excluir_notificacao(notificacao_id):
    notificacao = Notificacao.query.get_or_404(notificacao_id)
    try:
        db.session.delete(notificacao)
        db.session.commit()
        flash('Notificação removida com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao remover notificação: {str(e)}', 'error')
    
    return redirect(url_for('listar_notificacoes'))

def obter_conversas(usuario):
    mensagens_relacionadas = ChatMensagem.query.filter(
        or_(ChatMensagem.remetente_id == usuario.id, ChatMensagem.destinatario_id == usuario.id)
    ).order_by(ChatMensagem.enviada_em.desc()).all()
    
    conversas_temp = {}
    usuarios_ids = set()
    
    for mensagem in mensagens_relacionadas:
        outro_id = mensagem.destinatario_id if mensagem.remetente_id == usuario.id else mensagem.remetente_id
        if outro_id == usuario.id:
            continue
        usuarios_ids.add(outro_id)
        existente = conversas_temp.get(outro_id)
        if not existente or mensagem.enviada_em > existente['ultima_data']:
            conversas_temp[outro_id] = {
                'ultima_mensagem': mensagem,
                'ultima_data': mensagem.enviada_em
            }
    
    usuarios_map = {}
    if usuarios_ids:
        usuarios_map = {
            u.id: u for u in Usuario.query.filter(Usuario.id.in_(usuarios_ids)).all()
        }
    
    nao_lidas_por_usuario = {
        row.remetente_id: row.total
        for row in db.session.query(
            ChatMensagem.remetente_id,
            db.func.count(ChatMensagem.id).label('total')
        ).filter(
            ChatMensagem.destinatario_id == usuario.id,
            ChatMensagem.lida_em == None
        ).group_by(ChatMensagem.remetente_id)
    }
    
    conversas = []
    for outro_id, dados in conversas_temp.items():
        outro_usuario = usuarios_map.get(outro_id)
        if not outro_usuario:
            continue
        conversas.append({
            'usuario': outro_usuario,
            'ultima_mensagem': dados['ultima_mensagem'],
            'ultima_data': dados['ultima_data'],
            'nao_lidas': nao_lidas_por_usuario.get(outro_id, 0)
        })
    
    conversas.sort(key=lambda c: c['ultima_data'] or datetime.min, reverse=True)
    return conversas

def usuarios_disponiveis_para_chat(usuario):
    consulta = Usuario.query.filter(Usuario.id != usuario.id, Usuario.ativo == True)
    if usuario.tipo != 'Admin':
        consulta = consulta.filter(Usuario.tipo == 'Admin')
    return consulta.order_by(Usuario.username).all()

def validar_destinatario_chat(usuario, destinatario):
    if destinatario.id == usuario.id:
        return False
    if not destinatario.ativo:
        return False
    if usuario.tipo == 'Admin':
        return True
    return destinatario.tipo == 'Admin'

@app.route('/chat')
@login_required
def chat_home():
    usuario = Usuario.query.get(session['user_id'])
    if not usuario:
        flash('Sessão inválida. Faça login novamente.', 'error')
        return redirect(url_for('logout'))
    
    destinatario_param = request.args.get('destinatario', type=int)
    if destinatario_param:
        return redirect(url_for('chat_conversa', destinatario_id=destinatario_param))
    
    conversas = obter_conversas(usuario)
    usuarios_disponiveis = usuarios_disponiveis_para_chat(usuario)
    
    return render_template(
        'chat.html',
        usuario=usuario,
        conversas=conversas,
        usuarios_disponiveis=usuarios_disponiveis,
        destinatario=None,
        mensagens=[]
    )

@app.route('/chat/<int:destinatario_id>', methods=['GET', 'POST'])
@login_required
def chat_conversa(destinatario_id):
    usuario = Usuario.query.get(session['user_id'])
    destinatario = Usuario.query.get_or_404(destinatario_id)
    
    if not usuario:
        flash('Sessão inválida. Faça login novamente.', 'error')
        return redirect(url_for('logout'))
    
    if not validar_destinatario_chat(usuario, destinatario):
        flash('Você não tem permissão para conversar com este usuário.', 'error')
        return redirect(url_for('chat_home'))
    
    if request.method == 'POST':
        mensagem_texto = request.form.get('mensagem', '').strip()
        if not mensagem_texto:
            flash('Digite uma mensagem antes de enviar.', 'error')
        else:
            try:
                mensagem = ChatMensagem(
                    remetente_id=usuario.id,
                    destinatario_id=destinatario.id,
                    mensagem=mensagem_texto
                )
                db.session.add(mensagem)
                db.session.commit()
                flash('Mensagem enviada!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao enviar mensagem: {str(e)}', 'error')
        return redirect(url_for('chat_conversa', destinatario_id=destinatario.id))
    
    atualizados = ChatMensagem.query.filter_by(
        remetente_id=destinatario.id,
        destinatario_id=usuario.id,
        lida_em=None
    ).update(
        {ChatMensagem.lida_em: datetime.utcnow()},
        synchronize_session=False
    )
    if atualizados:
        db.session.commit()
    
    conversas = obter_conversas(usuario)
    if destinatario.id not in [c['usuario'].id for c in conversas]:
        conversas.append({
            'usuario': destinatario,
            'ultima_mensagem': None,
            'ultima_data': None,
            'nao_lidas': 0
        })
    conversas.sort(key=lambda c: c['ultima_data'] or datetime.min, reverse=True)
    
    mensagens = ChatMensagem.query.filter(
        or_(
            and_(ChatMensagem.remetente_id == usuario.id, ChatMensagem.destinatario_id == destinatario.id),
            and_(ChatMensagem.remetente_id == destinatario.id, ChatMensagem.destinatario_id == usuario.id)
        )
    ).order_by(ChatMensagem.enviada_em.asc()).all()
    
    usuarios_disponiveis = usuarios_disponiveis_para_chat(usuario)
    
    return render_template(
        'chat.html',
        usuario=usuario,
        conversas=conversas,
        usuarios_disponiveis=usuarios_disponiveis,
        destinatario=destinatario,
        mensagens=mensagens
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
