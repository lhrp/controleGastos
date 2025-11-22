from Models import gerarLog, conexaoBanco
from Models import tbPagamento, tbMesAnoPagamento
from Controller import mesAnoPagamento

from sqlalchemy.orm import sessionmaker
from datetime import date, datetime
from calendar import monthrange

engine = conexaoBanco()
sessaoLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def conversaoParaDate(data) -> date:
    if isinstance(data, date):
        return data
    elif isinstance(data, datetime):
        return data.date()
    elif isinstance(data, str):
        return datetime.strptime(data, "%Y-%m-%d").date()
    return data

def consultarMesAnoPagamento(vencimento: date, codigoUsuario: int) -> int:
    sessao = sessaoLocal()
    try:
        mesAno = sessao.query(tbMesAnoPagamento).filter_by(
            codigoUsuario=codigoUsuario,
            mesPagamento=vencimento.month,
            anoPagamento=vencimento.year
        ).first()
        
        if mesAno:
            return mesAno.codigoMesAnoPagamento
        
        # Se não existir, criar automaticamente
        novoMesAno = tbMesAnoPagamento()
        novoMesAno.codigoUsuario = codigoUsuario
        novoMesAno.mesPagamento = vencimento.month
        novoMesAno.anoPagamento = vencimento.year
        
        sessao.add(novoMesAno)
        sessao.commit()
        sessao.refresh(novoMesAno)
        
        return novoMesAno.codigoMesAnoPagamento
        
    except Exception as e:
        gerarLog(
            mensagemLog=f"Erro ao consultar/criar mês/ano: {str(e)}",
            nivelLogger="error",
            classeLog="pagamento - consultarMesAnoPagamento"
        )
        return None
    finally:
        sessao.close()

class pagamento():
    def __init__(self):
        self.descricaoPagamento = None
        self.codigoTipoPagamento = None
        self.codigoMesAnoPagamento = None
        self.vencimentoPagamento = None
        self.valorPagamento = None
        self.numeroParcelaPagamento = None
        self.statusPagamento = None
    
    def cadastrarPagamento(self, 
                           codigoUsuario: int,
                           descricaoPagamento: str, 
                           codigoTipoPagamento: int, 
                           valorPagamento: float, 
                           vencimentoPagamento: date = datetime.now().date(),
                           numeroParcelaPagamento: int = 1, 
                           statusPagamento: bool = False
                          ) -> dict:
        sessao = sessaoLocal()
        try:
            # Se for tipo Fixo (código 2), cadastrar para todos os meses/anos disponíveis
            if codigoTipoPagamento == 2:
                return self.cadastrarPagamentoFixo(
                    codigoUsuario=codigoUsuario,
                    descricaoPagamento=descricaoPagamento,
                    codigoTipoPagamento=codigoTipoPagamento,
                    valorPagamento=valorPagamento,
                    vencimentoPagamento=vencimentoPagamento,
                    statusPagamento=statusPagamento
                )
            
            novoPagamento = tbPagamento()
            novoPagamento.codigoUsuario = codigoUsuario
            novoPagamento.descricaoPagamento = descricaoPagamento
            novoPagamento.codigoTipoPagamento = codigoTipoPagamento
            
            novoPagamento.vencimentoPagamento = conversaoParaDate(vencimentoPagamento)
            
            novoPagamento.codigoMesAnoPagamento = consultarMesAnoPagamento(
                novoPagamento.vencimentoPagamento, 
                codigoUsuario
            )
            novoPagamento.valorPagamento = valorPagamento
            novoPagamento.numeroParcelaPagamento = numeroParcelaPagamento
            novoPagamento.statusPagamento = statusPagamento

            sessao.add(novoPagamento)
            sessao.commit()
            sessao.refresh(novoPagamento)

            gerarLog(
                mensagemLog=f"Pagamento '{descricaoPagamento}' cadastrado para usuário {codigoUsuario}.",
                nivelLogger="info",
                classeLog="pagamento - cadastrarPagamento"
            )

            return {
                "status": "SUCESSO",
                "mensagem": "Pagamento cadastrado com sucesso.",
                "codigoPagamento": novoPagamento.codigoPagamento,
                "descricaoPagamento": novoPagamento.descricaoPagamento,
                "codigoTipoPagamento": novoPagamento.codigoTipoPagamento,
                "codigoMesAnoPagamento": novoPagamento.codigoMesAnoPagamento,
                "vencimentoPagamento": novoPagamento.vencimentoPagamento,
                "valorPagamento": novoPagamento.valorPagamento,
                "numeroParcelaPagamento": novoPagamento.numeroParcelaPagamento,
                "statusPagamento": novoPagamento.statusPagamento
            }        
        except Exception as e:
            sessao.rollback()
            gerarLog(
                mensagemLog=f"Erro ao cadastrar pagamento: {str(e)}",
                nivelLogger="error",
                classeLog="pagamento - cadastrarPagamento"
            )
            return {
                "status": "ERRO",
                "mensagem": f"Erro ao cadastrar pagamento: {str(e)}"
            }
        finally:
            sessao.close()

    def cadastrarPagamentoFixo(self, 
                               codigoUsuario: int,
                               descricaoPagamento: str,
                               codigoTipoPagamento: int,
                               valorPagamento: float,
                               vencimentoPagamento: date = datetime.now().date(),
                               statusPagamento: bool = False
                              ) -> dict:
        from Controller import funcoesMesAnoPagamento
        
        resultados = []
        vencimentoPagamento = conversaoParaDate(vencimentoPagamento)
        diaVencimentoOriginal = vencimentoPagamento.day
        
        # Obter todos os mês/ano disponíveis do usuário
        meses_anos_disponiveis = funcoesMesAnoPagamento.get("listar")(codigoUsuario)
        
        if not meses_anos_disponiveis:
            return {
                "status": "ERRO",
                "mensagem": "Nenhum mês/ano disponível para cadastro."
            }
        
        # Filtrar apenas mês/ano igual ou posterior à data inicial
        mes_inicial = vencimentoPagamento.month
        ano_inicial = vencimentoPagamento.year
        
        for ma in meses_anos_disponiveis:
            mes_ma = ma.get('mesPagamento')
            ano_ma = ma.get('anoPagamento')
            
            # Verificar se o mês/ano é igual ou posterior ao inicial
            if (ano_ma > ano_inicial) or (ano_ma == ano_inicial and mes_ma >= mes_inicial):
                # Ajustar dia do vencimento para o mês atual
                ultimo_dia_mes = monthrange(ano_ma, mes_ma)[1]
                dia_vencimento = min(diaVencimentoOriginal, ultimo_dia_mes)
                
                data_vencimento_mes = date(ano_ma, mes_ma, dia_vencimento)
                
                # Cadastrar pagamento para este mês/ano
                sessao = sessaoLocal()
                try:
                    novoPagamento = tbPagamento()
                    novoPagamento.codigoUsuario = codigoUsuario
                    novoPagamento.descricaoPagamento = descricaoPagamento
                    novoPagamento.codigoTipoPagamento = codigoTipoPagamento
                    novoPagamento.vencimentoPagamento = data_vencimento_mes
                    novoPagamento.codigoMesAnoPagamento = ma.get('codigoMesAnoPagamento')
                    novoPagamento.valorPagamento = valorPagamento
                    novoPagamento.numeroParcelaPagamento = 1
                    novoPagamento.statusPagamento = statusPagamento
                    
                    sessao.add(novoPagamento)
                    sessao.commit()
                    sessao.refresh(novoPagamento)
                    
                    resultados.append({
                        "status": "SUCESSO",
                        "codigoPagamento": novoPagamento.codigoPagamento,
                        "mes": mes_ma,
                        "ano": ano_ma
                    })
                    
                except Exception as e:
                    sessao.rollback()
                    resultados.append({
                        "status": "ERRO",
                        "mes": mes_ma,
                        "ano": ano_ma,
                        "erro": str(e)
                    })
                finally:
                    sessao.close()
        
        sucesso = len([r for r in resultados if r.get("status") == "SUCESSO"])
        erro = len([r for r in resultados if r.get("status") == "ERRO"])
        
        gerarLog(
            mensagemLog=f"Pagamento fixo '{descricaoPagamento}' cadastrado para usuário {codigoUsuario}: {sucesso} sucesso(s), {erro} erro(s).",
            nivelLogger="info",
            classeLog="pagamento - cadastrarPagamentoFixo"
        )
        
        return {
            "status": "SUCESSO" if sucesso > 0 else "ERRO",
            "mensagem": f"Pagamento fixo cadastrado em {sucesso} mês(es). {erro} erro(s).",
            "resultados": resultados
        }
    
    def listarPagamentos(self, codigoUsuario: int = None) -> list:
        
        sessao = sessaoLocal()
        try:
            query = sessao.query(tbPagamento)
            
            if codigoUsuario:
                query = query.filter_by(codigoUsuario=codigoUsuario)
            
            pagamentos = query.order_by(tbPagamento.vencimentoPagamento.desc()).all()
            
            return [{
                "codigoPagamento": p.codigoPagamento,
                "codigoUsuario": p.codigoUsuario,
                "descricaoPagamento": p.descricaoPagamento,
                "codigoTipoPagamento": p.codigoTipoPagamento,
                "codigoMesAnoPagamento": p.codigoMesAnoPagamento,
                "valorPagamento": p.valorPagamento,
                "vencimentoPagamento": p.vencimentoPagamento,
                "numeroParcelaPagamento": p.numeroParcelaPagamento,
                "statusPagamento": p.statusPagamento
            } for p in pagamentos]
            
        except Exception as e:
            gerarLog(
                mensagemLog=f"Erro ao listar pagamentos: {str(e)}",
                nivelLogger="error",
                classeLog="pagamento - listarPagamentos"
            )
            return []
        finally:
            sessao.close()
    
    def consultarPagamentoPorCodigo(self, codigoPagamento: int, codigoUsuario: int = None) -> dict:
        
        sessao = sessaoLocal()
        try:
            query = sessao.query(tbPagamento).filter_by(codigoPagamento=codigoPagamento)
            
            if codigoUsuario:
                query = query.filter_by(codigoUsuario=codigoUsuario)
            
            pagamento = query.first()
            
            if pagamento:
                return {
                    "status": "SUCESSO",
                    "codigoPagamento": pagamento.codigoPagamento,
                    "codigoUsuario": pagamento.codigoUsuario,
                    "descricaoPagamento": pagamento.descricaoPagamento,
                    "codigoTipoPagamento": pagamento.codigoTipoPagamento,
                    "codigoMesAnoPagamento": pagamento.codigoMesAnoPagamento,
                    "valorPagamento": pagamento.valorPagamento,
                    "vencimentoPagamento": pagamento.vencimentoPagamento,
                    "numeroParcelaPagamento": pagamento.numeroParcelaPagamento,
                    "statusPagamento": pagamento.statusPagamento
                }
            else:
                return {
                    "status": "ERRO",
                    "mensagem": "Pagamento não encontrado."
                }
                
        except Exception as e:
            gerarLog(
                mensagemLog=f"Erro ao consultar pagamento: {str(e)}",
                nivelLogger="error",
                classeLog="pagamento - consultarPagamentoPorCodigo"
            )
            return {
                "status": "ERRO",
                "mensagem": f"Erro ao consultar: {str(e)}"
            }
        finally:
            sessao.close()
    
    def atualizarPagamento(self,
                          codigoPagamento: int,
                          codigoUsuario: int,
                          descricaoPagamento: str = None,
                          codigoTipoPagamento: int = None,
                          valorPagamento: float = None,
                          vencimentoPagamento: date = None,
                          numeroParcelaPagamento: int = None,
                          statusPagamento: bool = None) -> dict:
        
        sessao = sessaoLocal()
        try:
            pagamento = sessao.query(tbPagamento).filter_by(
                codigoPagamento=codigoPagamento,
                codigoUsuario=codigoUsuario
            ).first()
            
            if not pagamento:
                return {
                    "status": "ERRO",
                    "mensagem": "Pagamento não encontrado."
                }
            
            if descricaoPagamento is not None:
                pagamento.descricaoPagamento = descricaoPagamento
            if codigoTipoPagamento is not None:
                pagamento.codigoTipoPagamento = codigoTipoPagamento
            if valorPagamento is not None:
                pagamento.valorPagamento = valorPagamento
            if vencimentoPagamento is not None:
                pagamento.vencimentoPagamento = conversaoParaDate(vencimentoPagamento)
                pagamento.codigoMesAnoPagamento = consultarMesAnoPagamento(
                    pagamento.vencimentoPagamento, 
                    codigoUsuario
                )
            if numeroParcelaPagamento is not None:
                pagamento.numeroParcelaPagamento = numeroParcelaPagamento
            if statusPagamento is not None:
                pagamento.statusPagamento = statusPagamento
            
            sessao.commit()
            
            gerarLog(
                mensagemLog=f"Pagamento {codigoPagamento} atualizado.",
                nivelLogger="info",
                classeLog="pagamento - atualizarPagamento"
            )
            
            return {
                "status": "SUCESSO",
                "mensagem": "Pagamento atualizado com sucesso."
            }
            
        except Exception as e:
            sessao.rollback()
            gerarLog(
                mensagemLog=f"Erro ao atualizar pagamento: {str(e)}",
                nivelLogger="error",
                classeLog="pagamento - atualizarPagamento"
            )
            return {
                "status": "ERRO",
                "mensagem": f"Erro ao atualizar: {str(e)}"
            }
        finally:
            sessao.close()
    
    def removerPagamento(self, codigoPagamento: int, codigoUsuario: int) -> dict:
        
        sessao = sessaoLocal()
        try:
            pagamento = sessao.query(tbPagamento).filter_by(
                codigoPagamento=codigoPagamento,
                codigoUsuario=codigoUsuario
            ).first()
            
            if not pagamento:
                return {
                    "status": "ERRO",
                    "mensagem": "Pagamento não encontrado."
                }
            
            sessao.delete(pagamento)
            sessao.commit()
            
            gerarLog(
                mensagemLog=f"Pagamento {codigoPagamento} removido.",
                nivelLogger="info",
                classeLog="pagamento - removerPagamento"
            )
            
            return {
                "status": "SUCESSO",
                "mensagem": "Pagamento removido com sucesso."
            }
            
        except Exception as e:
            sessao.rollback()
            gerarLog(
                mensagemLog=f"Erro ao remover pagamento: {str(e)}",
                nivelLogger="error",
                classeLog="pagamento - removerPagamento"
            )
            return {
                "status": "ERRO",
                "mensagem": f"Erro ao remover: {str(e)}"
            }
        finally:
            sessao.close()