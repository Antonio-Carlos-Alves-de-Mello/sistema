from flask import render_template, redirect, url_for, send_from_directory, flash, request, session
from helpers import FormularioFornecedores
from app import app, db 
from models import Fornecedores

@app.route('/sistema/fornecedores')
def index_fornecedores():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('index_fornecedores')))
    
    termo_busca = request.args.get('search', '', type=str).strip()
    consulta = db.session.query(
        Fornecedores.nome,
        Fornecedores.nome_contato,
        Fornecedores.site,
        Fornecedores.telefone
    )
    if termo_busca:
        consulta = consulta.filter(
            db.or_(
            Fornecedores.nome.ilike(f"%{termo_busca}%"),
            Fornecedores.nome_contato.ilike(f"%{termo_busca}%"),
            Fornecedores.site.ilike(f"%{termo_busca}%"),
            Fornecedores.telefone.ilike(f"%{termo_busca}%")
            )
        )
        
    Lista_Fornecedores = Fornecedores.query.order_by(Fornecedores.id)
    return render_template('fornecedor/fornecedores.html', Lista_Fornecedores=Lista_Fornecedores)


@app.route('/sistema/fornecedores/novo')
def novo_fornecedor():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('novo')))
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
    print(formecedor)

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
    fornecedor = Fornecedores.query.get_or_404(id)  # Garante que o fornecedor existe
    form = FormularioFornecedores(obj=fornecedor)  # Preenche o formulário com os dados existentes
    return render_template('fornecedor/editar.html', id=id, form=form)

@app.route('/sistema/fornecedor/atualizar', methods=['POST'])
def atualizar_Fornecedor():
    form = FormularioFornecedores(request.form)

    if form.validate_on_submit():
        fornecedor = Fornecedores.query.get(request.form.get('id'))  # Busca pelo ID no form

        if fornecedor:
            fornecedor.nome = form.nome.data
            fornecedor.nome_contato = form.contato.data
            fornecedor.site = form.site.data
            fornecedor.telefone = form.telefone.data

            db.session.commit()
            flash('Fornecedor atualizado com sucesso!', 'success')
            return redirect(url_for('index_fornecedores'))  # Certifique-se de que esta rota existe
        else:
            flash('Fornecedor não encontrado!', 'danger')
            return redirect(url_for('index_fornecedores'))

    flash('Erro ao atualizar fornecedor. Verifique os dados!', 'danger')
    return redirect(url_for('editar_Fornecedor', id=request.form.get('id')))


@app.route('/sistema/fornecedore/deletar/<int:id>')
def deletar_fornecedor(id):
    Fornecedores.query.filter_by(id=id).delete()
    db.session.commit()
    flash('Fornecedor apagado com sucesso.')
    return redirect(url_for('index_fornecedores'))