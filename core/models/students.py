from core.models.base import BaseModel
from core import db
from core.libs import helpers

class Student(BaseModel):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=helpers.get_utc_now, nullable=False)
    updated_at = db.Column(db.TIMESTAMP(timezone=True), default=helpers.get_utc_now, nullable=False, onupdate=helpers.get_utc_now)
    
    # Define relationships
    user = db.relationship('User', back_populates='student')
    assignments = db.relationship('Assignment', backref='student_ref', lazy='dynamic')

    @classmethod
    def filter(cls, *criterion):
        db_query = db.session.query(cls)
        return db_query.filter(*criterion)

    def __repr__(self):
        return f'<Student {self.id}>'
