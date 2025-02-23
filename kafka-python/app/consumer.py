from confluent_kafka import Consumer, KafkaError
import logging
from processor import ProcessMessage
from typing import  Optional

class KafkaConsumerWorker:

    def __init__(self, 
                config,
                logger: Optional[logging.Logger] = None,):
        
        self.KAFKA_CONFIG = config.KAFKA_CONFIG
        self.TOPIC = config.TOPIC
        self._logger = logger or logging.getLogger("worker.kafka")
        self.processMessage = ProcessMessage();
    
    def consume_events(self):
        """
        Consome eventos do Kafka e processa.
        """
        consumer = Consumer(self.KAFKA_CONFIG)
        consumer.subscribe([self.TOPIC])

        try:
            self._logger.info(f"Assinado ao tópico: {self.TOPIC} - {self.KAFKA_CONFIG}  ")       
            while True:
                msg = consumer.poll(timeout=1.0)  # Aguarda por mensagens

                if msg is None:
                    continue  # Sem mensagens no momento

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue  # Fim da partição
                    else:
                        self._logger.error(f"Erro no Kafka: {msg.error()}")
                        continue

                # Processar a mensagem recebida
                self._logger.info(f"Mensagem recebida: {msg.value().decode('utf-8')}")

                self.processMessage.process_event(msg)

                # Commit manual após processar a mensagem
                consumer.commit(asynchronous=False)

        except KeyboardInterrupt:
            self._logger.error("Interrompido pelo usuário.")
        finally:
            consumer.close()
