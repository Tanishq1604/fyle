import pytest
import json
from core import create_app, db

@pytest.fixture(scope='function')
def app():
    """Create application for the tests."""
    _app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    return _app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def app_ctx(app):
    with app.app_context() as ctx:
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def test_data(app_ctx):
    with app_ctx.app_context():
        yield db.session

@pytest.fixture
def h_student_1():
    headers = {
        'X-Principal': json.dumps({
            'student_id': 1,
            'user_id': 1
        })
    }

    return headers

@pytest.fixture
def h_student_2():
    headers = {
        'X-Principal': json.dumps({
            'student_id': 2,
            'user_id': 2
        })
    }

    return headers

@pytest.fixture
def h_teacher_1():
    headers = {
        'X-Principal': json.dumps({
            'teacher_id': 1,
            'user_id': 3
        })
    }

    return headers

@pytest.fixture
def h_teacher_2():
    headers = {
        'X-Principal': json.dumps({
            'teacher_id': 2,
            'user_id': 4
        })
    }

    return headers

@pytest.fixture
def h_principal():
    headers = {
        'X-Principal': json.dumps({
            'principal_id': 1,
            'user_id': 5
        })
    }

    return headers
