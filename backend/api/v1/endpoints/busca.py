import time
import unicodedata
from datetime import date, timedelta
from typing import List
from fastapi import APIRouter, Depends

from core.security import verify_api_key
from services.data_lake import query_duck_db
from schemas.produtos import Produto, ProdutoResponse, SearchProdutoResponse 

router = APIRouter(prefix="")

def _handle_query(query: str) -> str:
    
    # Remove leading and trailing whitespace
    query = query.strip()

    # Remove accents and special characters
    query = ''.join(
        c for c in unicodedata.normalize('NFD', query)
        if unicodedata.category(c) != 'Mn'
    )

    # Convert to uppercase
    query = query.upper()

    # Breeak spaces into % for wildcard search
    query = '%'.join(query.split())

    return query

@router.get("/buscar",  dependencies=[Depends(verify_api_key)])
async def buscar_produtos(
    query: str,
    recent_only: bool = False,
    results_per_page: int = 10,
    page: int = 1,
) -> SearchProdutoResponse:
    offset = (page - 1) * results_per_page

    handled_query = _handle_query(query)

    recent_only_clause = f" AND dt_ultima_atualizacao >= '{(date.today() + timedelta(days=-30)).isoformat()}'" if recent_only else ""

    base_query = f"""
        SELECT DISTINCT
            cd_produto,
            nm_produto,
            nm_tipo,
            nm_marca,
            dt_ultima_atualizacao,
            vl_ultimo_preco_mais_baixo,
            nm_descricao_original,
            nm_url_thumbnail,
            COALESCE(nm_url_thumbnail, 'https://cdn-icons-png.flaticon.com/512/1178/1178479.png') AS nm_url_imagem,
            COALESCE(CONCAT('[', nm_source_name, '](', nm_source_link, ')'), '') AS nm_imagem_creditos_markdown
        FROM d_produtos
        WHERE nm_descricao_original LIKE ?  
        {recent_only_clause}
        ORDER BY nm_url_thumbnail ASC
        LIMIT ? OFFSET ?
    """

    params = [f"%{handled_query}%", results_per_page, offset]
    produtos_df = query_duck_db(base_query, params)

    total_count_query = """
        SELECT COUNT(*) AS total_count
        FROM d_produtos
        WHERE nm_descricao_original LIKE ?
    """
    total_count_df = query_duck_db(total_count_query, [f"%{handled_query}%"])
    total_count = total_count_df.iloc[0]['total_count']

    produtos = [
        ProdutoResponse(
            cd_produto=row['cd_produto'],
            nm_produto=row['nm_produto'],
            nm_tipo=row['nm_tipo'],
            nm_marca=row['nm_marca'],
            nm_url_imagem=row['nm_url_imagem'],
            dt_ultima_atualizacao=row['dt_ultima_atualizacao'],
            nm_descricao_original=row['nm_descricao_original'],
            nm_imagem_creditos_markdown=row['nm_imagem_creditos_markdown'],
            vl_ultimo_preco_mais_baixo=row['vl_ultimo_preco_mais_baixo'],
        )
        for _, row in produtos_df.iterrows()
    ]

    return SearchProdutoResponse(
        query=query,
        handled_query=handled_query,
        produtos=produtos,
        total_count=total_count,
        page=page,
        results_per_page=results_per_page,
    )