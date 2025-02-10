from flask import render_template, redirect, url_for, flash, request, session
from helpers import FormularioContatos
from app import app, db 
from models import Contatos, Lojas, setores


@app.route('/sistema/contatos')
def index_Contatos():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('index_Contatos')))
    # Obtém o termo de busca a partir dos parâmetros da URL
    termo_busca = request.args.get('search', '', type=str).strip()
    
    consulta = db.session.query(
            Contatos.idcontatos,
            Lojas.fantasia,  # Campo da tabela Lojas
            setores.setor,   # Campo da tabela setores
            Contatos.telefone,
            Contatos.tipo,
            Contatos.contato
    ).join(Contatos, Contatos.cnpj == Lojas.cnpj
    ).join(setores, Contatos.idsetor == setores.id)  # Junção entre Contatos e setores
       
    if termo_busca:
        consulta = consulta.filter(
            db.or_(
                Lojas.fantasia.ilike(f"%{termo_busca}%"),
                setores.setor.ilike(f"%{termo_busca}%"),
                Contatos.tipo.ilike(f"%{termo_busca}%"),
                Contatos.contato.ilike(f"%{termo_busca}%")
           )
        )
    Lista_Contatos = consulta.order_by(Lojas.fantasia).all()
    
    return render_template('contatos/contatos.html', Lista_contatos=Lista_Contatos, termo_busca=termo_busca)



@app.route('/sistema/contato/novo')
def Novo_contato():
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        return redirect(url_for('login', proxima=url_for('Novo_contato')))
    
    form = FormularioContatos()
    form.idsetor.choices = [(setor.id, setor.setor) for setor in setores.query.all()]
    form.cnpj.choices = [(loja.cnpj, loja.fantasia) for loja in Lojas.query.all()]
    #print("Choices cnpj:", form.cnpj.choices)
    #print("Choices idsetor:", form.idsetor.choices)

    if request.method == 'POST':
       # print("Dados enviados pelo formulário:", request.form)
        if not form.validate_on_submit():
           # print("Erros de validação:", form.errors)
            flash('Erro ao validar o formulário.', 'error')
            return render_template('contatos/novo.html', form=form)
    
    return render_template('contatos/novo.html', form=form)


@app.route('/sistema/contato/criar', methods=['POST'])
def Criar_contato():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('Criar_contato')))
    form = FormularioContatos()
    
    # Preencher choices (necessário para validação correta no POST)
    form.cnpj.choices = [(loja.cnpj, loja.razao) for loja in Lojas.query.all()]
    form.idsetor.choices = [(setor.id, setor.setor) for setor in setores.query.all()]
    
    if not form.validate_on_submit():
        #print("Erros de validação:", form.errors)
        flash('Erro ao validar o formulário.', 'error')
        return render_template('contatos/novo.html', form=form)

    # Capturar apenas os valores selecionados
    cnpj_selecionado = form.cnpj.data  # Este será o valor selecionado
    idsetor_selecionado = form.idsetor.data  # Este será o valor selecionado

    #print(f"Valor selecionado - CNPJ: {cnpj_selecionado}, ID Setor: {idsetor_selecionado}")

    # Criar novo contato
    novocontato = Contatos(
        cnpj=cnpj_selecionado,
        idsetor=idsetor_selecionado,
        telefone=form.telefone.data,
        tipo=form.tipo.data,
        contato=form.contato.data
    )
    db.session.add(novocontato)
    db.session.commit()
    flash('Contato cadastrado com sucesso.', 'success')
    return redirect(url_for('index_Contatos'))


@app.route('/sistema/contato/editar/<int:id>', methods=['GET', 'POST'])
def Editar_contato(id):
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        return redirect(url_for('login', proxima=url_for('Editar_contato')))
    contato_editado = Contatos.query.filter_by(idcontatos=id).first()
    if not contato_editado:
        flash('Contato não encontrado.', 'error')
        return redirect(url_for('index_Contatos'))

    form = FormularioContatos()
    form.idsetor.choices = [(setor.id, setor.setor) for setor in setores.query.all()]
    form.cnpj.choices = [(loja.cnpj, loja.razao) for loja in Lojas.query.all()]
    
    if request.method == 'POST' and form.validate_on_submit():
        contato_editado.cnpj = form.cnpj.data
        contato_editado.idsetor = form.idsetor.data
        contato_editado.telefone = form.telefone.data
        contato_editado.tipo = form.tipo.data
        contato_editado.contato = form.contato.data
        db.session.commit()
        flash('Contato atualizado com sucesso.', 'success')
        return redirect(url_for('index_Contatos'))
    
    # Pré-preencher o formulário com os dados do contato existente
    form.cnpj.data = contato_editado.cnpj
    form.idsetor.data = contato_editado.idsetor
    form.telefone.data = contato_editado.telefone
    form.tipo.data = contato_editado.tipo
    form.contato.data = contato_editado.contato
    return render_template('contatos/editar.html', id=id, form=form)


@app.route('/sistema/contato/atualizar', methods=['POST'])
def Atualizar_contato():
    form = FormularioContatos()
    form.idsetor.choices = [(setor.id, setor.setor) for setor in setores.query.all()]
    form.cnpj.choices = [(loja.cnpj, loja.fantasia) for loja in Lojas.query.all()]
    if not form.validate_on_submit():
        print("Erros de validação:", form.errors)
        flash('Erro ao validar o formulário.', 'error')
        return redirect(url_for('index_Contatos'))
    
    contato_id = request.form.get('id')
    contato_atualizado = Contatos.query.filter_by(idcontatos=contato_id).first()
    if not contato_atualizado:
        
        flash('Contato não encontrado.1', 'error')
        return redirect(url_for('index_Contatos'))
    
    contato_atualizado.cnpj = form.cnpj.data
    contato_atualizado.idsetor = form.idsetor.data
    contato_atualizado.telefone = form.telefone.data
    contato_atualizado.tipo = form.tipo.data
    contato_atualizado.contato = form.contato.data
    db.session.commit()
    flash('Contato atualizado com sucesso.', 'success')
    return redirect(url_for('index_Contatos'))


@app.route('/sistema/contato/deletar/<int:id>', methods=['GET'])
def Excluir_contato(id):
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        return redirect(url_for('login', proxima=url_for('Editar_contato')))
    contato = Contatos.query.filter_by(idcontatos=id).first()
    if not contato:
        flash('Contato não encontrado.', 'error')
        return redirect(url_for('index_Contatos'))
    else:
        db.session.delete(contato)
        db.session.commit()
        flash('Contato apagado com sucesso.', 'success')
        return redirect(url_for('index_Contatos'))
