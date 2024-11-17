from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from sqlalchemy import inspect, Table

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'boom'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'  # Konfigūruojama duomenų bazė

    db.init_app(app)  # Inicializuojama Flask aplikacija su šiuo plėtiniu

    # Registruojame Blueprint'us
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Sukuriame duomenų bazę, jei jos dar nėra
    with app.app_context():
        if not path.exists('website/' + DB_NAME):
            print("Created Database")
            db.create_all()


    # Inicializuojame LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # Nukreipimo puslapis, kai reikia prisijungti
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User  # Importuojame User modelį čia, kad išvengtume ciklinių importų
        return User.query.get(int(user_id))

    return app

