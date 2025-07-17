from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Users(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship with customers
    customers = relationship("Musteri", back_populates="owner", cascade="all, delete-orphan")

class Musteri(Base):
    __tablename__ = "musteri"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    
    # Customer fields with appropriate indexing
    kategori = Column(String(100), index=True)
    firmaAdi = Column(String(200), index=True, nullable=False)
    email = Column(String(100), index=True)
    yetkili = Column(String(100))
    ulke = Column(String(100), index=True)
    sehir = Column(String(100), index=True)
    adres = Column(Text)
    web = Column(String(255))
    durum = Column(String(50), index=True)
    musteri_temsilci = Column(String(100))
    kartvizit = Column(String(255))
    Bayi = Column(String(100))
    ilkSatisYili = Column(Date, index=True)
    sonSatisYili = Column(Date, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship with user
    owner = relationship("Users", back_populates="customers")