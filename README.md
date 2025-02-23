
# LAB MONGODB

---
## Disclaimer
> **Esta configuração é puramente para fins de desenvolvimento local e estudos**
> 

---

![Lab](/content/arc.png)

---

# Mongodb

![Cluster Mongo db](/content/cluster-mongdb.png)

O Arquivo `docker-compose` provisiona cluster de mongodb com replica set de 3 instâncias: 

- mongo1:27017
- mongo2:27017
- mongo3:27017

---

## 💻 Pré-requisitos
* Docker
* Docker-Compose

---

## Subindo os nodes do Monogodb

```bash
docker-compose up -d mongo1 mongo2 mongo3
```

Verificando se os containers foram criados com sucesso

```bash
 docker container ls
```

Verificando as imagens que foram feitas download do docker-hub

```bash
 docker image ls
```

## Configurando Replica-set

> [!IMPORTANT]
> Os nomes da replica-set foi definido dentro do arquivo docker-compose.yml

```JavaScript

docker exec -it mongo1 /bin/bash

mongosh 

use loja

rs.initiate(
  {
    _id: "db-replica-set",
    members: [
      { _id: 0, host: "mongo1:27017",  priority: 2} ,
      { _id: 1, host: "mongo2:27017" , priority: 1} ,
      { _id: 2, host: "mongo3:27017" , priority: 1} 
    ]
  }
)


rs.config()

rs.status()

load("/scripts/importProdutos.js")

db.produtos.findOne()

```

## Criar os indices para o idProduto e array de Skus

```JavaScript
db.produtos.ensureIndex({ skus : 1});

db.produtos.ensureIndex({idProduto: 1}, { unique: true })

db.produtos.getIndexes();
```

## Criado as tags para organização das réplicas:

```JavaScript
conf = rs.conf()
conf.members[0].tags = { "dc": "SP"}
conf.members[1].tags = { "dc": "SP"}
conf.members[2].tags = { "dc": "RIO"}
rs.reconfig(conf)

rs.config().members;

```


# Pipelines no MongoDB

![Mongo db](/content/mongodb-agregacao.png)


No MongoDB, um pipeline de agregação é uma sequência de estágios que processam documentos em uma coleção, permitindo transformar, filtrar, agrupar e analisar dados de forma eficiente. Cada estágio recebe os documentos processados do estágio anterior e pode aplicar diversas operações.

Principais Estágios do Pipeline
* $match – Filtra documentos (equivalente ao WHERE no SQL).
* $group – Agrupa documentos (similar ao GROUP BY).
* $sort – Ordena os resultados.
* $project – Modifica o formato dos documentos retornados.
* $lookup – Realiza um join entre coleções.
* $unwind – Desnormaliza arrays, criando um documento para cada elemento.
* $limit – Restringe o número de documentos retornados.
* $skip – Pula um número específico de documentos.
* $addFields – Adiciona novos campos calculados.


## Filtrar os documentos

```JavaScript
db.produtos.aggregate([
  { $match: { idProduto: { $gt: 10, $lt: 50 } } }
])

```

## Contar o número total de SKUs por produto ($size)

```JavaScript
db.produtos.aggregate([
  { "$project": { "nomeProduto": 1, "quantidadeSkus": { "$size": "$skus" } } }
])

```


## Agrupar produtos por marca e contar quantos existem ($group)

```JavaScript
db.produtos.aggregate([
  { "$unwind": "$marcas" },
  { "$group": { "_id": "$marcas.nome", "totalProdutos": { "$sum": 1 } } }
])
```

## Calcular o preço médio dos produtos por categoria ($group)

```JavaScript
db.produtos.aggregate([
  { "$unwind": "$categorias" },
  { "$group": { "_id": "$categorias.nome", "precoMedio": { "$avg": "$valorProduto" } } }
])
```

## Criar um novo campo com $set para mostrar o preço final com desconto

```JavaScript
db.produtos.aggregate([
  { "$set": { "valorComDesconto": { "$multiply": ["$valorProduto", 0.9] } } }
])
```


## Transformar SKUs em documentos individuais ($unwind)

```JavaScript
db.produtos.aggregate([
  { "$unwind": "$skus" },
  { "$project": { "nomeProduto": 1, "idSku": "$skus.idSku", "nomeSku": "$skus.nome", "valor": "$skus.valor" } }
])
```


## Filtrar apenas produtos com SKUs acima de R$5000 ($match)

```JavaScript
db.produtos.aggregate([
  { "$unwind": "$skus" },
  { "$match": { "skus.valor": { "$gt": 5000 } } }
])
```


## Ordenar produtos pelo número de SKUs ($sort)

```JavaScript
db.produtos.aggregate([
  { "$project": { "nomeProduto": 1, "quantidadeSkus": { "$size": "$skus" } } },
  { "$sort": { "quantidadeSkus": -1 } }
])

```

## Criar um relatório consolidado dos produtos ($group e $push)

```JavaScript
 db.produtos.aggregate([
  { "$group": {
      "_id": null,
      "totalProdutos": { "$sum": 1 },
      "mediaValorProduto": { "$avg": "$valorProduto" },
      "produtos": { "$push": "$nomeProduto" }
  }}
])

```

## Mais um pipeline....

```JavaScript
db.produtos.aggregate([
  // Filtra produtos com idProduto entre 10 e 50
  { 
    $match: { idProduto: { $gt: 10, $lt: 50 } } 
  },

  //Desestrutura o array de SKUs para criar um documento por SKU
  { 
    $unwind: "$skus" 
  },

  // Agrupa os produtos contando a quantidade de SKUs
  { 
    $group: { 
      _id: "$idProduto", 
      nomeProduto: { $first: "$nomeproduto" }, 
      totalSKUs: { $sum: 1 }, 
      precoMedioSKU: { $avg: "$skus.valor" } 
    } 
  },

  //Ordena pelos produtos com maior quantidade de SKUs primeiro
  { 
    $sort: { totalSKUs: -1 } 
  },

  // Adiciona um campo para classificar o nível do produto baseado no número de SKUs
  { 
    $addFields: { 
      nivelProduto: { 
        $switch: {
          branches: [
            { case: { $gte: ["$totalSKUs", 10] }, then: "Alto" },
            { case: { $gte: ["$totalSKUs", 5] }, then: "Médio" }
          ],
          default: "Baixo"
        }
      }
    }
  }
])
```

## Salvar o resultado da consulta em outra collection

```JavaScript
db.produtos.aggregate([
  { "$project": { "nomeProduto": 1, "quantidadeSkus": { "$size": "$skus" } } },
  {  $out: "skus" }
])

 show collections;


 db.skus.findOne();

```

# PyMongoArrow
O Pymongoarrow é uma extensão do PyMongo que melhora a eficiência ao converter grandes volumes de dados do MongoDB para formatos compatíveis com Apache Arrow. Isso permite análises rápidas e eficientes em Pandas, NumPy e outras ferramentas de Data Science.

> [!IMPORTANT] 
> Apache Arrow é um framework de computação em colunas otimizado para processamento de dados em memória. Ele fornece um formato padronizado para representação de dados tabulares, permitindo operações eficientes entre diferentes linguagens e sistemas, como Pandas, Spark e Parquet. Seu design melhora a performance ao minimizar cópias de dados e maximizar o uso de CPU e cache.

### Subindo o ambiente do Jypyter

```bash
docker compose up -d jupyter_service

```


> [!IMPORTANT]
> Olhe os logs para pegar o endereço do Jupyter

## Abra o arquivo `pyMongoArrow.ipynb` que está dentro da pasta


## Vamos dar uma olhadinha na aplicação ??

### Subindo a aplicação FastApi

```bash
docker compose up -d api
```
> http://localhost:8000/docs


### CLI com a aplicação FastApi

> [!IMPORTANT]
> Se não tiver acesso a criar o pacote do fastApi, force a instalação de dentro do container ou tire o mapeamento do volumento 
> do arquivo docker comper
> `pip install --force-reinstall -e . `

```bash
docker exec -it fast-api-fia  /bin/bash

fia --help

fia consultarproduto --produto-id "67b531141a78374c04d16260"

```



## Configurando o Kafka Connect e seus conectores, que serão responsáveis,  pela leitura das informações em Mongodb

Criando a imagem com DockerFile

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

```bash
Consumindo mensagem mongo.loja.produtos

kafka-console-consumer --bootstrap-server localhost:9092 --topic mongo.loja.produtos --from-beginning
```

## Criando o worker para a leitura das mensagens no kafka


Vamos criar a estrutura abaixo

![Lab](/content/worker-python.png)


* app/__init__.py
* app/_config.py
* app/_ consumer.py
* app/_loggerWorker.py
* app/_main.py
* app/_processor.py
* __init__.py
* config.py
* consumer.py
* loggerWorker.py
* main.py
* processor.py


### Arquivos dentro da pasta app


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


## Criando a imagem docker


> [!IMPORTANT]
> Lembrar de informar o path do Dockerfile corretamente


```bash
docker build -t kafka-worker-consumer ./kafka-python

docker compose up -d kafka-worker-consumer

```

## Deu certo??