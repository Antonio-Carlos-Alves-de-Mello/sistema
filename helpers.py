import os
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators, PasswordField, EmailField, TelField, SelectField, DateField, IntegerField, TextAreaField
from wtforms.validators import Optional

# Constantes para comprimentos máximos de campos
MAX_LENGTH_NOME = 150
MAX_LENGTH_EMAIL = 100
MAX_LENGTH_SENHA = 100
MAX_LENGTH_TELEFONE = 15
MAX_LENGTH_CNPJ = 14
MAX_LENGTH_CEP = 10

class BaseForm(FlaskForm):
    """Classe base para reutilização de campos comuns."""
    nome = StringField('Nome', [validators.DataRequired(), validators.Length(min=1, max=MAX_LENGTH_NOME)],
                       render_kw={"style": "text-transform: uppercase;"})
    email = EmailField('Email', [validators.DataRequired(), validators.Length(min=1, max=MAX_LENGTH_EMAIL)])
    senha = PasswordField('Senha', [validators.DataRequired(), validators.Length(min=1, max=MAX_LENGTH_SENHA)])

class FormularioProdutos(BaseForm):
    """Formulário para cadastro de produtos."""
    salvar = SubmitField('Salvar')

class FormularioUsuario(BaseForm):
    """Formulário para login de usuários."""
    login = SubmitField('Login')

class FormularioDeCadastroUsuarios(BaseForm):
    """Formulário para cadastro de novos usuários."""
    salvar = SubmitField('Salvar')

class FormularioFornecedores(BaseForm):
    """Formulário para cadastro de fornecedores."""
    contato = StringField('Nome do contato', [validators.DataRequired(), validators.Length(min=1, max=MAX_LENGTH_NOME)],
                          render_kw={"style": "text-transform: uppercase;"})
    site = StringField('Site', [validators.DataRequired(), validators.Length(min=1, max=MAX_LENGTH_EMAIL)])
    telefone = TelField('Telefone para contato', [validators.DataRequired(), validators.Length(max=MAX_LENGTH_TELEFONE)])
    salvar = SubmitField('Salvar')

class FormularioContatos(FlaskForm):
    """Formulário para cadastro de contatos."""
    cnpj = SelectField('Unidade', choices=[])
    idsetor = SelectField('Setor', choices=[], coerce=int)
    telefone = TelField('Telefone', [validators.DataRequired(), validators.Length(min=4, max=MAX_LENGTH_TELEFONE)])
    tipo = StringField('Tipo', [validators.DataRequired(), validators.Length(max=50)])
    contato = StringField('Contato', [validators.DataRequired(), validators.Length(max=MAX_LENGTH_NOME)],
                          render_kw={"style": "text-transform: uppercase;"})
    submit = SubmitField('Enviar')

class FormularioTecnicos(BaseForm):
    """Formulário para cadastro de técnicos."""
    submit = SubmitField('Enviar')

class FormularioDeSetores(FlaskForm):
    """Formulário para cadastro de setores."""
    setor = StringField('Nome do setor', [validators.DataRequired(), validators.Length(min=1, max=45)])
    salvar = SubmitField('Enviar')

class FormulariodeLojas(FlaskForm):
    """Formulário para cadastro de lojas."""
    razao = StringField('Razão Social', [validators.DataRequired(), validators.Length(min=1, max=200)],
                        render_kw={"style": "text-transform: uppercase;"})
    fantazia = StringField('Nome Fantasia', [validators.DataRequired(), validators.Length(min=1, max=250)],
                           render_kw={"style": "text-transform: uppercase;"})
    cnpj = StringField('CNPJ', [validators.DataRequired(), validators.Length(min=1, max=MAX_LENGTH_CNPJ)],
                       render_kw={"style": "text-transform: uppercase;"})
    ie = StringField('Insc. Estadual', [validators.DataRequired(), validators.Length(min=1, max=15)],
                     render_kw={"style": "text-transform: uppercase;"})
    endereco = StringField('Endereço', [validators.DataRequired(), validators.Length(min=1, max=250)],
                           render_kw={"style": "text-transform: uppercase;"})
    cep = StringField('CEP', [validators.DataRequired(), validators.Length(min=1, max=MAX_LENGTH_CEP)],
                      render_kw={"style": "text-transform: uppercase;"})
    salvar = SubmitField('Enviar')

class FormularioDeIps(FlaskForm):
    """Formulário para cadastro de IPs."""
    cnpj = SelectField('Unidades', choices=[])
    setor = StringField('Setores', [validators.DataRequired(), validators.Length(min=1, max=200)],
                        render_kw={"style": "text-transform: uppercase;"})
    ip = StringField('IP´s', [validators.DataRequired(), validators.Length(min=1, max=20)],
                     render_kw={
                         "style": "text-transform: uppercase;",
                         "pattern": "^([0-9]{1,3}\.){3}[0-9]{1,3}$",  # Regex para endereços IP
                         "title": "Digite um endereço IP válido (ex: 192.168.0.1)"
                     })
    maquina = StringField('Nome da Máquina', [validators.DataRequired(), validators.Length(min=1, max=200)],
                          render_kw={"style": "text-transform: uppercase;"})
    salvar = SubmitField('Enviar')

class FormulariodePedidos(FlaskForm):
    """Formulário para cadastro de pedidos."""
    cnpj = SelectField('Unidade', choices=[])
    N_chamado = StringField('Número do Chamado', [validators.DataRequired()])
    id_produto = SelectField('Produto', choices=[])
    quantidade = IntegerField('Quantidade', [validators.DataRequired()])
    solicitado_em = DateField('Solicitado em', format='%Y-%m-%d')
    observacao = TextAreaField('Observação')
    entregue_em = DateField('Entregue em', validators=[Optional()], format='%Y-%m-%d')
    salvar = SubmitField('Salvar')

class FormularioEstoque(FlaskForm):
    """Formulário para gerenciamento de estoque."""
    cnpj_loja = SelectField('Unidade', choices=[])
    id_fornecedor = SelectField('Fornecedor', choices=[])
    id_produto = SelectField('Produto', choices=[])
    acao = StringField('Ação', [validators.DataRequired(), validators.Length(min=1, max=1)],
                       render_kw={"style": "text-transform: uppercase;"})
    qnt = IntegerField('Quantidade')
    id_tecnico = SelectField('Técnico', choices=[])
    n_glpi_chamado = StringField('Nº do Chamado', [validators.DataRequired(), validators.Length(min=1, max=5)],
                                 render_kw={"style": "text-transform: uppercase;"})
    observacao = TextAreaField('Observação')
    data_lancamento = DateField('Data do Lançamento', format='%Y-%m-%d')
    salvar = SubmitField('Salvar')