from consumer import KafkaConsumerWorker
from loggerWorker import LoggerWorker
import config
import logging


if __name__ == "__main__":
     # Configuração do logger
    logger_worker = LoggerWorker()  # Criando uma instância do logger  
    _logger = logging.getLogger("worker.kafka")
    _logger.info("Worker iniciado")
   
    consummer = KafkaConsumerWorker(config)  # Criando uma instância do logger
    consummer.consume_events()
