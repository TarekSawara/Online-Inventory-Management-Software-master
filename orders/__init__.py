from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_login import LoginManager
from flask_migrate import Migrate
# from .extensions import db
from flask_ngrok import run_with_ngrok




app = Flask(__name__)
# run_with_ngrok(app)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders4.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #to disable the warrning
db = SQLAlchemy(app)
migrate = Migrate(app, db)

api = Api(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'



# with app.app_context():
#         db.create_all()

from orders import routes
from orders import orderapi
