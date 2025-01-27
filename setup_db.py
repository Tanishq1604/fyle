from sqlalchemy import create_engine
from models import Base, User, Teacher  # Import other models as well

engine = create_engine('sqlite:///core/store.sqlite3')

Base.metadata.create_all(engine)
