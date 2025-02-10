from flask import jsonify, render_template, redirect, url_for, send_from_directory, flash, request,session
from config import PASSWORD, PORT, SMTP_SERVER, USERNAME
from helpers import FormulariodeLojas
from app import app, db 
from models import Lojas
from envia_email import EmailHandler

@app.route('/sistema/lojas')
def index_lojas():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('nova_loja')))
    # Obtém o termo de busca da URL
    termo_busca = request.args.get('search', '', type=str).strip()
    
    # Consulta ao banco de dados
    consulta = db.session.query(
        Lojas.id,
        Lojas.razao,
        Lojas.fantasia,
        Lojas.cnpj,
        Lojas.ie,
        Lojas.endereco,
        Lojas.cep
    )
    
    # Aplica o filtro de busca, se houver um termo
    if termo_busca:
        consulta = consulta.filter(
            db.or_(
                Lojas.razao.like(f'%{termo_busca}%'),
                Lojas.fantasia.ilike(f"%{termo_busca}%"),
                Lojas.cnpj.ilike(f"%{termo_busca}%"),
                Lojas.ie.ilike(f"{termo_busca}"),
                Lojas.endereco.ilike(f"%{termo_busca}%"),
                Lojas.cep.ilike(f"%{termo_busca}%")
            )
        )
    
    # Ordena os resultados
    lista_lojas = consulta.order_by(Lojas.fantasia).all()
   
    
    # Renderiza o template
    return render_template('lojas/lojas.html', lista_lojas=lista_lojas, termo_busca=termo_busca)

@app.route('/sistema/loja/novo')
def nova_loja():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('nova_loja')))
    form = FormulariodeLojas()
    return render_template('lojas/novo.html', form=form)


@app.route('/sistema/loja/enviar', methods=['POST',])
def criar_loja():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('nova_loja')))
    form = FormulariodeLojas()
    
    if not form.validate_on_submit():
        print("Erros de validação:", form.errors)
        flash('Erro ao validar o formulário.', 'error')
        return render_template('lojas/novo.html', form=form)
    
    # Consultar para verificar seo CNPJ existe no banco
    cnpj = form.cnpj.data 
    loja = Lojas.query.filter_by(cnpj=cnpj).first()
    if loja:
        flash('Este CNPJ ja esta cadastrado.', 'error')
        return redirect(url_for('nova_loja'))
    

    # Criar novo contato
    Loja_nova = Lojas (
        razao = form.razao.data,
        fantasia = form.fantazia.data,
        cnpj = form.cnpj.data,
        ie = form.ie.data,
        endereco = form.endereco.data ,
        cep = form.cep.data
    )
    db.session.add(Loja_nova)
    db.session.commit()
    flash('Loja cadastrado com sucesso.', 'success')
    return redirect(url_for('index_lojas'))


@app.route('/sistema/loja/editar/<int:id>',methods=['GET', 'POST'])
def editar_loja(id):

    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('nova_loja')))
    Loja = Lojas.query.filter_by(id=id).first()
    if not Loja:
        flash('Loja não encontrada ','Erro')
        return redirect(url_for('index_lojas'))
    
    form=FormulariodeLojas()
    if request.method == 'POST' and form.validate_on_submit():
        Loja.razao = form.razao.data
        Loja.fantasia = form.fantazia.data
        Loja.cnpj = form.cnpj.data
        Loja.ie = form.ie.data
        Loja.endereco = Loja.endereco
        Loja.cep = form.cep.data
        db.session.commit()
        flash('Loja atualizado com sucesso.', 'success')
        return redirect(url_for('index_lojas'))
    
    form.razao.data = Loja.razao
    form.fantazia.data = Loja.fantasia
    form.cnpj.data = Loja.cnpj
    form.ie.data = Loja.ie
    form.endereco.data = Loja.endereco
    form.cep.data = Loja.cep
    return render_template('lojas/editar.html', id=id ,form=form)

@app.route('/sistema/loja/apagar/<int:id>')
def apagar_loja(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('nova_loja')))
    Lojas.query.filter_by(id=id).delete()
    db.session.commit()
    flash('Unidade apagado com sucesso')
    return redirect(url_for('index_lojas'))
 

# Instancia a classe EmailHandler
email_handler = EmailHandler(SMTP_SERVER, PORT, USERNAME, PASSWORD)

@app.route('/sistema/send-email')
def send_email():
    # Configurações do e-mail
    assunto = 'Assunto do E-mail'
    dequem = USERNAME
    paraquel = 'antonio.mello@bigbox.com.br'

    # Consulta ao banco de dados
    consulta = db.session.query(
        Lojas.id,
        Lojas.razao,
        Lojas.fantasia,
        Lojas.cnpj,
        Lojas.ie,
        Lojas.endereco,
        Lojas.cep
    )
    
    lojas = consulta.order_by(Lojas.fantasia).all()

    if not assunto or not lojas or not paraquel:
        flash('Os campos "assunto", "lojas" e "paraquel" são obrigatórios.', 'error')
        return render_template('lojas/lojas.html')

    # Gerar corpo do e-mail
    mensagem = "Relatório de Lojas:\n\n"
    for loja in lojas:
        mensagem += f"ID: {loja.id}\n"
        mensagem += f"Razão Social: {loja.razao}\n"
        mensagem += f"Nome Fantasia: {loja.fantasia}\n"
        mensagem += f"CNPJ: {loja.cnpj}\n"
        mensagem += f"IE: {loja.ie}\n"
        mensagem += f"Endereço: {loja.endereco}\n"
        mensagem += f"CEP: {loja.cep}\n"
        mensagem += "-" * 30 + "\n"

    try:
        # Conecta ao servidor SMTP
        email_handler.connect()

        # Envia o e-mail
        email_handler.send_email(assunto, mensagem, dequem, paraquel)

        # Desconecta após o envio
        email_handler.disconnect()

        flash('E-mail enviado com sucesso!', 'success')
        return redirect(url_for('index_lojas'))

    except Exception as e:
        flash(f'Erro ao enviar e-mail: {e}', 'error')
        return render_template('lojas/lojas.html')
