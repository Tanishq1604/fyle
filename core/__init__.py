from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(test_config=None):
    app = Flask(__name__)
    
    # Ensure the instance folder exists and is accessible
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Use absolute path for database
    db_path = os.path.join(app.instance_path, 'store.sqlite3')
    app.config.update(
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{db_path}',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ECHO=False
    )
    
    if test_config:
        app.config.update(test_config)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Register blueprints once
        from core.server import register_blueprints
        register_blueprints(app)
        
        # Create database tables
        db.create_all()
    
    return app
