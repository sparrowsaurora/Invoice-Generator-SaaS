from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    db.init_app(app)
    
    from .routes import main
    app.register_blueprint(main)

    # 404 handler
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404
    
    @app.context_processor
    def inject_current_year():
        return {'current_year': datetime.datetime.now().year}

    return app
