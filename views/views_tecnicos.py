from flask import render_template, redirect, url_for, flash, request, session
from helpers import FormularioTecnicos
from app import app, db
from models import tecnicos


@app.route('/sistema/tecnicos')
def index_tecnico():
    por_pagina = 5
    pagina_atual = request.args.get('page', 1, type=int)
    Lista_tecnicos = tecnicos.query.order_by(tecnicos.nome).paginate(page=pagina_atual, per_page=por_pagina)
    return render_template('tecnicos/tecnicos.html', Lista_tecnicos=Lista_tecnicos)

@app.route('/sistema/tecnico/novo')
def novo_tecnico():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('novo_tecnico')))
    form = FormularioTecnicos()
    return render_template('tecnicos/novo.html', form=form)

@app.route('/sistema/tecnico/criar', methods=['POST',])
def criar_tecnico():
    form = FormularioTecnicos()
    if not form.validate_on_submit():
        return redirect(url_for('novo_tecnico'))
    
    nome = form.nome.data
    email = form.email.data

    if not email:
        flash('Ja Cadastrado')
        return redirect(url_for('index_tecnico'))
    novo_tecnico = tecnicos(nome=nome, email=email)

    db.session.add(novo_tecnico)
    db.session.commit()
    flash('técnico Inserido')
    return redirect(url_for('index_tecnico'))

@app.route('/sistema/tecnico/editar/<int:id>')
def editar_tecnico(id):
    tecnico = tecnicos.query.filter_by(id=id).first()
    form = FormularioTecnicos()
    form.nome.data = tecnico.nome
    form.email.data = tecnico.email
    return render_template('tecnicos/editar.html', id=id, form=form)

@app.route('/sistema/tecnico/deletar/<int:id>')
def deletar_tecnico(id):
    tecnicos.query.filter_by(id=id).delete()
    db.session.commit()
    flash('tecnico apagado')
    return redirect(url_for('index_tecnico'))
