from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# Connect to a PostgresSQL database in a FastAPI application
SQLALCHEMY_DATABASE_URI = "postgresql://todoappdb_deployment_user:wtTltVtXLG7f19R1NNdvLFpICoQPx7B8@dpg-d6td9qq4d50c73c8a6d0-a.virginia-postgres.render.com/todoappdb_deployment"

# Connect to an SQLite database in a FastAPI application
# SQLALCHEMY_DATABASE_URI = "sqlite:///./todoapppro.db"

# Connect to a MySQL database in a FastAPI application
# SQLALCHEMY_DATABASE_URI = "mysql://root:root@127.0.0.1:3306/TodoApplicationDatabase"

engine = create_engine(SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False})
# Comment out the above line and uncomment the below line to connect to a MySQL or Postgres SQL database
# engine = create_engine(SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
