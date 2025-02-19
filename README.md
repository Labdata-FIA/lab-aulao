
# LAB MONGODB

---
## Disclaimer
> **Esta configuração é puramente para fins de desenvolvimento local e estudos**
> 

---


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

## Executando réplica-set Monogodb

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

# PyMongoArrow
O Pymongoarrow é uma extensão do PyMongo que melhora a eficiência ao converter grandes volumes de dados do MongoDB para formatos compatíveis com Apache Arrow. Isso permite análises rápidas e eficientes em Pandas, NumPy e outras ferramentas de Data Science.

> [!IMPORTANT] 
> Apache Arrow é um framework de computação em colunas otimizado para processamento de dados em memória. Ele fornece um formato padronizado para representação de dados tabulares, permitindo operações eficientes entre diferentes linguagens e sistemas, como Pandas, Spark e Parquet. Seu design melhora a performance ao minimizar cópias de dados e maximizar o uso de CPU e cache.

### Subindo o ambiente do Jypyter

```bash
docker compose up -d jupyter_service

```

## Abra o arquivo `pyMongoArrow.ipynb` que está dentro da pasta


## Vamos dar uma olhadinha na aplicação ??

### Subindo a aplicação FastApi

```bash
docker compose up -d api
```

## Configurando o Kafka Connect e seus conectores, que serão responsáveis,  pela leitura das informações em Mongodb

Criando a imagem com DockerFile

```bash

docker image build -t kafka-connet-debezium:3.0.7.Final  -f Dockerfile .

docker compose up -d  kafka-broker zookeeper connect
```

## Obseravndo os plugins criados

```bash
docker exec -it kafkaConect curl  http://localhost:8083/connector-plugins

```

## Criando os conectores


```bash
 
 curl -X PUT -d @conector-mongdb.json http://localhost:8083/connectors/connector-mongodb/config -H 'Content-Type: application/json' -H 'Accept: application/json'


//Ou via powershell
$response = Invoke-WebRequest -Uri "http://localhost:8083/connectors/connector-mongodb/config" -Method Put -Body (Get-Content -Path "conector-mongdb.json" -Raw) -ContentType "application/json"; $response.Content

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


