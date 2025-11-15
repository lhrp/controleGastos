from datetime import datetime
from collections import defaultdict
from sqlalchemy.event import listen
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.schema import (PrimaryKeyConstraint, ForeignKeyConstraint, CheckConstraint)
from sqlalchemy import (create_engine, Column, Integer, BigInteger, String, Boolean, DateTime, CheckConstraint, DECIMAL, func, ForeignKey, event, DDL)

from Models import Base

class tbTipoPagamento(Base):
    __tablename__ = 'tbTipoPagamento'
    __tag__ = 'tbTipoPagamento'

    codigoTipoPagamento = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nomeTipoPagamento = Column(String(100), nullable=False)
    opcaoTipoPagamento = Column(Integer, nullable=False)
    # dataInclusao = Column(DateTime, default=func.now())
    # dataAlteracao = Column(DateTime, default=func.now(), onupdate=func.now())

    def repr(self):
        return f'<{self.__tag__} {self.codigoTipoPagamento} - {self.nomeTipoPagamento} - {self.opcaoTipoPagamento}>'
    
    def init(self, nomeTipoPagamento, opcaoTipoPagamento):
        self.nomeTipoPagamento = nomeTipoPagamento
        self.opcaoTipoPagamento = opcaoTipoPagamento