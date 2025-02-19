from typing import List
from app.models.produto import Produto, Sku, Marca, Categoria, Imagem
from bson import ObjectId

class ProdutoMapper:

    @staticmethod
    def from_mongo_to_response(mongo_data) -> Produto:
        """
        Converte os dados de um produto no formato armazenado no MongoDB
        para o formato esperado pela resposta da API.
        """
        produto = Produto(
            idProduto=mongo_data["idProduto"],
            Nome=mongo_data["nomeProduto"],
            valorProduto=mongo_data["valorProduto"],
            idSkus=mongo_data["idSkus"],
            skus=[Sku(**sku) for sku in mongo_data["skus"]],
            marcas=[Marca(**marca) for marca in mongo_data["marcas"]],
            categorias=[Categoria(**categoria) for categoria in mongo_data["categorias"]],
            imagens=[Imagem(**imagem) for imagem in mongo_data["imagens"]]
        )
        return produto

    @staticmethod
    def from_request_to_mongo(produto: Produto) -> dict:
        """
        Converte os dados recebidos pela API no formato de produto para
        o formato que o MongoDB espera.
        """
        return {
            "idProduto": produto.idProduto,
            "nomeProduto": produto.Nome,
            "valorProduto": produto.valorProduto,
            "idSkus": produto.idSkus,
            "skus": [sku.dict() for sku in produto.skus],
            "marcas": [marca.dict() for marca in produto.marcas],
            "categorias": [categoria.dict() for categoria in produto.categorias],
            "imagens": [imagem.dict() for imagem in produto.imagens]
        }

    @staticmethod
    def from_mongo_to_list(mongo_data) -> List[Produto]:
        """
        Converte uma lista de documentos MongoDB para uma lista de objetos Produto.
        """
        return [ProdutoMapper.from_mongo_to_response(data) for data in mongo_data]
