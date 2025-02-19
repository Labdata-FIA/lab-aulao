from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.produto import Produto
from app.models.produtoMapper import ProdutoMapper
from pymongo import MongoClient
from app.config import settings
from bson import ObjectId


# Conexão com o MongoDB
client = MongoClient(settings.DATABASE_URL)
db = client[settings.DATABASE]
produto_collection = db[settings.COLLECTION_PRODUCT]

router = APIRouter()

@router.get("/produtos/{produto_id}", response_model=Produto, status_code=status.HTTP_200_OK)
async def get_produto(produto_id: str):
    produto = produto_collection.find_one({"_id": ObjectId(produto_id)})
    if not produto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado..")
    
    # Mapeia o produto do MongoDB para o modelo de resposta
    produto_response = ProdutoMapper.from_mongo_to_response(produto)
    return produto_response

@router.put("/produtos/", response_model=Produto, status_code=status.HTTP_201_CREATED)
async def save_produto(produto: Produto):
    produto_dict = ProdutoMapper.from_request_to_mongo(produto)
    #produto_collection.insert_one(produto_dict)
    
     # Converte o modelo para dicionário
    #produto_dict = produto.dict()

    result = produto_collection.replace_one(
        {"idProduto": produto.idProduto},  # Busca pelo idProduto
        produto_dict,  # Novo documento a ser inserido ou atualizado
        upsert=True  # Habilita inserção se não existir
    )

    return produto

@router.delete("/produtos/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_produto(produto_id: str):
    result = produto_collection.delete_one({"_id": ObjectId(produto_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
    return None
