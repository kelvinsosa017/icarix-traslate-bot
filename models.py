from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import os

Base = declarative_base()

# Obtener la URL de la base de datos desde las variables de entorno
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "postgresql://neondb_owner:npg_nUSyq7lVMJk4@ep-steep-glade-a43chwal.us-east-1.aws.neon.tech/neondb?sslmode=require"

class ActiveTopic(Base):
    """Tabla para almacenar los temas activos en chats"""
    __tablename__ = "active_topics"
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, nullable=False)
    topic_id = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Restricción de unicidad para chat_id y topic_id
    __table_args__ = (UniqueConstraint('chat_id', 'topic_id', name='uix_chat_topic'),)
    
    def __repr__(self):
        return f"<ActiveTopic(chat_id={self.chat_id}, topic_id={self.topic_id}, is_active={self.is_active})>"


class UserLanguage(Base):
    """Tabla para almacenar el idioma preferido de cada usuario"""
    __tablename__ = "user_languages"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, unique=True)
    language_code = Column(String(10), nullable=False)
    
    def __repr__(self):
        return f"<UserLanguage(user_id={self.user_id}, language_code={self.language_code})>"


class UserChatMapping(Base):
    """Tabla para almacenar la relación entre usuarios y chats"""
    __tablename__ = "user_chat_mappings"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    chat_id = Column(Integer, nullable=False)
    
    # Restricción de unicidad para user_id y chat_id
    __table_args__ = (UniqueConstraint('user_id', 'chat_id', name='uix_user_chat'),)
    
    def __repr__(self):
        return f"<UserChatMapping(user_id={self.user_id}, chat_id={self.chat_id})>"


# Inicializar el motor de la base de datos
engine = create_engine(DATABASE_URL)

# Crear una sesión
Session = sessionmaker(bind=engine)

# Crear todas las tablas
def create_tables():
    Base.metadata.create_all(engine)