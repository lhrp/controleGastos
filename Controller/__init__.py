# Conexão com o banco de dados

from .tipoPagamento import tipoPagamento

funcoesTipoPagamento = {
    "cadastrar" : tipoPagamento().cadastrarTipoPagamento,
    "listar" : tipoPagamento().listarTiposPagamento,
    "atualizar" : tipoPagamento().atualizarTipoPagamento,
    "remover" : tipoPagamento().removerTipoPagamento
}