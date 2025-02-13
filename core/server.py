from flask import jsonify, Blueprint, Flask
from flask_migrate import Migrate
from marshmallow.exceptions import ValidationError
from core.apis.assignments import student_assignments_resources, teacher_assignments_resources, \
    principal_assignments_resources
from core.apis.teachers import principal_teachers_resources
from core.libs import helpers
from core.libs.exceptions import FyleError
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from core import create_app
from core import db
from core.admin import init_admin
import os

def create_main_blueprint():
    main_bp = Blueprint('main', __name__)
    
    @main_bp.route('/')
    def ready():
        return jsonify({
            'status': 'ready',
            'time': helpers.get_utc_now()
        })
    
    return main_bp

def register_blueprints(app):
    if 'main' not in app.blueprints:
        app.register_blueprint(create_main_blueprint())
    
    blueprints = [
        (student_assignments_resources, '/student'),
        (teacher_assignments_resources, '/teacher'),
        (principal_assignments_resources, '/principal'),
        (principal_teachers_resources, '/principal')
    ]
    
    for blueprint, url_prefix in blueprints:
        if blueprint.name not in app.blueprints:
            app.register_blueprint(blueprint, url_prefix=url_prefix)

    @app.errorhandler(Exception)
    def handle_error(err):
        if isinstance(err, FyleError):
            return jsonify(error=err.__class__.__name__, message=err.message), err.status_code
        elif isinstance(err, ValidationError):
            return jsonify(error=err.__class__.__name__, message=err.messages), 400
        elif isinstance(err, IntegrityError):
            return jsonify(error=err.__class__.__name__, message=str(err.orig)), 400
        elif isinstance(err, HTTPException):
            return jsonify(error=err.__class__.__name__, message=str(err)), err.code
        raise err

    return app

def create_app(config=None):
    app = Flask(__name__)
    
    # Get the instance path
    instance_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    
    # Default configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "store.sqlite3")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    
    if config:
        app.config.update(config)
    
    db.init_app(app)
    migrate = Migrate(app, db)  # Add this line
    
    with app.app_context():
        db.create_all()  # Ensure all tables are created
        init_admin(app)  # Initialize admin interface
    
    app = register_blueprints(app)
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run()
