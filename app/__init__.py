from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

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

    return app
