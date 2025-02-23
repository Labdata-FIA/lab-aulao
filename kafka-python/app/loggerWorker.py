import logging

class LoggerWorker:
    def __init__(self, name="worker.kafka", log_level=logging.DEBUG, log_file=None):
        """
        Inicializa o logger com a configuração fornecida.

        :param name: Nome do logger (default é "worker.kafka").
        :param log_level: Nível de log (default é DEBUG).
        :param log_file: Caminho do arquivo de log (default é None, o que significa apenas imprimir no console).
        """
        # Cria o logger com o nome fornecido
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)

        # Cria o formatter para as mensagens de log
        formatter = logging.Formatter(fmt="[%(asctime)s][%(levelname)s] %(message)s", datefmt="%d-%m-%Y %H:%M:%S")

        # Cria o StreamHandler para exibir os logs no console
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

        # Se um arquivo de log for fornecido, cria o FileHandler
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

   