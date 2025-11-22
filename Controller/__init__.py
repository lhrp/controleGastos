
# Conexão com o banco de dados

from .tipoPagamento import tipoPagamento
from .mesAnoPagamento import mesAnoPagamento
from .pagamento import pagamento
from .usuario import usuario

funcoesTipoPagamento = {
    "cadastrar" : tipoPagamento().cadastrarTipoPagamento,
    "listar" : tipoPagamento().listarTiposPagamento,
    "atualizar" : tipoPagamento().atualizarTipoPagamento,
    "remover" : tipoPagamento().removerTipoPagamento
}

funcoesMesAnoPagamento = {
    "cadastrar" : mesAnoPagamento().cadastrarMesAnoPagamento,
    "consultar" : mesAnoPagamento().consultarMesAnoPagamentoPorCodigo,
    "consultarAnosDisponiveis": mesAnoPagamento().consultarAnosDisponiveis,
    "consultarPorCodigo" : mesAnoPagamento().consultarMesAnoPagamentoPorCodigo,
    "listar" : mesAnoPagamento().listarMesesAnosPagamento,
    "remover" : mesAnoPagamento().removerMesAnoPagamento
}

funcoesPagamento = {
    "cadastrar" : pagamento().cadastrarPagamento,
    "listar" : pagamento().listarPagamentos,
    "consultarPagamentoPorCodigo" : pagamento().consultarPagamentoPorCodigo,
    "atualizar" : pagamento().atualizarPagamento,
    "remover" : pagamento().removerPagamento
}

funcoesUsuario = {
    "cadastrar": usuario().cadastrarUsuario,
    "autenticar": usuario().autenticarUsuario,
    "listar": usuario().listarUsuarios,
    "atualizarSenha": usuario().atualizarSenha
}