from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os

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
@app.route('/')
def index():
    unidades = Unidade.query.all()
    moradores = Morador.query.all()
    return render_template('index.html', unidades=unidades, moradores=moradores)

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
