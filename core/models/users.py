from core.models.base import BaseModel
from core import db
from core.libs import helpers


class User(BaseModel):
    __tablename__ = 'users'
    
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # Define relationships
    student = db.relationship('Student', uselist=False, foreign_keys='Student.user_id')
    teacher = db.relationship('Teacher', uselist=False, foreign_keys='Teacher.user_id')
    principal = db.relationship('Principal', uselist=False, foreign_keys='Principal.user_id')

    def __init__(self, username, email, **kwargs):
        super().__init__(**kwargs)
        self.username = username
        self.email = email

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @classmethod
    def filter(cls, *criterion):
        db_query = db.session.query(cls)
        return db_query.filter(*criterion)

    @classmethod
    def get_by_id(cls, _id):
        return cls.filter(cls.id == _id).first()

    @classmethod
    def get_by_email(cls, email):
        return cls.filter(cls.email == email).first()
