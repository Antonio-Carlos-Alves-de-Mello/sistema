# Sistema de gerenciamento

Aplicação web em Python e Flask para gestão de produtos, estoque, fornecedores, unidades, contatos, setores, técnicos e requisições de materiais. Inclui cadastro e login de usuários, consultas públicas e rotinas de relatórios.

**Estado atual:** projeto em desenvolvimento. O arquivo de configuração e a criação do banco precisam ser preparados localmente; há limitações de navegação e autenticação descritas ao final.

## Tecnologias

- Python e Flask.
- Flask-SQLAlchemy e SQLAlchemy para persistência.
- Flask-WTF e WTForms para formulários e proteção CSRF.
- Jinja, HTML e CSS para as telas.
- ReportLab para relatórios PDF.
- SMTP para envio de e-mail.

A conexão do banco é definida por `SQLALCHEMY_DATABASE_URI` em um `config.py` local. O repositório inclui o driver MySQL, mas não contém a configuração efetiva do ambiente; não pressupõe um banco SQLite já pronto.

## Estrutura

| Caminho | Responsabilidade |
| --- | --- |
| [app.py](app.py) | Inicializa Flask, carrega configuração e registra os módulos de rotas. |
| [models.py](models.py) | Modelos do banco de dados. |
| [views/](views/) | Rotas dos módulos e autenticação. |
| [helpers.py](helpers.py) | Formulários e validações. |
| [templates/](templates/) | Telas HTML/Jinja. |
| [static/](static/) | Recursos estáticos. |
| [envia_email.py](envia_email.py) | Cliente de e-mail SMTP. |
| [requirements.txt](requirements.txt) | Dependências versionadas. |

## Preparação do ambiente local

### 1. Obter o projeto e criar o ambiente

```sh
git clone https://github.com/Antonio-Carlos-Alves-de-Mello/sistema.git
cd sistema
python -m venv .venv
```

Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```sh
source .venv/bin/activate
```

Instale as dependências:

```sh
python -m pip install -r requirements.txt
```

### 2. Criar a configuração local

O código exige um arquivo `config.py` na raiz, que não está incluído no repositório. Um exemplo para **desenvolvimento local com SQLite** é:

```python
import os

SECRET_KEY = os.environ["SECRET_KEY"]
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///sistema-dev.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False

SMTP_SERVER = os.getenv("SMTP_SERVER", "localhost")
PORT = int(os.getenv("SMTP_PORT", "587"))
USERNAME = os.getenv("SMTP_USERNAME", "")
PASSWORD = os.getenv("SMTP_PASSWORD", "")
```

Esse exemplo é uma configuração proposta para desenvolvimento, não uma reprodução do ambiente original. O código não carrega `.env` automaticamente: defina as variáveis no terminal ou no ambiente que inicia a aplicação.

Gere uma chave temporária na sessão do PowerShell:

```powershell
$env:SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
```

Ou no Linux/macOS:

```sh
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
```

Para MySQL, defina `DATABASE_URL` com o formato `mysql+mysqlconnector://USUARIO:SENHA@HOST/BANCO`, usando credenciais locais e um banco existente. Valores com caracteres especiais precisam ser codificados corretamente na URL.

### 3. Preparar as tabelas de desenvolvimento

O repositório não possui um fluxo de migrações. Para criar as tabelas dos modelos em um banco de desenvolvimento vazio, abra:

```sh
python -m flask --app app shell
```

No console Python:

```python
from app import db
import models
db.create_all()
exit()
```

`create_all()` cria tabelas ausentes; não migra a estrutura de tabelas existentes. O exemplo SQLite evita depender de um servidor MySQL, mas os fluxos completos ainda precisam ser validados nesse banco.

### 4. Iniciar a aplicação

```sh
python -m flask --app app run
```

O módulo de entrada é `app.py`; não há `run.py` no repositório. O comando acima importa o módulo pelo Flask, sem depender da execução direta como `__main__`.

Acesse:

- [Login](http://127.0.0.1:5000/sistema/login).
- [Cadastro de usuário](http://127.0.0.1:5000/sistema/usuario/novo).
- [Consulta de unidades](http://127.0.0.1:5000/unidades).
- [Consulta de contatos](http://127.0.0.1:5000/contatos).
- [Consulta de IPs](http://127.0.0.1:5000/ips).

## Autenticação e configuração

O login atual consulta o usuário por e-mail, compara um hash SHA-256 da senha e registra `usuario_logado` na sessão. Embora Flask-Bcrypt seja inicializado, essas rotas ainda utilizam `hashlib.sha256`; a migração para um algoritmo específico para senhas permanece pendente.

A chave de sessão deve ser configurada em `config.py`. A variável `SECRET_KEY` declarada isoladamente em `app.py` não substitui essa configuração.

As rotinas de e-mail importam `SMTP_SERVER`, `PORT`, `USERNAME` e `PASSWORD` de `config.py`. Os destinatários ainda estão fixos nos módulos de lojas e pedidos; revise-os antes de testar envios. Mantenha credenciais fora do código versionado.

## Limitações conhecidas

- Há redirecionamentos para o endpoint `index`, sem uma definição correspondente nos módulos de rotas inspecionados. Alguns retornos de formulário e o logout podem falhar até esse ajuste.
- Existem rotas de exclusão por GET e verificações de acesso que precisam de revisão.
- Há módulos duplicados para fornecedores; `app.py` importa `views/views_fornecedores.py`.
- A edição de usuário contém uma função ainda não implementada.
- Não há migrações nem uma suíte de testes versionada na árvore inspecionada.

## Validação desta documentação

Esta revisão conferiu comandos, módulos e configurações por leitura do código. Não executou a aplicação, o banco ou envios de e-mail e não declara compatibilidade funcional completa entre bancos. As pendências acima permanecem no código.
