from datetime import datetime
from collections import defaultdict
from sqlalchemy.event import listen
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.schema import (PrimaryKeyConstraint, ForeignKeyConstraint, CheckConstraint, UniqueConstraint)
from sqlalchemy import (create_engine, Column, Integer, BigInteger, String, Boolean, DateTime, CheckConstraint, DECIMAL, func, ForeignKey, event, DDL)

from Models import Base

class tbTipoPagamento(Base):
    __tablename__ = 'tbTipoPagamento'
    __tag__ = 'tbTipoPagamento'
    __table_args__ = (
        UniqueConstraint('codigoUsuario', 'nomeTipoPagamento', 'opcaoTipoPagamento', name='UK_Usuario_NomeOpcao_TipoPagamento'),
    )

    codigoTipoPagamento = Column(Integer, primary_key=True, index=True, autoincrement=True, unique=True)
    codigoUsuario = Column(Integer, ForeignKey('tbUsuario.codigoUsuario'), nullable=False)
    nomeTipoPagamento = Column(String(50), nullable=False)
    opcaoTipoPagamento = Column(String(20), nullable=False)
    
    # Relacionamentos
    usuario = relationship("tbUsuario", back_populates="tiposPagamento")
    pagamentos = relationship("tbPagamento", back_populates="tipoPagamento")

    def repr(self):
        return f'<{self.__tag__} {self.codigoTipoPagamento} - {self.nomeTipoPagamento} - {self.opcaoTipoPagamento}>'
    
    def __repr__(self):
        return f"<TipoPagamento(codigo={self.codigoTipoPagamento}, nome='{self.nomeTipoPagamento}')>"