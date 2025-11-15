import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Conexao():
    
    def retornaConexao(self):
        
        caminhaBancoSQLite = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'LocalDataBase')
        
        # Criando a pasta se não existir
        if not os.path.exists(caminhaBancoSQLite):
            os.makedirs(caminhaBancoSQLite)
        
        # Definindo o caminho completo de onde o arquivo .db está
        caminhaBancoSQLite = os.path.join(caminhaBancoSQLite, 'controleGastos.db')
        
        self.connectionString = f"sqlite:///{caminhaBancoSQLite}"
       
        return create_engine(self.connectionString)