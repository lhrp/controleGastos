from Models import tbTipoPagamento
from Models import gerarLog, conexaoBanco

from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

engine = conexaoBanco()
sessaoLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class tipoPagamento():
    def __init__(self):
        self.codigoTipoPagamento = None
        self.codigoUsuario = None
        self.nomeTipoPagamento = None
        self.opcaoTipoPagamento = None
    
    def cadastrarTipoPagamento(self, 
                               codigoUsuario: int,
                               nomeTipoPagamento: str, 
                               opcaoTipoPagamento: str) -> dict:
        
        sessao = sessaoLocal()
        try:
            novoTipoPagamento = tbTipoPagamento()
            novoTipoPagamento.codigoUsuario = codigoUsuario
            novoTipoPagamento.nomeTipoPagamento = nomeTipoPagamento
            novoTipoPagamento.opcaoTipoPagamento = opcaoTipoPagamento
            
            sessao.add(novoTipoPagamento)
            sessao.commit()
            sessao.refresh(novoTipoPagamento)
            
            gerarLog(
                mensagemLog=f"Tipo de pagamento '{nomeTipoPagamento}' cadastrado para usuário {codigoUsuario}.",
                nivelLogger="info",
                classeLog="tipoPagamento - cadastrarTipoPagamento"
            )
            
            return {
                "status": "SUCESSO",
                "mensagem": "Tipo de pagamento cadastrado com sucesso.",
                "codigoTipoPagamento": novoTipoPagamento.codigoTipoPagamento,
                "nomeTipoPagamento": novoTipoPagamento.nomeTipoPagamento,
                "opcaoTipoPagamento": novoTipoPagamento.opcaoTipoPagamento
            }
            
        except Exception as e:
            sessao.rollback()
            gerarLog(
                mensagemLog=f"Erro ao cadastrar tipo de pagamento: {str(e)}",
                nivelLogger="error",
                classeLog="tipoPagamento - cadastrarTipoPagamento"
            )
            return {
                "status": "ERRO",
                "mensagem": f"Erro ao cadastrar tipo de pagamento: {str(e)}"
            }
        finally:
            sessao.close()
    
    def listarTiposPagamento(self, codigoUsuario: int = None) -> list:
        
        sessao = sessaoLocal()
        try:
            query = sessao.query(tbTipoPagamento)
            
            if codigoUsuario:
                query = query.filter_by(codigoUsuario=codigoUsuario)
            
            tiposPagamento = query.all()
            
            return [{
                "codigoTipoPagamento": tp.codigoTipoPagamento,
                "codigoUsuario": tp.codigoUsuario,
                "nomeTipoPagamento": tp.nomeTipoPagamento,
                "opcaoTipoPagamento": tp.opcaoTipoPagamento
            } for tp in tiposPagamento]
            
        except Exception as e:
            gerarLog(
                mensagemLog=f"Erro ao listar tipos de pagamento: {str(e)}",
                nivelLogger="error",
                classeLog="tipoPagamento - listarTiposPagamento"
            )
            return []
        finally:
            sessao.close()
    
    def consultarTipoPagamentoPorCodigo(self, codigoTipoPagamento: int, codigoUsuario: int = None) -> dict:
        
        sessao = sessaoLocal()
        try:
            query = sessao.query(tbTipoPagamento).filter_by(codigoTipoPagamento=codigoTipoPagamento)
            
            if codigoUsuario:
                query = query.filter_by(codigoUsuario=codigoUsuario)
            
            tipoPagamento = query.first()
            
            if tipoPagamento:
                return {
                    "status": "SUCESSO",
                    "codigoTipoPagamento": tipoPagamento.codigoTipoPagamento,
                    "codigoUsuario": tipoPagamento.codigoUsuario,
                    "nomeTipoPagamento": tipoPagamento.nomeTipoPagamento,
                    "opcaoTipoPagamento": tipoPagamento.opcaoTipoPagamento
                }
            else:
                return {
                    "status": "ERRO",
                    "mensagem": "Tipo de pagamento não encontrado."
                }
                
        except Exception as e:
            gerarLog(
                mensagemLog=f"Erro ao consultar tipo de pagamento: {str(e)}",
                nivelLogger="error",
                classeLog="tipoPagamento - consultarTipoPagamentoPorCodigo"
            )
            return {
                "status": "ERRO",
                "mensagem": f"Erro ao consultar: {str(e)}"
            }
        finally:
            sessao.close()
    
    def atualizarTipoPagamento(self, 
                              codigoTipoPagamento: int,
                              codigoUsuario: int,
                              nomeTipoPagamento: str = None,
                              opcaoTipoPagamento: str = None) -> dict:
        
        sessao = sessaoLocal()
        try:
            tipoPagamento = sessao.query(tbTipoPagamento).filter_by(
                codigoTipoPagamento=codigoTipoPagamento,
                codigoUsuario=codigoUsuario
            ).first()
            
            if not tipoPagamento:
                return {
                    "status": "ERRO",
                    "mensagem": "Tipo de pagamento não encontrado."
                }
            
            if nomeTipoPagamento:
                tipoPagamento.nomeTipoPagamento = nomeTipoPagamento
            if opcaoTipoPagamento:
                tipoPagamento.opcaoTipoPagamento = opcaoTipoPagamento
            
            sessao.commit()
            
            gerarLog(
                mensagemLog=f"Tipo de pagamento {codigoTipoPagamento} atualizado.",
                nivelLogger="info",
                classeLog="tipoPagamento - atualizarTipoPagamento"
            )
            
            return {
                "status": "SUCESSO",
                "mensagem": "Tipo de pagamento atualizado com sucesso."
            }
            
        except Exception as e:
            sessao.rollback()
            gerarLog(
                mensagemLog=f"Erro ao atualizar tipo de pagamento: {str(e)}",
                nivelLogger="error",
                classeLog="tipoPagamento - atualizarTipoPagamento"
            )
            return {
                "status": "ERRO",
                "mensagem": f"Erro ao atualizar: {str(e)}"
            }
        finally:
            sessao.close()
    
    def removerTipoPagamento(self, codigoTipoPagamento: int, codigoUsuario: int) -> dict:
        
        sessao = sessaoLocal()
        try:
            tipoPagamento = sessao.query(tbTipoPagamento).filter_by(
                codigoTipoPagamento=codigoTipoPagamento,
                codigoUsuario=codigoUsuario
            ).first()
            
            if not tipoPagamento:
                return {
                    "status": "ERRO",
                    "mensagem": "Tipo de pagamento não encontrado."
                }
            
            sessao.delete(tipoPagamento)
            sessao.commit()
            
            gerarLog(
                mensagemLog=f"Tipo de pagamento {codigoTipoPagamento} removido.",
                nivelLogger="info",
                classeLog="tipoPagamento - removerTipoPagamento"
            )
            
            return {
                "status": "SUCESSO",
                "mensagem": "Tipo de pagamento removido com sucesso."
            }
            
        except Exception as e:
            sessao.rollback()
            gerarLog(
                mensagemLog=f"Erro ao remover tipo de pagamento: {str(e)}",
                nivelLogger="error",
                classeLog="tipoPagamento - removerTipoPagamento"
            )
            return {
                "status": "ERRO",
                "mensagem": f"Erro ao remover: {str(e)}"
            }
        finally:
            sessao.close()