from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from config import load_config

config = load_config()

Base = declarative_base()

engine = create_engine(f'postgresql://{config.db.user}:{config.db.password}@{config.db.host}:{config.db.port}/{config.db.name}')

session_maker = sessionmaker(bind=engine)