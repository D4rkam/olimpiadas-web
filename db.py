# Importamos SQLAlchemy para definir y manejar el modelo de la base de datos
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
# Base declarativa de SQLAlchemy para definir modelos
from sqlalchemy.ext.declarative import declarative_base
# Manejador de sesiones para interactuar con la base de datos
from sqlalchemy.orm import sessionmaker

user = "root"
password = ""
host = "127.0.0.1"
port = "3307"
database = "olimpiadas"

# URL de la base de datos SQLite
SQLALCHEMY_DATABASE_URL = f"mysql://{user}:{password}@{host}:{port}/{database}"
# Crear el motor de la base de datos
engine = create_engine(SQLALCHEMY_DATABASE_URL)
# Crear la sesión local para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()  # Base para definir los modelos de la base de datos
