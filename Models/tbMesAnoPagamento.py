from datetime import datetime
from collections import defaultdict
from sqlalchemy.event import listen
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.schema import (PrimaryKeyConstraint, ForeignKeyConstraint, CheckConstraint, UniqueConstraint)
from sqlalchemy import (create_engine, Column, Integer, BigInteger, String, Boolean, DateTime, CheckConstraint, DECIMAL, func, ForeignKey, event, DDL)

from Models import Base

class tbMesAnoPagamento(Base):
    __tablename__ = 'tbMesAnoPagamento'
    __tag__ = 'tbMesAnoPagamento'
    __table_args__ = (
        UniqueConstraint('mesPagamento', 'anoPagamento', 'codigoUsuario', name='UK_MesAnoUsuario_Pagamento'),
    )

    codigoMesAnoPagamento = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigoUsuario = Column(Integer, ForeignKey('tbUsuario.codigoUsuario'), nullable=False)
    mesPagamento = Column(Integer, nullable=False)
    anoPagamento = Column(Integer, nullable=False)

    # Relacionamentos
    usuario = relationship("tbUsuario", back_populates="mesesAnosPagamento")
    pagamentos = relationship("tbPagamento", back_populates="mesAnoPagamento")

    def __repr__(self):
        return f"<MesAnoPagamento(codigo={self.codigoMesAnoPagamento}, mes={self.mesPagamento}, ano={self.anoPagamento})>"