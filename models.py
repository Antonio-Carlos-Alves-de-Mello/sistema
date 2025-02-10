from app import db


class Produtos(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return f"<Produto {self.id} - {self.nome}>"

    
class Usuarios(db.Model):
    nome = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), primary_key=True)
    senha = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<Name %r>' % self.nome
    
class Fornecedores (db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    nome_contato = db.Column(db.String(100), nullable=False)
    site = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(15), nullable=False)

    def __repr__(self):
        return '<Name %r>' % self.nome

class Contatos (db.Model):
    idcontatos = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cnpj = db.Column(db.String(14),  nullable=False)
    idsetor = db.Column(db.Integer, nullable=False)
    telefone = db.Column(db.String(45), nullable=False)
    tipo = db.Column(db.String(45), nullable=False)
    contato = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<Name %r>' % self.cnpj
    
class Lojas (db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    razao = db.Column(db.String(200), nullable=False)
    fantasia = db.Column(db.String(250), nullable=False)
    cnpj = db.Column(db.String(14), nullable=False)
    ie = db.Column(db.String(15), nullable=False)
    endereco = db.Column(db.String(250), nullable=False)
    cep = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return '<Name %r>' % self.id
    
class setores (db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    setor = db.Column(db.String(200), nullable=False)
        
    def __repr__(self):
        return '<Nane %r>' % self.id


class tecnicos (db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome =db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return '<Nane %r>' % self.id
    
class ips (db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cnpj = db.Column(db.String(14), nullable=False)
    setor = db.Column(db.String(200), nullable=False)
    ip = db.Column(db.String(20), nullable=False)
    maquina = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Nane %r>' % self.id
    
    
class RequisicaoMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cnpj = db.Column(db.String(14), nullable=False)
    numero_chamado = db.Column(db.String(50), nullable=False)
    id_material = db.Column(db.Integer)
    quantidade = db.Column(db.Integer)
    solicitado_em = db.Column(db.Date, nullable=True)  # Data de solicitação
    observacao = db.Column(db.Text, nullable=True)     # Observação é opcional
    entregue_em = db.Column(db.Date, nullable=True)    # Data de entrega
    
    def __repr__(self):
        return '<Nane %r>' % self.id
    

class Estoque(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cnpj_loja = db.Column(db.String(14), nullable=False)
    id_fornecedor = db.Column(db.Integer)
    id_produto = db.Column(db.Integer)
    acao = db.Column(db.String(1), nullable=False)
    qnt = db.Column(db.Integer)
    id_tecnico = db.Column(db.Integer)
    n_glpi_chamado = db.Column(db.String, nullable=True)
    observacao = db.Column(db.Text, nullable=True)
    data_lancamento = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return '<Nane %r>' % self.id