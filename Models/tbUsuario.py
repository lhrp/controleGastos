from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from Models import Base

class tbUsuario(Base):
    __tablename__ = 'tbUsuario'
    __tag__ = 'tbUsuario'
    
    codigoUsuario = Column(Integer, primary_key=True, autoincrement=True)
    nomeUsuario = Column(String(100), nullable=False)
    emailUsuario = Column(String(100), unique=True, nullable=False)
    senhaUsuario = Column(String(255), nullable=False)  # Senha criptografada
    ativoUsuario = Column(Boolean, default=True)
    dataCadastroUsuario = Column(DateTime, default=datetime.now)
    dataUltimoAcessoUsuario = Column(DateTime)
    
    # Relacionamentos
    tiposPagamento = relationship("tbTipoPagamento", back_populates="usuario", cascade="all, delete-orphan")
    mesesAnosPagamento = relationship("tbMesAnoPagamento", back_populates="usuario", cascade="all, delete-orphan")
    pagamentos = relationship("tbPagamento", back_populates="usuario", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Usuario(codigo={self.codigoUsuario}, nome='{self.nomeUsuario}', email='{self.emailUsuario}')>"