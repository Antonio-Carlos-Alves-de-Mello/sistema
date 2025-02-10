from flask import render_template, redirect, url_for, send_from_directory, flash, request,session,make_response
from helpers import FormularioDeIps
from app import app, db 
from models import ips, Lojas
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors

@app.route('/sistema/ips')
def index_ips():
    # Obtém o termo de busca da URL
    termo_busca = request.args.get('search', '', type=str).strip()

    # Consulta ao banco de dados
    consulta = db.session.query(
        ips.id,
        Lojas.fantasia,
        ips.setor,
        ips.ip,
        ips.maquina
    ).join(ips, ips.cnpj == Lojas.cnpj)

    # Aplica o filtro de busca, se houver um termo
    if termo_busca:
        consulta = consulta.filter(
            db.or_(
                Lojas.fantasia.ilike(f"%{termo_busca}%"),
                ips.setor.ilike(f"%{termo_busca}%"),
                ips.ip.ilike(f"%{termo_busca}%"),
                ips.maquina.ilike(f"%{termo_busca}%")
            )
        )

    # Ordena os resultados
    lista_ips = consulta.order_by(ips.cnpj).all()

    # Contar o número total de IPs no banco de dados
    total_ips = db.session.query(ips).count()

    # Renderiza o template
    return render_template(
        'ips/ips.html',
        lista_ips=lista_ips,
        termo_busca=termo_busca,
        total_ips=total_ips  # Passa a contagem de IPs para o template
    )

@app.route('/sistema/ip/novo')
def novo_ip():
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        return redirect(url_for('login', proxima=url_for('novo_ip')))
    
    form = FormularioDeIps()
    form.cnpj.choices = [(loja.cnpj, loja.fantasia) for loja in Lojas.query.all()]
    return render_template('ips/novo.html', form=form)

@app.route('/sistema/ip/criar', methods=['POST'])
def salvar_ip():
    form = FormularioDeIps()
    form.cnpj.choices = [(loja.cnpj, loja.razao) for loja in Lojas.query.all()]
    
    if not form.validate_on_submit():
        flash('Erro ao validar o formulário.', 'error')
        return render_template('ips/novo.html', form=form)

    cnpj_selecionado = form.cnpj.data
    novo_ip_dado = form.ip.data.strip()  # Remove espaços extras, caso existam

    # Verificar se o IP já existe
    ip_existente = ips.query.filter_by(ip=novo_ip_dado).first()
    if ip_existente:
        flash(f'O IP "{novo_ip_dado}" já está cadastrado.', 'error')
        return render_template('ips/novo.html', form=form)

    # Criar e salvar o novo IP
    novo_ip = ips(
        cnpj=cnpj_selecionado,
        setor=form.setor.data.strip(),
        ip=novo_ip_dado,
        maquina=form.maquina.data.strip()
    )

    try:
        db.session.add(novo_ip)
        db.session.commit()
        flash('IP criado com sucesso!', 'success')
        return redirect(url_for('index_ips'))
    except db.IntegrityError:
        db.session.rollback()
        flash('Erro ao salvar o IP. Verifique os dados e tente novamente.', 'error')
        return render_template('ips/novo.html', form=form)
@app.route('/sistema/ip/editar/<int:id>', methods=['GET', 'POST'])
def editar_ip(id):
    try:
        # Obtém o IP pelo ID
        ip_edita = ips.query.filter(ips.id == id).first()
        if not ip_edita:
            flash('IP não encontrado.', 'error')
            return redirect(url_for('index_ips'))

        # Inicializa o formulário
        form = FormularioDeIps()
        form.cnpj.choices = [(loja.cnpj, loja.fantasia) for loja in Lojas.query.all()]
        # Preenche o formulário com os dados do IP para requisições GET
        if request.method == 'GET':
            form.cnpj.data = ip_edita.cnpj
            form.setor.data = ip_edita.setor
            form.ip.data = ip_edita.ip
            form.maquina.data = ip_edita.maquina
            return render_template('ips/editar.html', id=id, form=form)

        # Valida e processa o formulário para requisições POST
        if request.method == 'POST' and form.validate_on_submit():
            ip_edita.cnpj = form.cnpj.data
            ip_edita.setor = form.setor.data
            ip_edita.ip = form.ip.data
            ip_edita.maquina = form.maquina.data

            # Atualiza o banco de dados
            db.session.commit()
            flash('IP atualizado com sucesso!', 'success')
            return redirect(url_for('index_ips'))
        else:
            flash('Erro ao validar o formulário.', 'error')
            return render_template('ips/editar.html', id=id, form=form)

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao editar o IP: {str(e)}', 'error')
        return redirect(url_for('index_ips'))


@app.route('/sistema/ip/apagar/<int:id>')
def apagar_ip(id):
    ips.query.filter_by(id=id).delete()
    db.session.commit()
    flash('IP apagado com sucesso')
    return redirect(url_for('index_ips'))

@app.route('/gerar-pdf')
def gerar_pdf():
    # Criação do buffer para o PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Lista para armazenar elementos do relatório
    elements = []

    # Estilos para texto
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1  # Centralizado
    title_paragraph = Paragraph("Relatório de IPs", title_style)

    # Adiciona título
    elements.append(title_paragraph)
    elements.append(Paragraph("<hr/>", styles['Normal']))  # Linha horizontal

    # Consulta ao banco de dados
    try:
        Lista_ips_PDF = (
            db.session.query(
                Lojas.fantasia,
                ips.setor,
                ips.ip,
                ips.maquina
            )
            .join(ips, ips.cnpj == Lojas.cnpj)
            .order_by(ips.cnpj, ips.setor)
            .all()
        )

        # Construção dos dados para a tabela
        data = [["Unidade", "Setor", "IP", "Máquina"]]  # Cabeçalho da tabela
        data.extend([[ip.fantasia, ip.setor, ip.ip, ip.maquina] for ip in Lista_ips_PDF])

        # Configuração da tabela
        table = Table(data, colWidths=[190, 105, 90, 120])  # Ajuste da largura das colunas
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Fundo do cabeçalho
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Cor do texto do cabeçalho
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alinhamento central
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Fonte do cabeçalho
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),  # Espaçamento no cabeçalho
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Fundo das linhas
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Grade da tabela
        ])
        table.setStyle(style)

        # Adiciona tabela ao PDF
        elements.append(table)

    except Exception as e:
        # Adiciona mensagem de erro ao PDF
        error_message = [
            Paragraph("Erro ao gerar o relatório.", styles['Normal']),
            Paragraph(f"Detalhes do erro: {str(e)}", styles['Normal'])
        ]
        elements.extend(error_message)

    # Geração do documento PDF
    try:
        doc.build(elements)
    except Exception as build_error:
        return f"Erro ao gerar o documento PDF: {str(build_error)}"

    # Configuração da resposta HTTP para servir o PDF
    buffer.seek(0)
    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=relatorio_ips.pdf'

    return response
