from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt

SECRET_KEY = 'alura'
app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)

csrf = CSRFProtect(app)
bcrypt = Bcrypt(app)


from views.views_home import *
from views.views_usuarios import *
from views.views_produtos import *
from views.views_setores import *
from views.views_fornecedores import *
from views.views_contatos import *
from views.views_tecnicos import *
from views.views_lojas import *
from views.views_ips import *
from views.views_pedidos import *
from views.views_estoque import *



if __name__ == '__main__':
    app.run(debug=True)
    