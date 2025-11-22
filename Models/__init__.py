# Conexão com o banco de dados

from .conexaoBD import Conexao, Base

# Importando os modelos de tabelas
from .tbUsuario import tbUsuario
from .tbTipoPagamento import tbTipoPagamento
from .tbMesAnoPagamento import tbMesAnoPagamento
from .tbPagamento import tbPagamento

# Importando funções auxiliares
from .fnLog import GestaoLogs

# Instanciando funções
gerarLog = GestaoLogs().gerarLog
conexaoBanco = Conexao().retornaConexao

Base.metadata.create_all(conexaoBanco())