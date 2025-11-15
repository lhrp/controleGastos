import logging
import os

class GestaoLogs():
    def __init__(self, caminhoLog="log/logs.log", loggerName="gestaoGastos"):
        # Garantindo a existência da pasta base
        os.makedirs(os.path.dirname(caminhoLog), exist_ok=True)

        # Criando logger principal
        self.logger = logging.getLogger(loggerName)
        self.logger.setLevel(logging.DEBUG)

        # 🔧 Força UTF-8 no arquivo, evitando erros de caracteres especiais
        self.arquivoLog = logging.FileHandler(caminhoLog, encoding="utf-8")

        # Formato de log
        formatacaoArquivoLog = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.arquivoLog.setFormatter(formatacaoArquivoLog)

        # Evita adicionar handlers duplicados
        if not self.logger.handlers:
            self.logger.addHandler(self.arquivoLog)

    def gerarLog(self, mensagemLog: str, nivelLogger: str = "info", classeLog: str = None):
        """
        Registra log usando o nome do logger como a classeLog informada.
        - Se "classeLog" for fornecida, o logger usado terá esse nome (substitui o loggerName na saída).
        - Caso contrário, usa o logger padrão.
        """
        loggerAlvo = self.logger

        if classeLog:
            nomeLogger = str(classeLog)
            loggerAlvo = logging.getLogger(nomeLogger)
            # Configurando o logger com a classeLog informada, para salvar no mesmo arquivo, evitando duplicidades
            if not loggerAlvo.handlers:
                loggerAlvo.setLevel(self.logger.level)
                loggerAlvo.addHandler(self.arquivoLog)
                loggerAlvo.propagate = False

        nivelLoggerLogger = str(nivelLogger).lower()
        if nivelLogger == "info":
            loggerAlvo.info(mensagemLog)
        elif nivelLogger == "error":
            loggerAlvo.error(mensagemLog)
        elif nivelLogger == "debug":
            loggerAlvo.debug(mensagemLog)
        elif nivelLogger == "warning":
            loggerAlvo.warning(mensagemLog)
        elif nivelLogger == "exception":
            loggerAlvo.exception(mensagemLog)
        else:
            loggerAlvo.info(mensagemLog)
