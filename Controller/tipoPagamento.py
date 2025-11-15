from Models import tbTipoPagamento
from Models import gerarLog, conexaoBanco

from sqlalchemy.orm import sessionmaker

engine = conexaoBanco()
sessaoLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class tipoPagamento():
    def __init__(self):
        self.nomeTipoPagamento = None
        self.opcaoTipoPagamento = None

    def cadastrarTipoPagamento(self, nomeTipoPagamento: str, opcaoTipoPagamento: int) -> dict:
        sessao = sessaoLocal()
        try:
            novoTipoPagamento = tbTipoPagamento()
            novoTipoPagamento.nomeTipoPagamento = nomeTipoPagamento
            novoTipoPagamento.opcaoTipoPagamento = opcaoTipoPagamento      
            sessao.add(novoTipoPagamento)
            sessao.commit()
            sessao.refresh(novoTipoPagamento)
            sessao.close()

            gerarLog(mensagemLog=f"Tipo de pagamento '{nomeTipoPagamento}' cadastrado com sucesso.", nivelLogger="info", classeLog="tipoPagamento - cadastrarTipoPagamento")

            return {
                "status": "SUCESSO",
                "mensagem": "Tipo de pagamento cadastrado com sucesso.",
                "codigoUsuario": novoTipoPagamento.codigoTipoPagamento,
                "nomeTipoPagamento": novoTipoPagamento.nomeTipoPagamento,
                "opcaoTipoPagamento": novoTipoPagamento.opcaoTipoPagamento                
            }        
        except Exception as e:
            sessao.rollback()
            gerarLog(mensagemLog=f"Erro ao cadastrar tipo de pagamento '{nomeTipoPagamento}': {str(e)}", nivelLogger="error", classeLog="tipoPagamento - cadastrarTipoPagamento")
            return {
                "status": "ERRO",
                "mensagem": f"Erro ao cadastrar tipo de pagamento: {str(e)}"
            }
        finally:
            sessao.close()

    def listarTiposPagamento(self) -> list:
        sessao = sessaoLocal()
        try:
            tiposPagamento = sessao.query(tbTipoPagamento).all()
            resultado = []
            for tipo in tiposPagamento:
                resultado.append({
                    "codigoTipoPagamento": tipo.codigoTipoPagamento,
                    "nomeTipoPagamento": tipo.nomeTipoPagamento,
                    "opcaoTipoPagamento": tipo.opcaoTipoPagamento
                })
            gerarLog(mensagemLog="Listagem de tipos de pagamento realizada com sucesso.", nivelLogger="info", classeLog="tipoPagamento - listarTiposPagamento")
            return resultado
        except Exception as e:
            gerarLog(mensagemLog=f"Erro ao listar tipos de pagamento: {str(e)}", nivelLogger="error", classeLog="tipoPagamento - listarTiposPagamento")
            return []
        finally:
            sessao.close()

    def atualizarTipoPagamento(self, codigoTipoPagamento: int, nomeTipoPagamento: str = None, opcaoTipoPagamento: int = None) -> dict:
        sessao = sessaoLocal()
        try:
            tipoPagamento = sessao.query(tbTipoPagamento).filter(tbTipoPagamento.codigoTipoPagamento == codigoTipoPagamento).first()
            if not tipoPagamento:
                gerarLog(mensagemLog=f"Tipo de pagamento '{codigoTipoPagamento}' não encontrado para atualização.", nivelLogger="warning", classeLog="tipoPagamento - atualizarTipoPagamento")
                return {
                    "status": "ERRO",
                    "mensagem": "Tipo de pagamento não encontrado."
                }
            if nomeTipoPagamento:
                tipoPagamento.nomeTipoPagamento = nomeTipoPagamento
            if opcaoTipoPagamento is not None:
                tipoPagamento.opcaoTipoPagamento = opcaoTipoPagamento
            sessao.commit()
            gerarLog(mensagemLog=f"Tipo de pagamento '{codigoTipoPagamento}' atualizado com sucesso.", nivelLogger="info", classeLog="tipoPagamento - atualizarTipoPagamento")
            return {
                "status": "SUCESSO",
                "mensagem": "Tipo de pagamento atualizado com sucesso."
            }
        except Exception as e:
            sessao.rollback()
            gerarLog(mensagemLog=f"Erro ao atualizar tipo de pagamento '{codigoTipoPagamento}': {str(e)}", nivelLogger="error", classeLog="tipoPagamento - atualizarTipoPagamento")
            return {
                "status": "ERRO",
                "mensagem": f"Erro ao atualizar tipo de pagamento: {str(e)}"
            }
        finally:
            sessao.close()

    def removerTipoPagamento(self, codigoTipoPagamento: int) -> dict:
        sessao = sessaoLocal()
        try:
            tipoPagamento = sessao.query(tbTipoPagamento).filter(tbTipoPagamento.codigoTipoPagamento == codigoTipoPagamento).first()
            if not tipoPagamento:
                gerarLog(mensagemLog=f"Tipo de pagamento '{codigoTipoPagamento}' não encontrado para remoção.", nivelLogger="warning", classeLog="tipoPagamento - removerTipoPagamento")
                return {
                    "status": "ERRO",
                    "mensagem": "Tipo de pagamento não encontrado."
                }
            sessao.delete(tipoPagamento)
            sessao.commit()
            gerarLog(mensagemLog=f"Tipo de pagamento '{codigoTipoPagamento}' removido com sucesso.", nivelLogger="info", classeLog="tipoPagamento - removerTipoPagamento")
            return {
                "status": "SUCESSO",
                "mensagem": "Tipo de pagamento removido com sucesso."
            }
        except Exception as e:
            sessao.rollback()
            gerarLog(mensagemLog=f"Erro ao remover tipo de pagamento '{codigoTipoPagamento}': {str(e)}", nivelLogger="error", classeLog="tipoPagamento - removerTipoPagamento")
            return {
                "status": "ERRO",
                "mensagem": f"Erro ao remover tipo de pagamento: {str(e)}"
            }
        finally:
            sessao.close()