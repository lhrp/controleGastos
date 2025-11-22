from Models import gerarLog, conexaoBanco
from Models.tbUsuario import tbUsuario
from datetime import datetime
import hashlib
import re

from sqlalchemy.orm import sessionmaker

engine = conexaoBanco()
sessaoLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class usuario():
    
    def __init__(self):
        self.codigoUsuario = None
        self.nomeUsuario = None
        self.emailUsuario = None
        self.senhaUsuario = None
        self.ativoUsuario = None
        self.dataCadastroUsuario = None
        self.dataUltimoAcessoUsuario = None


    def criptografarSenha(self, senha: str) -> str:
        """Criptografa a senha usando SHA256"""
        return hashlib.sha256(senha.encode()).hexdigest()
    
    def validarEmail(self, email: str) -> bool:
        """Valida formato de email"""
        padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(padrao, email) is not None
    
    def cadastrarUsuario(self, 
                        nomeUsuario: str,
                        emailUsuario: str,
                        senhaUsuario: str) -> dict:
        
        sessao = sessaoLocal()
        try:
            # Validações
            if not nomeUsuario or len(nomeUsuario.strip()) < 3:
                return {
                    "status": "ERRO",
                    "mensagem": "Nome deve ter pelo menos 3 caracteres."
                }
            
            if not self.validarEmail(emailUsuario):
                return {
                    "status": "ERRO",
                    "mensagem": "Email inválido."
                }
            
            if len(senhaUsuario) < 6:
                return {
                    "status": "ERRO",
                    "mensagem": "Senha deve ter pelo menos 6 caracteres."
                }
            
            # Verificar se email já existe
            usuario_existente = sessao.query(tbUsuario).filter_by(emailUsuario=emailUsuario).first()
            if usuario_existente:
                return {
                    "status": "ERRO",
                    "mensagem": "Email já cadastrado no sistema."
                }
            
            # Criar novo usuário
            novoUsuario = tbUsuario()
            novoUsuario.nomeUsuario = nomeUsuario.strip()
            novoUsuario.emailUsuario = emailUsuario.lower().strip()
            novoUsuario.senhaUsuario = self.criptografarSenha(senhaUsuario)
            novoUsuario.ativoUsuario = True
            novoUsuario.dataCadastroUsuario = datetime.now()
            
            sessao.add(novoUsuario)
            sessao.commit()
            sessao.refresh(novoUsuario)
            
            gerarLog(
                mensagemLog=f"Usuário '{nomeUsuario}' cadastrado com sucesso.",
                nivelLogger="info",
                classeLog="usuario - cadastrarUsuario"
            )
            
            return {
                "status": "SUCESSO",
                "mensagem": "Usuário cadastrado com sucesso!",
                "codigoUsuario": novoUsuario.codigoUsuario,
                "nomeUsuario": novoUsuario.nomeUsuario,
                "emailUsuario": novoUsuario.emailUsuario
            }
            
        except Exception as e:
            sessao.rollback()
            gerarLog(
                mensagemLog=f"Erro ao cadastrar usuário: {str(e)}",
                nivelLogger="error",
                classeLog="usuario - cadastrarUsuario"
            )
            return {
                "status": "ERRO",
                "mensagem": f"Erro ao cadastrar usuário: {str(e)}"
            }
        finally:
            sessao.close()
    
    def autenticarUsuario(self, emailUsuario: str, senhaUsuario: str) -> dict:
        
        sessao = sessaoLocal()
        try:
            # Buscar usuário
            usuario = sessao.query(tbUsuario).filter_by(
                emailUsuario=emailUsuario.lower().strip()
            ).first()
            
            if not usuario:
                return {
                    "status": "ERRO",
                    "mensagem": "Email ou senha incorretos."
                }
            
            # Verificar se está ativo
            if not usuario.ativoUsuario:
                return {
                    "status": "ERRO",
                    "mensagem": "Usuário inativo. Entre em contato com o suporte."
                }
            
            # Verificar senha
            senha_criptografada = self.criptografarSenha(senhaUsuario)
            if usuario.senhaUsuario != senha_criptografada:
                return {
                    "status": "ERRO",
                    "mensagem": "Email ou senha incorretos."
                }
            
            # Atualizar último acesso
            usuario.dataUltimoAcessoUsuario = datetime.now()
            sessao.commit()
            
            gerarLog(
                mensagemLog=f"Usuário '{usuario.nomeUsuario}' autenticado com sucesso.",
                nivelLogger="info",
                classeLog="usuario - autenticarUsuario"
            )
            
            return {
                "status": "SUCESSO",
                "mensagem": "Login realizado com sucesso!",
                "codigoUsuario": usuario.codigoUsuario,
                "nomeUsuario": usuario.nomeUsuario,
                "emailUsuario": usuario.emailUsuario
            }
            
        except Exception as e:
            sessao.rollback()
            gerarLog(
                mensagemLog=f"Erro ao autenticar usuário: {str(e)}",
                nivelLogger="error",
                classeLog="usuario - autenticarUsuario"
            )
            return {
                "status": "ERRO",
                "mensagem": f"Erro ao autenticar: {str(e)}"
            }
        finally:
            sessao.close()
    
    def listarUsuarios(self) -> list:
        
        sessao = sessaoLocal()
        try:
            usuarios = sessao.query(tbUsuario).filter_by(ativoUsuario=True).all()
            
            return [{
                "codigoUsuario": u.codigoUsuario,
                "nomeUsuario": u.nomeUsuario,
                "emailUsuario": u.emailUsuario,
                "dataCadastroUsuario": u.dataCadastroUsuario,
                "dataUltimoAcessoUsuario": u.dataUltimoAcessoUsuario
            } for u in usuarios]
            
        except Exception as e:
            gerarLog(
                mensagemLog=f"Erro ao listar usuários: {str(e)}",
                nivelLogger="error",
                classeLog="usuario - listarUsuarios"
            )
            return []
        finally:
            sessao.close()
    
    def atualizarSenha(self, codigoUsuario: int, senhaAtual: str, novaSenha: str) -> dict:
        
        sessao = sessaoLocal()
        try:
            usuario = sessao.query(tbUsuario).filter_by(codigoUsuario=codigoUsuario).first()
            
            if not usuario:
                return {
                    "status": "ERRO",
                    "mensagem": "Usuário não encontrado."
                }
            
            # Verificar senha atual
            if usuario.senhaUsuario != self.criptografarSenha(senhaAtual):
                return {
                    "status": "ERRO",
                    "mensagem": "Senha atual incorreta."
                }
            
            # Validar nova senha
            if len(novaSenha) < 6:
                return {
                    "status": "ERRO",
                    "mensagem": "Nova senha deve ter pelo menos 6 caracteres."
                }
            
            # Atualizar senha
            usuario.senhaUsuario = self.criptografarSenha(novaSenha)
            sessao.commit()
            
            gerarLog(
                mensagemLog=f"Senha do usuário {codigoUsuario} atualizada.",
                nivelLogger="info",
                classeLog="usuario - atualizarSenha"
            )
            
            return {
                "status": "SUCESSO",
                "mensagem": "Senha atualizada com sucesso!"
            }
            
        except Exception as e:
            sessao.rollback()
            gerarLog(
                mensagemLog=f"Erro ao atualizar senha: {str(e)}",
                nivelLogger="error",
                classeLog="usuario - atualizarSenha"
            )
            return {
                "status": "ERRO",
                "mensagem": f"Erro ao atualizar senha: {str(e)}"
            }
        finally:
            sessao.close()

# Exportar funções
funcoesUsuario = {
    "cadastrar": usuario().cadastrarUsuario,
    "autenticar": usuario().autenticarUsuario,
    "listar": usuario().listarUsuarios,
    "atualizarSenha": usuario().atualizarSenha
}