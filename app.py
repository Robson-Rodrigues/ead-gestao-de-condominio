from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
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
        
        return render_template('index.html', 
                             unidades=unidades, 
                             moradores=moradores,
                             visitantes_ativos=visitantes_ativos,
                             multas_pendentes=multas_pendentes,
                             valor_multas=valor_multas)
    
    else:
        moradores_unidade = Morador.query.filter_by(unidade_id=usuario.morador.unidade_id).count()
        visitantes_ativos = Visitante.query.filter_by(unidade_id=usuario.morador.unidade_id, data_saida=None).count()
        multas_abertas = Multa.query.filter_by(morador_id=usuario.morador_id, status='Pendente').count()
        valor_multas = db.session.query(db.func.sum(Multa.valor)).filter_by(morador_id=usuario.morador_id, status='Pendente').scalar() or 0
        
        return render_template('index.html', 
                             unidades=unidades, 
                             moradores=moradores,
                             moradores_unidade=moradores_unidade,
                             visitantes_ativos=visitantes_ativos,
                             multas_abertas=multas_abertas,
                             valor_multas=valor_multas)

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
