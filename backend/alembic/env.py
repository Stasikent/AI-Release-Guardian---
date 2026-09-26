from alembic import context
from sqlalchemy import engine_from_config, pool
from app.db import Base, DATABASE_URL
from app.models import db_models  # noqa: F401
config=context.config
config.set_main_option("sqlalchemy.url",DATABASE_URL)
target_metadata=Base.metadata
def offline():
    context.configure(url=DATABASE_URL,target_metadata=target_metadata,literal_binds=True,compare_type=True)
    with context.begin_transaction(): context.run_migrations()
def online():
    engine=engine_from_config(config.get_section(config.config_ini_section),prefix="sqlalchemy.",poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection,target_metadata=target_metadata,compare_type=True)
        with context.begin_transaction(): context.run_migrations()
offline() if context.is_offline_mode() else online()
