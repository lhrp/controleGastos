# Conexão com o banco de dados

from .conexaoBD import Conexao, Base

# Importando os modelos de tabelas
from .tbTipoPagamento import tbTipoPagamento

# Importando funções auxiliares
from .fnLog import GestaoLogs

# Instanciando funções
gerarLog = GestaoLogs().gerarLog
conexaoBanco = Conexao().retornaConexao