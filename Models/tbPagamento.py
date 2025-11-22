from datetime import datetime
from collections import defaultdict
from sqlalchemy.event import listen
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.schema import (PrimaryKeyConstraint, ForeignKeyConstraint, CheckConstraint)
from sqlalchemy import (create_engine, Column, Integer, BigInteger, String, Boolean, DateTime, CheckConstraint, DECIMAL, func, ForeignKey, event, DDL, Float, Date)

from Models import Base

class tbPagamento(Base):
    __tablename__ = 'tbPagamento'
    __tag__ = 'tbPagamento'
    __table_args__ = (
        ForeignKeyConstraint(['codigoTipoPagamento'], ['tbTipoPagamento.codigoTipoPagamento']),
        ForeignKeyConstraint(['codigoMesAnoPagamento'], ['tbMesAnoPagamento.codigoMesAnoPagamento'])
    )

    codigoPagamento = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigoUsuario = Column(Integer, ForeignKey('tbUsuario.codigoUsuario'), nullable=False)
    codigoTipoPagamento = Column(Integer, ForeignKey('tbTipoPagamento.codigoTipoPagamento'), nullable=False)
    codigoMesAnoPagamento = Column(Integer, ForeignKey('tbMesAnoPagamento.codigoMesAnoPagamento'), nullable=False)
    descricaoPagamento = Column(String(100), nullable=False)
    valorPagamento = Column(Float, nullable=False)
    vencimentoPagamento = Column(Date, nullable=False)
    numeroParcelaPagamento = Column(Integer, default=1)
    statusPagamento = Column(Boolean, default=False)
    dataInclusao = Column(DateTime, default=func.now())
    dataAlteracao = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relacionamentos
    usuario = relationship("tbUsuario", back_populates="pagamentos")
    tipoPagamento = relationship("tbTipoPagamento", back_populates="pagamentos")
    mesAnoPagamento = relationship("tbMesAnoPagamento", back_populates="pagamentos")

    def __repr__(self):
        return f"<Pagamento(codigo={self.codigoPagamento}, descricao='{self.descricaoPagamento}', valor={self.valorPagamento})>"