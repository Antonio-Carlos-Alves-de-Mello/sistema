from flask import render_template, redirect, url_for, send_from_directory, flash, request,session
from helpers import FormularioFornecedores
from app import app, db 
from models import Fornecedores

@app.route('/sistema/fornecedores')
def index_fornecedores():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('index_fornecedores')))
    # Obtém o termo de busca
    termo_busca = request.args.get('search', '', type=str).strip()
    
    try:
        # Construção da consulta inicial
        consulta = db.session.query(
            Fornecedores.id,
            Fornecedores.nome,
            Fornecedores.nome_contato,
            Fornecedores.site,
            Fornecedores.telefone
        )
        
        # Aplica filtro de busca se houver termo
        if termo_busca:
            consulta = consulta.filter(
                db.or_(
                    Fornecedores.nome.ilike(f"%{termo_busca}%"),
                    Fornecedores.nome_contato.ilike(f"%{termo_busca}%"),
                    Fornecedores.telefone.ilike(f"%{termo_busca}%"),
                    Fornecedores.site.ilike(f"%{termo_busca}%")
                )
            )
        
        # Ordena e executa a consulta
        Lista_Fornecedores = consulta.order_by(Fornecedores.nome).all()
    except Exception as e:
        # Captura erros e retorna mensagem amigável
        app.logger.error(f"Erro ao buscar fornecedores: {e}")
        flash("Erro ao carregar os fornecedores. Tente novamente mais tarde.")
        Lista_Fornecedores = []

    # Renderiza o template com os dados obtidos
    return render_template(
        'fornecedor/fornecedores.html',
        Lista_Fornecedores=Lista_Fornecedores,
        termo_busca=termo_busca
    )

@app.route('/sistema/fornecedores/novo')
def novo_fornecedor():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('index_fornecedores')))
    form = FormularioFornecedores()
    return render_template('fornecedor/novo.html', form=form)
    
@app.route('/sistema/fornecedores/criar', methods=['POST',])
def criar_fornrcedor():
    form = FormularioFornecedores()
    if not form.validate_on_submit():
        return redirect(url_for('novo_fornecedor'))
    
    nome = form.nome.data
    contato = form.contato.data
    site = form.site.data
    telefone = form.telefone.data
    formecedor = Fornecedores.query.filter_by(nome=nome).first
   

    if not formecedor:
        flash (' Já cadastrado')
        return redirect(url_for('index_fornecedores'))
    novo_fornecedor = Fornecedores(nome=nome, nome_contato=contato, site=site, telefone=telefone)

    db.session.add(novo_fornecedor)
    db.session.commit()
    flash('Fornecedor cadastrado')
    return redirect(url_for('index_fornecedores'))

@app.route('/sistema/fornecedor/editar/<int:id>')
def editar_Fornecedor(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('index_fornecedores')))
    fornecedor = Fornecedores.query.filter_by(id=id).first()
    form = FormularioFornecedores()
    form.nome.data = fornecedor.nome
    form.contato.data = fornecedor.nome_contato
    form.site.data = fornecedor.site
    form.telefone.data = fornecedor.telefone
    return render_template('fornecedor/editar.html', id=id, form=form)

@app.route('/sistema/fornecedor/atualizar', methods=['POST',])
def atualizar_Fornecedor():
    form = FormularioFornecedores(request.form)
    if form.validate_on_submit():
        fornecedor = Fornecedores.query.filter_by(id=request.form['id']).first()
        print(fornecedor)
        fornecedor.nome = form.nome.data
        fornecedor.nome_contato= form.contato.data
        fornecedor.site = form.site.data
        fornecedor.telefone = form.telefone.data
        db.session.add(fornecedor)
        db.session.commit()
        flash('Atualizado com sucesso')
        return redirect(url_for('index_fornecedores'))

@app.route('/sistema/fornecedore/deletar/<int:id>')
def deletar_fornecedor(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('index_fornecedores')))
    Fornecedores.query.filter_by(id=id).delete()
    db.session.commit()
    flash('Fornecedor apagado com sucesso.')
    return redirect(url_for('index_fornecedores'))