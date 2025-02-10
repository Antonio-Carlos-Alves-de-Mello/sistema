from flask import render_template, request , redirect, url_for , session,flash
from helpers import FormularioEstoque
from app import app, db
from models import Estoque, Lojas, Produtos, tecnicos, Fornecedores

@app.route('/sistema/estoque')
def Index_estoque():
    
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        return redirect(url_for('login', proxima=url_for('Index_estoque')))
    
    # Obtém o termo de busca a partir dos parâmetros da URL
    termo_busca = request.args.get('search', '', type=str).strip()

    # Cria a consulta ao banco de dados
    consulta = db.session.query(
        Estoque.id.label("estoque_id"),
        Estoque.cnpj_loja,
        Lojas.fantasia.label("nome_loja"),
        Estoque.id_fornecedor,
        Fornecedores.nome.label("nome_fornecedor"),
        Estoque.id_produto,
        Produtos.nome.label("nome_produto"),
        # Substituição dos valores de 'acao' por texto
        db.case(
            (Estoque.acao == '1', 'Saída'), (Estoque.acao == '2', 'Entrada'),
            else_='desconhecido'
        ).label("entrada_saida"),
        Estoque.qnt,
        Estoque.id_tecnico,
        tecnicos.nome.label("nome_tecnico"),
        Estoque.n_glpi_chamado.label("chamado"),
        Estoque.observacao,
        Estoque.data_lancamento
    ).join(
        Lojas, Estoque.cnpj_loja == Lojas.cnpj
    ).join(
        Produtos, Estoque.id_produto == Produtos.id
    ).join(
        tecnicos, Estoque.id_tecnico == tecnicos.id
    ).join(
        Fornecedores, Estoque.id_fornecedor == Fornecedores.id
    )

    # Adiciona o filtro com base no termo de busca, se fornecido
    if termo_busca:
        consulta = consulta.filter(
            db.or_(
                Lojas.fantasia.ilike(f"%{termo_busca}%"),
                Estoque.n_glpi_chamado.ilike(f"%{termo_busca}%"),
                tecnicos.nome.ilike(f"%{termo_busca}%"),
                Estoque.acao.ilike(f"%{termo_busca}%"),
                Produtos.nome.ilike(f"%{termo_busca}%")
            )
        )

    # Ordena os resultados pelo nome da loja e obtém todos os registros
    lista_estoque = consulta.order_by(Lojas.fantasia, Produtos.nome).all()

    # Renderiza o template com os dados da consulta
    return render_template(
        'estoque/estoque.html',
        lista_estoque=lista_estoque,
        termo_busca=termo_busca
    )
@app.route('/sistema/estoque/novo', methods=['GET', 'POST'])
def novo_lacamento():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('novo')))
    form = FormularioEstoque()

    # Configuração dinâmica das opções
    form.cnpj_loja.choices = [(loja.cnpj, loja.fantasia) for loja in Lojas.query.all()]
    form.id_fornecedor.choices = [(fornecedor.id, fornecedor.nome) for fornecedor in Fornecedores.query.all()]
    form.id_produto.choices = [(produto.id, produto.nome) for produto in Produtos.query.all()]
    form.id_tecnico.choices = [(tecnico.id, tecnico.nome) for tecnico in tecnicos.query.all()]

    if form.validate_on_submit():
        # Criação de um novo item no estoque
        novo_item_estoque = Estoque(
            cnpj_loja=form.cnpj_loja.data,
            id_fornecedor=form.id_fornecedor.data,
            id_produto=form.id_produto.data,
            acao=form.acao.data,
            qnt=form.qnt.data,
            id_tecnico=form.id_tecnico.data,
            n_glpi_chamado=form.n_glpi_chamado.data,
            observacao=form.observacao.data,
            data_lancamento=form.data_lancamento.data
        )

        # Salvar no banco de dados
        db.session.add(novo_item_estoque)
        db.session.commit()

        flash('Lançamento realizado com sucesso!', 'success')
        return redirect(url_for('Index_estoque'))

    return render_template('estoque/novo.html', form=form)


@app.route('/sistema/estoque/editar')
def editar_estoque():
     if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('novo')))
    

@app.route('/sistema/estoque/apagar')
def apagar_estoque():
     if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('novo')))
     
     
@app.route('/sistema/estoque/publico')
def ver_estoque():
    # Obtém o termo de busca a partir dos parâmetros da URL
    termo_busca = request.args.get('search', '', type=str).strip()

    # Consulta ajustada para calcular a diferença entre entradas e saídas
    consulta = db.session.query(
        
        Estoque.id_produto,
        Produtos.nome.label("nome_produto"),
        # Soma as entradas e saídas separadamente, depois calcula a diferença
        db.func.sum(
            db.case((Estoque.acao == '2', Estoque.qnt), else_=0)
        ).label("total_entrada"),
        db.func.sum(
            db.case((Estoque.acao == '1', Estoque.qnt), else_=0)
        ).label("total_saida"),
        (db.func.sum(
            db.case((Estoque.acao == '2', Estoque.qnt), else_=0)
        ) - db.func.sum(
            db.case((Estoque.acao == '1', Estoque.qnt), else_=0)
        )).label("saldo")
    ).join(
        Lojas, Estoque.cnpj_loja == Lojas.cnpj
    ).join(
        Produtos, Estoque.id_produto == Produtos.id
    ).join(
        tecnicos, Estoque.id_tecnico == tecnicos.id
    ).join(
        Fornecedores, Estoque.id_fornecedor == Fornecedores.id
    ).group_by(
       
        Estoque.id_produto,
        Produtos.nome
    )

    # Adiciona o filtro com base no termo de busca, se fornecido
    if termo_busca:
        consulta = consulta.filter(
            db.or_(
                
                Produtos.nome.ilike(f"%{termo_busca}%")
            )
        )

    # Obtém os registros ordenados
    lista_estoque = consulta.order_by(Produtos.nome).all()

    # Renderiza o template com os dados da consulta
    return render_template(
        'estoque/ver_estoque.html',
        lista_estoque=lista_estoque,
        termo_busca=termo_busca
    )