from flask import jsonify, render_template, redirect, url_for,  flash, request,session,make_response
from config import PASSWORD, PORT, SMTP_SERVER, USERNAME
from datetime import date
from helpers import FormulariodePedidos
from app import app, db 
from models import RequisicaoMaterial, Lojas, Produtos
from envia_email import EmailHandler

@app.route('/sistema/pedidos')
def index_pedidos():
    termo_busca = request.args.get('search', '', type=str).strip()
    
    # Criação da consulta inicial
    consulta = db.session.query(
        RequisicaoMaterial.id,
        RequisicaoMaterial.cnpj,
        Lojas.fantasia,
        RequisicaoMaterial.numero_chamado,
        RequisicaoMaterial.id_material, 
        Produtos.nome,
        RequisicaoMaterial.quantidade,
        RequisicaoMaterial.solicitado_em,
        RequisicaoMaterial.observacao,
        db.case(
        (RequisicaoMaterial.entregue_em.is_(None), 'Não'),
        else_=RequisicaoMaterial.entregue_em
    ).label("entregue_em")
        
    ).join(Lojas, RequisicaoMaterial.cnpj == Lojas.cnpj) \
     .join(Produtos, RequisicaoMaterial.id_material == Produtos.id)
    
    # Filtro de busca se termo de busca estiver presente
    if termo_busca:
        consulta = consulta.filter(
            db.or_(
                Lojas.fantasia.ilike(f"%{termo_busca}%"),
                Produtos.nome.ilike(f"%{termo_busca}%"),
                RequisicaoMaterial.numero_chamado.ilike(f"%{termo_busca}%"),
                RequisicaoMaterial.solicitado_em.ilike(f"%{termo_busca}%")
            )
        )
    
    # Ordenação e execução da consulta
    lista_pedidos = consulta.order_by(Lojas.fantasia,RequisicaoMaterial.solicitado_em).all()
        
    # Renderização do template
    return render_template(
        'pedidos/pedidos.html', 
        lista_pedidos=lista_pedidos, 
        termo_busca=termo_busca
    )

@app.route('/sistema/pedidos/Apagar/<int:id>')
def apagar_pedido(id):
    RequisicaoMaterial.query.filter_by(id=id).delete()
    db.session.commit()
    flash('Pedido apagado com sucesso')
    return redirect(url_for('index_pedidos'))

@app.route('/sistema/pedido/novo', methods=['GET', 'POST'])
def novo_pedido():
    form = FormulariodePedidos()
    # Configurando opções para os campos de seleção
    form.cnpj.choices = [(loja.cnpj, loja.fantasia) for loja in Lojas.query.all()]
    form.id_produto.choices = [(produto.id, produto.nome) for produto in Produtos.query.all()]

    if form.validate_on_submit():
        # Processar dados do formulário
        novo_pedido = RequisicaoMaterial(
            cnpj=form.cnpj.data,
            numero_chamado=form.N_chamado.data,
            id_material=form.id_produto.data,
            quantidade=form.quantidade.data,
            solicitado_em=form.solicitado_em.data,
            observacao=form.observacao.data,
            entregue_em=form.entregue_em.data if form.entregue_em.data else None  # Garante que seja opcional
        )
        db.session.add(novo_pedido)
        db.session.commit()
        flash('Pedido criado com sucesso!', 'success')
        return redirect(url_for('index_pedidos'))

    return render_template('pedidos/novo.html', form=form)

@app.route('/sistema/pedido/editar/<int:id>', methods=['GET', 'POST'])
def editar_pedido(id):
    try:
        # Obter o pedido pelo ID
        editar = RequisicaoMaterial.query.filter(RequisicaoMaterial.id ==id).first()
        print(editar)
        if not editar:
            flash('Pedido não encontrado.', 'error')
            return redirect(url_for('index_pedidos'))
        
        # Instanciar o formulário
        form = FormulariodePedidos()
        
        # Preencher as opções do SelectField
        form.cnpj.choices = [(loja.cnpj, loja.fantasia) for loja in Lojas.query.all()]
        form.id_produto.choices = [(produto.id, produto.nome) for produto in Produtos.query.all()]
        
        if request.method == 'GET':
            # Preencher o formulário com os dados do pedido
            form.cnpj.data = editar.cnpj
            form.N_chamado.data = editar.numero_chamado
            form.id_produto.data = editar.id_material
            form.quantidade.data = editar.quantidade
            form.solicitado_em.data = editar.solicitado_em
            form.observacao.data = editar.observacao
            form.entregue_em.data = editar.entregue_em
            
            # Renderizar o template
            return render_template('pedidos/editar.html', id=id, form=form)
        
        # Manipulação do formulário no POST
        if form.validate_on_submit():
            # Atualizar os dados do pedido
            editar.cnpj = form.cnpj.data
            editar.numero_chamado = form.N_chamado.data
            editar.id_material = form.id_produto.data
            editar.quantidade = form.quantidade.data
            editar.solicitado_em = form.solicitado_em.data
            editar.observacao = form.observacao.data
            editar.entregue_em = form.entregue_em.data
            
            # Salvar alterações no banco
            db.session.commit()
            flash('Pedido atualizado com sucesso.', 'success')
            return redirect(url_for('index_pedidos'))
        else:
            # Caso a validação falhe
            flash('Erro ao validar o formulário.', 'error')
            return render_template('pedidos/editar.html', id=id, form=form)
    except Exception as e:
        # Reverter transação e tratar erros
        db.session.rollback()
        flash(f'Erro ao editar o pedido: {str(e)}', 'error')
        print(str(e))
        return redirect(url_for('index_pedidos'))

# Instancia a classe EmailHandler
email_handler = EmailHandler(SMTP_SERVER, PORT, USERNAME, PASSWORD)


from datetime import date

@app.route('/sistema/pedido/send-email')
def pedido_send_email():
    # Configurações do e-mail
    assunto = 'Pedidos do dia'
    dequem = USERNAME
    paraquem = 'suporte@bigbox.com.br'

    # Data do dia para a consulta
    data_hoje = date.today()

    # Consulta ao banco de dados com filtro pela data de entrega igual à data atual
    consulta = db.session.query(
        RequisicaoMaterial.id,
        RequisicaoMaterial.cnpj,
        Lojas.fantasia,
        RequisicaoMaterial.numero_chamado,
        RequisicaoMaterial.id_material,
        Produtos.nome,
        RequisicaoMaterial.quantidade,
        RequisicaoMaterial.solicitado_em,
        RequisicaoMaterial.observacao,
        RequisicaoMaterial.entregue_em
    ).join(Lojas, RequisicaoMaterial.cnpj == Lojas.cnpj) \
     .join(Produtos, RequisicaoMaterial.id_material == Produtos.id) \
     .filter(RequisicaoMaterial.solicitado_em == data_hoje)  # Filtro pela data de hoje
    
    pedidos = consulta.order_by(Lojas.fantasia).all()
    
    print(assunto, pedidos, paraquem, data_hoje)

    if not assunto or not pedidos or not paraquem:
        flash('Os campos "assunto", "pedidos" e "paraquem" são obrigatórios.', 'error')
        return render_template('pedidos/pedidos.html')

    # Gerar corpo do e-mail
    mensagem = "Relatório de Pedidos:\n\n"
    for pedido in pedidos:
        mensagem += f"ID: {pedido.id}\n"
        mensagem += f"Chamado: {pedido.numero_chamado}\n"
        mensagem += f"Nome Fantasia: {pedido.fantasia}\n"
        mensagem += f"CNPJ: {pedido.cnpj}\n"
        mensagem += f"Produto: {pedido.nome}\n"
        mensagem += f"Quantidade: {pedido.quantidade}\n"
        mensagem += f"Pedido em : {pedido.solicitado_em}\n"
        mensagem += f"Entregue em: {pedido.entregue_em}\n"
        mensagem += "-" * 30 + "\n"

    try:
        # Conecta ao servidor SMTP
        email_handler.connect()

        # Envia o e-mail
        email_handler.send_email(assunto, mensagem, dequem, paraquem )

        # Desconecta após o envio
        email_handler.disconnect()

        flash('E-mail enviado com sucesso!', 'success')
        return redirect(url_for('index_lojas'))

    except Exception as e:
        flash(f'Erro ao enviar e-mail: {e}', 'error')
        return render_template('lojas/lojas.html')
