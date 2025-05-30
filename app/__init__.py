from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_login import LoginManager

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    db.init_app(app)
    
    from .routes import main
    from .auth import auth as auth_blueprint
    app.register_blueprint(main)
    app.register_blueprint(auth_blueprint)

    from .models import User

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # redirect to login if not logged in

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.init_app(app)

    # 404 handler
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404
    
    @app.context_processor
    def inject_current_year():
        return {'current_year': datetime.datetime.now().year}

    return app
