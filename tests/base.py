import pytest
import unittest
from core import create_app, db
from core.models.assignments import Assignment, AssignmentStateEnum, GradeEnum

class BaseTestCase(unittest.TestCase):
    """A base test case for Flask """

    def setUp(self):
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'  # Use in-memory database for tests
        })
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        with self.app_context:
            db.session.remove()
            db.drop_all()
        self.app_context.pop()

class BaseTest:
    @pytest.fixture(autouse=True)
    def setup(self, app_ctx, test_data):
        """Initialize test environment"""
        self.app = app_ctx
        self.client = self.app.test_client()
        self.db = db
        self.session = test_data
        
        # Create class-specific test data
        with self.app.app_context():
            self._setup_test_data()
            yield
            # Cleanup after each test
            self.db.session.rollback()
            self.db.session.query(Assignment).delete()
            self.db.session.commit()

    def _setup_test_data(self):
        """Override this in test classes to add specific test data"""
        pass
