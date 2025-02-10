from flask import render_template, request
from app import app, db
from models import Lojas, ips, Contatos, setores


@app.route('/unidades')

def home():
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
    return render_template('publico/unidades.html', lista_lojas=lista_lojas, termo_busca=termo_busca)

@app.route('/contatos')
def lista_contatos():
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
    
    return render_template('publico/contatos.html', Lista_contatos=Lista_Contatos, termo_busca=termo_busca)



@app.route('/ips')
def lista_ips():
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
        ).order_by(Lojas.fantasia, ips.cnpj)
    # Ordena os resultados
    lista_ips = consulta.order_by(Lojas.fantasia, ips.cnpj).all()
    # Renderiza o template
    return render_template('publico/ips.html', lista_ips=lista_ips, termo_busca=termo_busca)
