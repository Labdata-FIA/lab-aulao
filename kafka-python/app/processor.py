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