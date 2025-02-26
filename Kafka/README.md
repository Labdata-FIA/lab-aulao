
# LAB Mongodb Kafka e Nifi

---
## Disclaimer
> **Esta configuração é puramente para fins de desenvolvimento local e estudos**
> 

---

![Lab](/content/arc.png)

---

# Kafka e Kafka Connect

---

## 💻 Pré-requisitos
* [Docker] https://docs.docker.com/engine/install/
* [Docker-Compose] https://docs.docker.com/engine/install/

---


## Configurando o Kafka Connect e seus conectores que serão responsáveis  pela leitura das informações do Mongodb

Criando a imagem com DockerFile e subindo o ambiente

```bash

docker image build -t kafka-connet-debezium:3.0.7.Final  -f  kafka-connect/Dockerfile .

docker compose up -d  kafka-broker zookeeper connect
```

## Obseravndo os plugins criados

```bash
docker exec -it kafkaConect curl  http://localhost:8083/connector-plugins

```

## Criando os conectores


```bash
 
 curl -X PUT -d @kafka-connect/conector-mongdb.json http://localhost:8083/connectors/connector-mongodb/config -H 'Content-Type: application/json' -H 'Accept: application/json'


//Ou via powershell
$response = Invoke-WebRequest -Uri "http://localhost:8083/connectors/connector-mongodb/config" -Method Put -Body (Get-Content -Path "kafka-connect/conector-mongdb.json" -Raw) -ContentType "application/json"; $response.Content

```

### Listando os conectores

```bash
docker exec -it kafkaConect curl http://localhost:8083/connectors/
```


### Verificando o status dos conectores

```bash
docker exec -it kafkaConect curl http://localhost:8083/connectors/connector-mongodb/status

```

### Listando os tópicos

```bash
docker exec -it kafka-broker /bin/bash
kafka-topics --bootstrap-server localhost:9092 --list 
```
> [!IMPORTANT]
>### Altere o script do arquivo `importProdutos.js` para gerar novos produtos, como por exemplo 600 a 100

### Listando os tópicos

Consumindo mensagens do tópico `mongo.loja.produtos`

```bash
kafka-console-consumer --bootstrap-server localhost:9092 --topic mongo.loja.produtos --from-beginning
```

## Criando o worker para a leitura das mensagens no kafka


Crie um pastinha worker com  a estrutura abaixo dentro

![Lab](/content/worker-python.png)


```
├── Dockerfile
├── app
│   ├── __init__.py
│   ├── config.py
│   ├── consumer.py
│   ├── loggerWorker.py
│   ├── main.py
│   └── processor.py
├── docker.env
└── requirements.txt
```

### Arquivos dentro da pasta app/

### Arquivo `config.py`

```python
import os
from dotenv import load_dotenv

if os.getenv("DOCKER_ENV") is None:  # Se NÃO estiver rodando no Docker
    # Carrega as variáveis de ambiente do arquivo .env
    load_dotenv(override=True)


# Configurações para o  Kafka
KAFKA_CONFIG = {
    'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka-broker:29092'),
    'group.id': os.getenv('KAFKA_GROUP_ID', 'default-group'),
    'auto.offset.reset': os.getenv('KAFKA_AUTO_OFFSET_RESET', 'earliest'),
}

# Nome do tópico
TOPIC = os.getenv('KAFKA_TOPIC', 'default-topic')


```


### Arquivo `consumer.py`
```python
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

        except KeyboardInterrupt:
            self._logger.error("Interrompido pelo usuário.")
        finally:
            consumer.close()

```

### Arquivo `loggerWorker.py`
```python
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

   
```

### Arquivo `main.py`

```python
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

```

### Arquivo `processor.py`

```python
import json
from typing import  Optional
import logging


class ProcessMessage:

    def __init__(self,               
                logger: Optional[logging.Logger] = None,):
       
        self._logger = logger or logging.getLogger("worker.kafka")
        
    def process_event(self, message):
        """
        Processa um evento Kafka e acessa o objeto correspondente no MinIO.
        """
        try:
            # Decodificando a mensagem JSON
            payload = message.value().decode('utf-8')
            data = json.loads(payload)
            
            # Exibindo a mensagem completa          
            self._logger.info(f"Mensagem recebida:{json.dumps(data, indent=4)}")

            # Processamento adicional (por exemplo, extrair o campo 'after')
            if 'after' in data:
                after_data = data['after']
                self._logger.info(f"\nDados 'after:{json.dumps(after_data, indent=4)}")

        except Exception as e:
            self._logger.error(f"Erro ao processar a mensagem: {e}")
```

### Arquivo `Dockerfile`

```python
# Imagem base do Python
FROM python:3.9-slim

# Diretório de trabalho
WORKDIR /app

# Instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia os arquivos do projeto
COPY . .

# Comando de inicialização
CMD ["python", "app/main.py"]

```

### Arquivo `requirements.txt`

```text
confluent-kafka==2.1.1
boto3==1.35.76
python-dotenv==1.0.0
```


## Criando a imagem Docker para o consumer


> [!IMPORTANT]
> Lembrar de informar o path do Dockerfile corretamente


```bash
docker build -t kafka-worker-consumer ./worker

docker compose up -d kafka-worker-consumer

```

## Deu certo??
Acesse os logs


## Altere informações do mongodb da collection produtos

[LAB NIFI](../nifi/README.md)
