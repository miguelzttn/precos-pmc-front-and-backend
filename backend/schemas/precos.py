from datetime import date
from typing import Optional
from pydantic import BaseModel

class Preco(BaseModel):
    nm_rede: Optional[str] = None
    nm_bairro: Optional[str] = None
    cd_produto: Optional[int] = None
    dt_ultima_atualizacao: Optional[date] = None
    nm_tipo_preco_varejo: Optional[str] = None
    vl_preco_varejo: Optional[float] = None
    nm_tipo_preco_atacado: Optional[str] = None
    vl_preco_atacado: Optional[float] = None
    dt_ultima_atualizacao_ge: Optional[date] = None
    dt_ultima_atualizacao_le: Optional[date] = None


class PrecoResponse(BaseModel):
    nm_rede: str
    nm_bairro: str
    cd_produto: int
    dt_ultima_atualizacao: date
    nm_tipo_preco_varejo: str
    vl_preco_varejo: float
    nm_tipo_preco_atacado: str
    vl_preco_atacado: float
