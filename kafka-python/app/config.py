import os
from dotenv import load_dotenv

if os.getenv("DOCKER_ENV") is None:  # Se NÃO estiver rodando no Docker
    # Carrega as variáveis de ambiente do arquivo .env
    load_dotenv(override=True)


# Configurações do Kafka
KAFKA_CONFIG = {
    'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka-broker:29092'),
    'group.id': os.getenv('KAFKA_GROUP_ID', 'default-group'),
    'auto.offset.reset': os.getenv('KAFKA_AUTO_OFFSET_RESET', 'earliest'),
    'enable.auto.commit': os.getenv('KAFKA_AUTO_COMMIT', "False")   # Desativa o commit automático
}

# Nome do tópico
TOPIC = os.getenv('KAFKA_TOPIC', 'default-topic')

