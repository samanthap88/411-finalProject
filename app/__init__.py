from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    db.init_app(app)
    migrate.init_app(app, db)
    from app.models import User, Favorite, Team

    # Register Blueprints
    from app.routes import auth_routes, pokemon_routes, team_routes
    app.register_blueprint(auth_routes.bp, url_prefix="/auth")
    app.register_blueprint(pokemon_routes.bp, url_prefix="/pokemon")
    app.register_blueprint(team_routes.bp, url_prefix="/team")

    return app
