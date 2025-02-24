
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


### Criando o Process Group
![Lab](/content/nifi1.png)


### Parameter Context

No Apache NiFi, Contexto de Parâmetros é um recurso que permite centralizar e gerenciar configurações reutilizáveis dentro de um fluxo de dados. Ele possibilita definir valores parametrizáveis para processadores, permitindo maior flexibilidade e facilidade na manutenção dos fluxos.

![Lab](/content/nifi2.png)


### Os principais benefícios incluem:
✅ Reutilização – Um único conjunto de parâmetros pode ser aplicado a vários componentes.
✅ Segurança – Parâmetros sensíveis, como credenciais, podem ser protegidos.
✅ Facilidade de Alteração – Ajustes podem ser feitos sem modificar diretamente os fluxos.



![Lab](/content/nifi3.png)

![Lab](/content/nifi4.png)

![Lab](/content/nifi5.png)


Para atribuir um Contexto de Parâmetro a um Grupo de Processos, clique em Configurar, na Paleta de Operação ou no menu de contexto do Grupo de Processos.

![Lab](/content/nifi6.png)


### Controller Services
No Apache NiFi, os Controller Services são componentes compartilháveis que fornecem funcionalidades comuns a vários processadores dentro de um fluxo de dados. Eles permitem centralizar configurações e melhorar a eficiência do processamento.

Exemplos de Controller Services:
🔹 DBCPConnectionPool – Gerencia conexões com bancos de dados.
🔹 SSLContextService – Configura SSL/TLS para comunicação segura.
🔹 AvroSchemaRegistry – Define esquemas de dados Avro para validação.

![Lab](/content/nifi7.png)

![Lab](/content/nifi8.png)

### Criando um Processor PublishKafka

![Lab](/content/nifi10.png)

![Lab](/content/nifi11.png)


|Property|Value|
|------------------|--------------|
|Kafka Connection Service|Kafka3ConnectionService|
|Topic Name|#{kafka-topic}|


### Criando um Funnel

![Lab](/content/nifi12.png)


### Deu tudo certo ???

Linguem de expressão
https://nifi.apache.org/docs/nifi-docs/html/expression-language-guide.html


## Vamos criar outro ProcessGroup com o nome de kafka

![Lab](/content/nifi13.png)

![Lab](/content/nifi14.png)

Configure o Parameter Context a um Grupo de Processos e crie os parametros novos com os nomes `kafka-topic-produto` e `kafka-group-produtos` com os valores `mongo.loja.produtos` e `group-produtos`, respectivamente e crie um novo Service.

![Lab](/content/nifi15.png)

![Lab](/content/nifi16.png)

![Lab](/content/nifi17.png)


> [!IMPORTANT]
> Não esqueça de habilitar o service

Teste o fluxo, atualizando o documento no mongodb.

## Criando um Process Group para o MiniIO, mas antes..

```bash
 docker compose up -d minio mc
```

![Lab](/content/nifi20.png)

## Criando Output Port e New Input Port