from core.models.base import BaseModel
from core import db
from core.libs import helpers


class Principal(BaseModel):
    __tablename__ = 'principals'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
