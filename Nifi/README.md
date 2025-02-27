
# LAB Mongodb Kafka e Nifi

---
## Disclaimer
> **Esta configuração é puramente para fins de desenvolvimento local e estudos**
> 

---

![Lab](/content/arc.png)

---

# Nifi

## Subindo o ambiente docker com NIFI

> [!IMPORTANT]
> Observe o docker compose, o serviço do NIFI


```bash
 docker compose up -d nifi
```

> https://localhost:9443/nifi/#/login


|Usuário|Senha|
|------------------|--------------|
|admin|fia@2024@ladata@laboratorio|


### Criando o Process Group

Process Group (Grupo de Processos) é um agrupador lógico que organiza um conjunto de processadores e outros componentes do fluxo de dados

![Lab](/content/nifi1.png)


### Parameter Context

No Apache NiFi, Contexto de Parâmetros é um recurso que permite centralizar e gerenciar configurações reutilizáveis dentro de um fluxo de dados. Ele possibilita definir valores parametrizáveis para processadores, permitindo maior flexibilidade e facilidade na manutenção dos fluxos.

![Lab](/content/nifi2.png)


### Os principais benefícios incluem:
* ✅ Reutilização – Um único conjunto de parâmetros pode ser aplicado a vários componentes.
* ✅ Segurança – Parâmetros sensíveis, como credenciais, podem ser protegidos.
* ✅ Facilidade de Alteração – Ajustes podem ser feitos sem modificar diretamente os fluxos.



![Lab](/content/nifi3.png)

![Lab](/content/nifi4.png)

![Lab](/content/nifi-parameter.png)


![Lab](/content/nifi5.png)


|Name|Value|
|------------------|--------------|
|consumer-group-produto|mongo.loja.produtos|
|kafka-broker|kafka-broker:29092|
|kafka-topic|topic-demo|
|kafka-topic-produto|mongo.loja.produtos|

![Lab](/content/nifi15.png)

Para atribuir um Contexto de Parâmetro a um Grupo de Processos, clique em Configurar, na Paleta de Operação ou no menu de contexto do Grupo de Processos.

![Lab](/content/nifi6.png)




### Criando um Processeor GenerateFlowFile

Altere o Custom Text do GenerateFlowFile para o json abaixo

```json
{
  "idProduto": "${random():mod(1000):plus(1)}",
  "nomeProduto": "Produto Teste",
  "orderId": "${UUID()}",
  "date": "${now():format('yyyy-MM-dd HH:mm:ss')}"
}
```



### Controller Services
No Apache NiFi, os Controller Services são componentes compartilháveis que fornecem funcionalidades comuns a vários processadores dentro de um fluxo de dados. Eles permitem centralizar configurações e melhorar a eficiência do processamento.

Exemplos de Controller Services:
* 🔹 DBCPConnectionPool – Gerencia conexões com bancos de dados.
* 🔹 SSLContextService – Configura SSL/TLS para comunicação segura.
* 🔹 AvroSchemaRegistry – Define esquemas de dados Avro para validação.

![Lab](/content/nifi7.png)



![Lab](/content/nifi8.png)


### Configurando o Controller Services `Kafka3ConnectionService`

|Property|Value|
|------------------|--------------|
|Bootstrap Servers|#{kafka-broker}|

![Lab](/content/nifi8-1.png)

![Lab](/content/nifi8-2.png)



### Criando um Processor PublishKafka

![Lab](/content/nifi10.png)

![Lab](/content/nifi11.png)


|Property|Value|
|------------------|--------------|
|Kafka Connection Service|Kafka3ConnectionService|
|Topic Name|#{kafka-topic}|


### Criando e vinculando um Funil

![Lab](/content/nifi12.png)


### Deu tudo certo ???

### Listando os tópicos

```bash
docker exec -it kafka-broker /bin/bash
kafka-topics --bootstrap-server localhost:9092 --list 

kafka-console-consumer --bootstrap-server localhost:9092 --topic topic-demo --from-beginning
```

Linguem de expressão
https://nifi.apache.org/docs/nifi-docs/html/expression-language-guide.html

---

## Vamos criar outro ProcessGroup com o nome de kafka

![Lab](/content/nifi13.png)

![Lab](/content/nifi14.png)


![Lab](/content/nifi16.png)

|Property|Value|
|------------------|--------------|
|Kafka Connection Service|Kafka3ConnectionService|
|Group ID|#{consumer-group-produto}|
|Topics|#{kafka-topic-produto}|


![Lab](/content/nifi17.png)

## Vinculando um Funil

![Lab](/content/nifi17-2.png)


> [!IMPORTANT] 
> Altere o script `importProdutos.js` para novos idproduto

## Publicando novas mensgens

```JavaScript

docker exec -it mongo1 /bin/bash

mongosh


use loja

load("/scripts/importProdutos.js")


```


## Analisando o consumer group no kafka

```bash
docker exec -it kafka-broker /bin/bash
kafka-consumer-groups --bootstrap-server localhost:9092 --list
```

### Descrevendo o consumer group

```
kafka-consumer-groups --bootstrap-server localhost:9092 --describe --group mongo.loja.produtos

```

## Criando um Process Group para o MiniIO, mas antes..

```bash
 docker compose up -d minio
```

> http://localhost:9001/

|Usuário|Senha|
|------------------|--------------|
|admin|minioadmin|

## Criando ProcessGroup para o MinIO

![Lab](/content/nifi19.png)


## Criando Controller Services `AWSCredentialsProviderControllerService` para autenticação 

![Lab](/content/nifi22.png)


## Configurando o ProcessGroup

|Property|Value|
|------------------|--------------|
|Bucket|raw|
|Object Key|/kafka/produtos/year=${now():format('yyyy')}/month=${now():format('MM')}/day=${now():format('dd')}/${kafka.topic}/${filename}.json|


![Lab](/content/nifi21.png)



## Criando Output Input Port e correlacionando os Group Process

![Lab](/content/nifi17-1.png)



![Lab](/content/nifi23.png)


---


## Configurando o Minio para gerar eventos

![MinIO](/content/minio-events-01.png)

### Selecione a Queue Kafka

![MinIO](/content/minio-events-02.png)

### Informa as seguintes configurações

* Identifier : EventKafkaProduto
* Brokers: kafka-broker:29092
* Topic: sink-minio-produto


![MinIO](/content/minio-events-03.png)

### Renicia o serviço e veja depois se ficou online

![MinIO](/content/minio-events-04.png)
![MinIO](/content/minio-events-05.png)


### Criando o Subscribe para o bucket raw//kafka/produtos/
![MinIO](/content/minio-events-06.png)


### Configurando o evento para ser acionado para a pasta /kafka/produtos/

* ARN : arn:minio:sqs::EventKafkaProduto:kafka
* Prefix: /kafka/produtos/
* Suffix: .json

![MinIO](/content/minio-events-07.png)


### Crie mensagens novas no mongodb


Consumindo mensagens do tópico `mongo.loja.produtos`

```bash
docker exec -it kafka-broker /bin/bash
kafka-topics --bootstrap-server localhost:9092 --list 
kafka-console-consumer --bootstrap-server localhost:9092 --topic sink-minio-produto --from-beginning
```

-----

## Ajuste seu worker para a leitura dos eventos do kafka para buscar informações no Minio

### Arquivo `processor.py`

```python
import json
from typing import  Optional
import logging
import boto3
from urllib.parse import unquote

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

    def process_event_minio(self, message, config):
        """
        Processa um evento Kafka e acessa o objeto correspondente no MinIO.
        """
        try:
             # Decodificando a mensagem JSON
            payload = message.value().decode('utf-8')

            # Parse do evento recebido
            event_data = json.loads(payload)
            bucket_name = event_data.get('Records')[0]['s3']['bucket']['name']
            object_key = unquote(event_data.get('Records')[0]['s3']['object']['key'])

            self._logger.info(f"Bucket: {bucket_name}, Key: {object_key}")

            # Conexão ao MinIO usando boto3
            s3_client = boto3.client('s3', **config.MINIO_CONFIG)

            # Baixar o conteúdo do objeto
            response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
            content = response['Body'].read().decode('utf-8')
            self._logger.info(f"\nDados 'Bucket:{json.dumps(content, indent=4)}")
          

        except Exception as e:
            self._logger.error(f"Erro ao processar a mensagem: {e}")

```


### Arquivo `config.py`

```python
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

# Configurações do MinIO
MINIO_CONFIG = {
    'endpoint_url': os.getenv('MINIO_ENDPOINT_URL', 'http://minio:9000'),
    'aws_access_key_id': os.getenv('MINIO_ACCESS_KEY', 'cursolab'),
    'aws_secret_access_key': os.getenv('MINIO_SECRET_KEY', 'cursolab'),
}

# Configurações do MinIO
APP_MINIO= os.getenv('APP_MINIO', '0')

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
        self.APP_MINIO=config.APP_MINIO  
        self._logger = logger or logging.getLogger("worker.kafka")
        self.config =config
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

             
                if self.APP_MINIO:
                    self.processMessage.process_event_minio(msg, self.config)
                else:
                    self.processMessage.process_event(msg)

                # Commit manual após processar a mensagem
                consumer.commit(asynchronous=False)

        except KeyboardInterrupt:
            self._logger.error("Interrompido pelo usuário.")
        finally:
            consumer.close()



```


## Criando uma nova imagem Docker para o consumer


> [!IMPORTANT]
> Lembrar de informar o path do Dockerfile corretamente


```bash
docker build -t kafka-worker-consumer ./worker

docker compose up -d kafka-worker-python

```