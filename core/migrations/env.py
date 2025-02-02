from __future__ import with_statement
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
import logging

# Add your models here
from core.models.assignments import Assignment
from core.models.teachers import Teacher
from core.models.students import Student
from core import db

config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

def run_migrations_online():
    """Run migrations in 'online' mode."""
    engine = engine_from_config(
                config.get_section(config.config_ini_section),
                prefix='sqlalchemy.',
                poolclass=pool.NullPool)

    connection = engine.connect()
    context.configure(
                connection=connection,
                target_metadata=db.metadata
                )

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()

run_migrations_online()
