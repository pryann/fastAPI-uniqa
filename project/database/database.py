from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./real_app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

# create datatbase engine, not connecting yet
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# every request create a new session
# autocommit=False: we will commit manually
# autoflush=False: we will flush manually
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# create a base class for our models
Base = declarative_base()


def get_session():
    with Session() as session:
        yield session
