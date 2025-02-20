import typer
from pymongo import MongoClient
from bson import ObjectId
from app.config import settings
from app.models.produto import Produto
import json
import asyncio

main = typer.Typer(name="Fia CLI")

# Conexão com o MongoDB
client = MongoClient(settings.DATABASE_URL)
db = client[settings.DATABASE]
produto_collection = db[settings.COLLECTION_PRODUCT]


# Função para converter documento BSON para JSON serializável
def serialize_doc(doc):
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

# Método CLI para consultar um produto
@main.command()
def consultarProduto(produto_id: str = typer.Option(None, help="ID do produto (opcional)")):
    """Consultar um produto no mongodb"""
       
    async def find_product():
     
        if produto_id:
            filtro = {"_id": ObjectId(produto_id)}
        else:
            filtro = {}  # Retorna qualquer produto existente
        
        produto = produto_collection.find_one(filtro)
     
        if produto:
            print(json.dumps(serialize_doc(produto), indent=4))
        else:
            print("Produto não encontrado.")  
    asyncio.run(find_product())


@main.command()
def shell():
    """shell"""   
    print("shell")