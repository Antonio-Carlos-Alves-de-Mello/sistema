from flask import render_template, redirect, url_for, send_from_directory, flash, request,session
from helpers import FormularioProdutos
from app import app, db 
from models import Produtos

@app.route('/sistema/produtos')
def index():
   termo_busca = request.args.get('search', '', type=str).strip()
   consulta = db.session.query(
       Produtos.id,
       Produtos.nome
   )
   if termo_busca:
       consulta = consulta.filter(
       db.or_(
           Produtos.nome.ilike(f"%{termo_busca}%")
       )
    )
   Lista_Produtos = consulta.order_by(Produtos.nome).all()
   return render_template('produto/produtos.html' , Lista_Produtos=Lista_Produtos, termo_busca=termo_busca)

@app.route('/sistema/produtos/novo')
def novo():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('novo')))
    form = FormularioProdutos()
    return render_template('produto/novo.html', form=form)

@app.route('/sistema/produtos/criar', methods=['POST',])
def criar():
    form = FormularioProdutos()
    if not form.validate_on_submit():
        return redirect(url_for('novo'))
    
    nome = form.nome.data
    produto = Produtos.query.filter_by(nome=nome).first
    
    if  not produto:
        flash(' Já cadatrado')
        return redirect(url_for('index'))
    novo_produto = Produtos(nome=nome)
    
    db.session.add(novo_produto)
    db.session.commit()
    flash('Produto cadastrado')
    return redirect(url_for('index'))


@app.route('/sisstema/produtos/editar/<int:id>')
def editar(id):
    produto = Produtos.query.filter_by(id=id).first()
    form=FormularioProdutos()
    form.nome.data = produto.nome
    return render_template('produto/editar.html', id=id ,form=form)

@app.route('/sistema/produtos/atualizar', methods=['POST',])
def atualizar():
    form=FormularioProdutos(request.form)
    if form.validate_on_submit():
        produto =Produtos.query.filter_by(id=request.form['id']).first()
        produto.nome = form.nome.data
        db.session.add(produto)
        db.session.commit()
        flash(' Atualizado com sucesso')
        return redirect(url_for('index'))

@app.route('/sistema/produtos/deletar/<int:id>')
def deletar(id):
    Produtos.query.filter_by(id=id).delete()
    db.session.commit()
    flash('Produto apagado com sucesso')
    return redirect(url_for('index'))
        
