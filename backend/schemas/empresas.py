from datetime import date
from typing import Optional
from pydantic import BaseModel

class Empresa(BaseModel):
    nm_rede: Optional[str] = None
    nm_bairro: Optional[str] = None
    nm_endereco_logradouro: Optional[str] = None
    nm_endereco_numero: Optional[str] = None
    dt_ultima_atualizacao: Optional[date] = None

class EmpresaResponse(BaseModel):
    nm_rede: str
    nm_bairro: str
    nm_endereco_logradouro: str
    nm_endereco_numero: str
    dt_ultima_atualizacao: date