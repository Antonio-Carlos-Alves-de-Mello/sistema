from flask import render_template, redirect, url_for, flash, request, session
from helpers import FormularioDeSetores
from app import app, db
from models import setores

@app.route('/sistema/setores')
def index_setores():
    termo_busca = request.args.get('search', '', type=str).strip()
    consulta = db.session.query(setores.id, setores.setor)
    
    if termo_busca:
        consulta = consulta.filter(
            setores.setor.ilike(f"%{termo_busca}%")
        )
    
    Lista_setores = consulta.order_by(setores.setor).all()
    return render_template('setores/setores.html', Lista_setores=Lista_setores, termo_busca=termo_busca)

@app.route('/sistema/setores/novo')
def novo_setores():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('novo_setores')))
    form = FormularioDeSetores()
    return render_template('setores/novo.html', form=form)

@app.route('/sistema/setore/criar', methods=['POST',])
def criar_setor():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login'))
    
    form = FormularioDeSetores(request.form)
    if not form.validate_on_submit():
        return redirect(url_for('novo_setores'))
    
    setor = form.setor.data
    consulta_setor = setores.query.filter_by(setor=setor).first()

    if consulta_setor:
        flash('Setor já existe')
        return redirect(url_for('index_setores'))
    
    try:
        setor_novo = setores(setor=setor)
        db.session.add(setor_novo)
        db.session.commit()
        flash('Setor criado com sucesso')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao criar setor: {e}')
    return redirect(url_for('index_setores'))

@app.route('/sistema/setores/editar/<int:id>')
def editar_setor(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login'))
    
    seto = setores.query.filter_by(id=id).first()
    if not seto:
        flash('Setor não encontrado')
        return redirect(url_for('index_setores'))
    
    form = FormularioDeSetores()
    form.setor.data = seto.setor
    return render_template('setores/editar.html', id=id, form=form)

@app.route('/sistema/setor/atualizar', methods=['POST',])
def atualizar_setor():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login'))
    
    form = FormularioDeSetores(request.form)
    if form.validate_on_submit():
        setor = setores.query.filter_by(id=request.form['id']).first()
        if setor:
            setor.setor = form.setor.data
            db.session.commit()
            flash('Atualizado com sucesso')
        else:
            flash('Setor não encontrado')
    return redirect(url_for('index_setores'))

@app.route('/sistema/setor/deletar/<int:id>')
def deletar_setor(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login'))
    
    try:
        setores.query.filter_by(id=id).delete()
        db.session.commit()
        flash('Setor apagado com sucesso')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao apagar setor: {e}')
    return redirect(url_for('index_setores'))
