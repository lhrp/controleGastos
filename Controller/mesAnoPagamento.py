from Models import tbMesAnoPagamento
from Models import gerarLog, conexaoBanco

from sqlalchemy import distinct

from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

engine = conexaoBanco()
sessaoLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class mesAnoPagamento():
    def __init__(self):
        self.codigoUsuario = None
        self.mesPagamento = None
        self.anoPagamento = None

    def cadastrarMesAnoPagamento(self, 
                                codigoUsuario: int,
                                mesPagamento: int,
                                anoPagamento: int) -> dict:
        
        sessao = sessaoLocal()
        try:
            # Verificar se já existe
            existe = sessao.query(tbMesAnoPagamento).filter_by(
                codigoUsuario=codigoUsuario,
                mesPagamento=mesPagamento,
                anoPagamento=anoPagamento
            ).first()
            
            if existe:
                return {
                    "status": "ERRO",
                    "mensagem": "Mês/Ano já cadastrado para este usuário."
                }
            
            novoMesAno = tbMesAnoPagamento()
            novoMesAno.codigoUsuario = codigoUsuario
            novoMesAno.mesPagamento = mesPagamento
            novoMesAno.anoPagamento = anoPagamento
            
            sessao.add(novoMesAno)
            sessao.commit()
            sessao.refresh(novoMesAno)
            
            gerarLog(
                mensagemLog=f"Mês/Ano {mesPagamento}/{anoPagamento} cadastrado para usuário {codigoUsuario}.",
                nivelLogger="info",
                classeLog="mesAnoPagamento - cadastrarMesAnoPagamento"
            )
            
            return {
                "status": "SUCESSO",
                "mensagem": "Mês/Ano cadastrado com sucesso.",
                "codigoMesAnoPagamento": novoMesAno.codigoMesAnoPagamento,
                "mesPagamento": novoMesAno.mesPagamento,
                "anoPagamento": novoMesAno.anoPagamento
            }
            
        except Exception as e:
            sessao.rollback()
            gerarLog(
                mensagemLog=f"Erro ao cadastrar mês/ano: {str(e)}",
                nivelLogger="error",
                classeLog="mesAnoPagamento - cadastrarMesAnoPagamento"
            )
            return {
                "status": "ERRO",
                "mensagem": f"Erro ao cadastrar: {str(e)}"
            }
        finally:
            sessao.close()
    
    def listarMesesAnosPagamento(self, codigoUsuario: int = None) -> list:
        
        sessao = sessaoLocal()
        try:
            query = sessao.query(tbMesAnoPagamento)
            
            if codigoUsuario:
                query = query.filter_by(codigoUsuario=codigoUsuario)
                    

            mesesAnos = query.order_by(
                tbMesAnoPagamento.anoPagamento.desc(),
                tbMesAnoPagamento.mesPagamento.desc()
            ).all()
            
            print(mesesAnos)

            return [{
                "codigoMesAnoPagamento": ma.codigoMesAnoPagamento,
                "codigoUsuario": ma.codigoUsuario,
                "mesPagamento": ma.mesPagamento,
                "anoPagamento": ma.anoPagamento
            } for ma in mesesAnos]
            
        except Exception as e:
            gerarLog(
                mensagemLog=f"Erro ao listar meses/anos: {str(e)}",
                nivelLogger="error",
                classeLog="mesAnoPagamento - listarMesesAnosPagamento"
            )
            return []
        finally:
            sessao.close()
    
    def consultarMesAnoPagamentoPorCodigo(self, codigoMesAnoPagamento: int, codigoUsuario: int = None) -> dict:
        """Consulta um mês/ano específico por código"""
        
        sessao = sessaoLocal()
        try:
            query = sessao.query(tbMesAnoPagamento).filter_by(codigoMesAnoPagamento=codigoMesAnoPagamento)
            
            if codigoUsuario:
                query = query.filter_by(codigoUsuario=codigoUsuario)
            
            mesAno = query.first()
            
            if mesAno:
                return {
                    "status": "SUCESSO",
                    "codigoMesAnoPagamento": mesAno.codigoMesAnoPagamento,
                    "codigoUsuario": mesAno.codigoUsuario,
                    "mesPagamento": mesAno.mesPagamento,
                    "anoPagamento": mesAno.anoPagamento
                }
            else:
                return {
                    "status": "ERRO",
                    "mensagem": "Mês/Ano não encontrado."
                }
                
        except Exception as e:
            gerarLog(
                mensagemLog=f"Erro ao consultar mês/ano: {str(e)}",
                nivelLogger="error",
                classeLog="mesAnoPagamento - consultarMesAnoPagamentoPorCodigo"
            )
            return {
                "status": "ERRO",
                "mensagem": f"Erro ao consultar: {str(e)}"
            }
        finally:
            sessao.close()
    
    def consultarAnosDisponiveis(self, codigoUsuario: int = None) -> list:
        """Retorna lista de anos disponíveis, ordenados do mais recente para o mais antigo"""
        
        sessao = sessaoLocal()
        try:
            query = sessao.query(distinct(tbMesAnoPagamento.anoPagamento))
            
            if codigoUsuario:
                query = query.filter_by(codigoUsuario=codigoUsuario)
            
            anos = query.order_by(tbMesAnoPagamento.anoPagamento.desc()).all()
            
            # Retornar lista de anos (desempacotando as tuplas)
            return [ano[0] for ano in anos]
            
        except Exception as e:
            gerarLog(
                mensagemLog=f"Erro ao consultar anos disponíveis: {str(e)}",
                nivelLogger="error",
                classeLog="mesAnoPagamento - consultarAnosDisponiveis"
            )
            return []
        finally:
            sessao.close()
    
    def consultarMesesDisponiveis(self, codigoUsuario: int = None, anoPagamento: int = None) -> list:
        """Retorna lista de meses disponíveis, opcionalmente filtrados por ano"""
        
        sessao = sessaoLocal()
        try:
            query = sessao.query(distinct(tbMesAnoPagamento.mesPagamento))
            
            if codigoUsuario:
                query = query.filter_by(codigoUsuario=codigoUsuario)
            
            if anoPagamento:
                query = query.filter_by(anoPagamento=anoPagamento)
            
            meses = query.order_by(tbMesAnoPagamento.mesPagamento).all()
            
            # Retornar lista de meses (desempacotando as tuplas)
            return [mes[0] for mes in meses]
            
        except Exception as e:
            gerarLog(
                mensagemLog=f"Erro ao consultar meses disponíveis: {str(e)}",
                nivelLogger="error",
                classeLog="mesAnoPagamento - consultarMesesDisponiveis"
            )
            return []
        finally:
            sessao.close()
    
    def consultarMesAnoPagamentoPorCodigo(self, codigoMesAnoPagamento: int, codigoUsuario: int = None) -> dict:
        
        sessao = sessaoLocal()
        try:
            query = sessao.query(tbMesAnoPagamento).filter_by(codigoMesAnoPagamento=codigoMesAnoPagamento)
            
            if codigoUsuario:
                query = query.filter_by(codigoUsuario=codigoUsuario)
            
            mesAno = query.first()
            
            if mesAno:
                return {
                    "status": "SUCESSO",
                    "codigoMesAnoPagamento": mesAno.codigoMesAnoPagamento,
                    "codigoUsuario": mesAno.codigoUsuario,
                    "mesPagamento": mesAno.mesPagamento,
                    "anoPagamento": mesAno.anoPagamento
                }
            else:
                return {
                    "status": "ERRO",
                    "mensagem": "Mês/Ano não encontrado."
                }
                
        except Exception as e:
            gerarLog(
                mensagemLog=f"Erro ao consultar mês/ano: {str(e)}",
                nivelLogger="error",
                classeLog="mesAnoPagamento - consultarMesAnoPagamentoPorCodigo"
            )
            return {
                "status": "ERRO",
                "mensagem": f"Erro ao consultar: {str(e)}"
            }
        finally:
            sessao.close()
    
    def removerMesAnoPagamento(self, codigoMesAnoPagamento: int, codigoUsuario: int) -> dict:
        
        sessao = sessaoLocal()
        try:
            mesAno = sessao.query(tbMesAnoPagamento).filter_by(
                codigoMesAnoPagamento=codigoMesAnoPagamento,
                codigoUsuario=codigoUsuario
            ).first()
            
            if not mesAno:
                return {
                    "status": "ERRO",
                    "mensagem": "Mês/Ano não encontrado."
                }
            
            sessao.delete(mesAno)
            sessao.commit()
            
            gerarLog(
                mensagemLog=f"Mês/Ano {codigoMesAnoPagamento} removido.",
                nivelLogger="info",
                classeLog="mesAnoPagamento - removerMesAnoPagamento"
            )
            
            return {
                "status": "SUCESSO",
                "mensagem": "Mês/Ano removido com sucesso."
            }
            
        except Exception as e:
            sessao.rollback()
            gerarLog(
                mensagemLog=f"Erro ao remover mês/ano: {str(e)}",
                nivelLogger="error",
                classeLog="mesAnoPagamento - removerMesAnoPagamento"
            )
            return {
                "status": "ERRO",
                "mensagem": f"Erro ao remover: {str(e)}"
            }
        finally:
            sessao.close()