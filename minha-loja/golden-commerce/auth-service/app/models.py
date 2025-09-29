from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from .database import Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    senha_hash = Column(String)
    funcao = Column(String, default="cliente")
    criado_at = Column(DateTime(timezone=True), server_default=func.now())

class Product(Base):
    __tablename__ = "produtos"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True)
    nome = Column(String, index=True)
    descricao = Column(String)
    preco = Column(Float)
    estoque = Column(Integer, default=0)
    criado_at = Column(DateTime(timezone=True), server_default=func.now())

class Order(Base):
    __tablename__ = "pedidos"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"))
    total = Column(Float)
    status = Column(String, default="pendente")
    criado_at = Column(DateTime(timezone=True), server_default=func.now())

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("pedidos.id"))
    product_id = Column(Integer, ForeignKey("produtos.id"))
    qty = Column(Integer)
    price = Column(Float)