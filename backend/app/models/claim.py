from sqlalchemy import Column, Integer, String, Text, Float, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    texto_original = Column(Text, nullable=True)
    texto_limpio = Column(Text, nullable=True)
    label = Column(String(10), nullable=False)
    score_alta = Column(Float, nullable=False, default=0.0)
    score_media = Column(Float, nullable=False, default=0.0)
    score_baja = Column(Float, nullable=False, default=0.0)
    fuente = Column(String(10), nullable=False)
    timestamp = Column(DateTime, default=func.now())
