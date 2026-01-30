from datetime import date
from typing import List, Optional
from pydantic import BaseModel

class Produto(BaseModel):
    cd_produto: Optional[int] = None
    nm_produto: Optional[str] = None
    nm_tipo: Optional[str] = None
    nm_marca: Optional[str] = None
    nm_descricao_original: Optional[str] = None
    dt_ultima_atualizacao: Optional[date] = None
    dt_ultima_atualizacao_ge: Optional[date] = None
    dt_ultima_atualizacao_le: Optional[date] = None

class ProdutoGetResposte(BaseModel):
    cd_produto: int
    nm_descricao_original: str

class ProdutoResponse(BaseModel):
    cd_produto: int
    nm_produto: str
    nm_tipo: str
    nm_marca: str
    nm_descricao_original: str
    dt_ultima_atualizacao: date
    vl_ultimo_preco_mais_baixo: Optional[float] = None
    nm_url_imagem: str
    nm_imagem_creditos_markdown: str

class ProdutoDetails(BaseModel):
    cd_produto: int
    nm_produto: str
    nm_tipo: str
    nm_marca: str
    nm_url_imagem: str
    nm_imagem_creditos_markdown: str
    
    obj_metricas: dict
    obj_chart_trend: List[dict]
    obj_chart_comparativo: List[dict]
    obj_enderecos_mais_baratos: List[dict]

class SearchProdutoResponse(BaseModel):
    query: str
    handled_query: str
    produtos: List[ProdutoResponse]
    total_count: int
    page: int
    results_per_page: int