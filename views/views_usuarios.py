from app import app, db
from models import Usuarios
from helpers import FormularioUsuario, FormularioDeCadastroUsuarios
from flask import render_template, redirect, url_for, flash, request,session
import hashlib
from urllib.parse import urlparse, urljoin

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@app.route('/sistema/login')
def login():
    proxima = request.args.get('proxima')
    form = FormularioUsuario()
    return render_template('acesso/login.html', proxima=proxima, form=form)

@app.route('/autenticar', methods=['POST',])
def autenticar():
    
    form = FormularioUsuario(request.form)
    usuario_b = Usuarios.query.filter_by(email=form.email.data).first()

    if usuario_b and hashlib.sha256(form.senha.data.encode()).hexdigest() == usuario_b.senha:
        session['usuario_logado'] = usuario_b.nome
        proxima_pagina = request.form['proxima']
        if not is_safe_url(proxima_pagina):
            return redirect(url_for('index'))
        return redirect(proxima_pagina)
    else:
        flash("Usuário ou senha incorretos!")
        return redirect(url_for('login'))
    
@app.route('/logout')
def logout():
    if 'usuario_logado' in session:
        session.pop('usuario_logado', None)
        flash('Logout efetuado com sucesso!')
    return redirect(url_for('index'))

@app.route('/sistema/usuario/novo')
def novo_usuario():
   form = FormularioDeCadastroUsuarios()
   return render_template('acesso/novo.html', form=form)

@app.route('/sistema/usuario/criar', methods=['POST',] )
def criar_usurio():
    form= FormularioDeCadastroUsuarios()
    if not form.validate_on_submit():
        return redirect(url_for('index'))
    
    nome = form.nome.data
    email = form.email.data
    senha = form.senha.data
    senha_H = hashlib.sha256(senha.encode()).hexdigest()

    nv_usuario = Usuarios.query.filter_by(email=email).first()

    if nv_usuario:
        flash('Este email já existe')
        return redirect(url_for('novo_usuario'))
    else:
        novo_usuario = Usuarios(nome=nome, email=email, senha=senha_H)
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Usuário cadastrado com sucesso')
        return redirect(url_for('novo_usuario'))
    
@app.route('/sistema/usuarios')
def index_usuarios():
    por_pagina = 5
    pagina_atual = request.args.get('page', 1, type=int)
    Lista_usuarios = Usuarios.query.order_by(Usuarios.nome).paginate(page=pagina_atual, per_page=por_pagina)
    return render_template('usuarios/usuarios.html', Lista_usuarios=Lista_usuarios)


@app.route('/sistema/usuario/editar')
def editar_usuario():
    pass