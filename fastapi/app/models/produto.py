from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId


# Modelos internos para produtos, SKUs, marcas, categorias e imagens
class Sku(BaseModel):
    idSku: int
    nome: str
    valor: float
    estoque: int
    cor: str

class Marca(BaseModel):
    idMarca: int
    nome: str

class Categoria(BaseModel):
    idCategoria: int
    nome: str

class Imagem(BaseModel):
    idImagem: int
    url: str

# Modelo de Produto
class Produto(BaseModel):
    idProduto: int
    Nome: str
    valorProduto: float
    idSkus: List[int]
    skus: List[Sku]
    marcas: List[Marca]
    categorias: List[Categoria]
    imagens: List[Imagem]

    class Config:
        orm_mode = True  # Isso permite que o Pydantic saiba como lidar com tipos complexos, como o ObjectId.
