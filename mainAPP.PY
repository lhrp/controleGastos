from Models import gerarLog, conexaoBanco, Base
from Controller import funcoesTipoPagamento

Base.metadata.create_all(conexaoBanco())



#funcoesTipoPagamento.get("cadastrar")(nomeTipoPagamento="Parcelado", opcaoTipoPagamento=2)