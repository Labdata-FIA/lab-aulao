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