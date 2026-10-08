
from sqlalchemy import create_engine
from sqlalchemy .orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
sqlalchemy_database_url="sqlite:///./movies.db"

engine=create_engine(sqlalchemy_database_url,connect_args={"check_same_thread": False})

sessionlocal=sessionmaker(autoflush=False,bind=engine)
Base=declarative_base()