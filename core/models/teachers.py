from core.models.base import BaseModel
from core import db
from core.libs import helpers


class Teacher(BaseModel):
    __tablename__ = 'teachers'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Define relationships
    assignments = db.relationship('Assignment', backref='teacher_ref', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @classmethod
    def filter(cls, *criterion):
        db_query = db.session.query(cls)
        return db_query.filter(*criterion)

    def __repr__(self):
        return f'<Teacher {self.id}>'
