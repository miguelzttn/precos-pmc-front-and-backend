from datetime import date
from typing import List
from fastapi import APIRouter, Depends

from core.security import verify_api_key
from services.data_lake import query_duck_db
from schemas.produtos import ProdutoDetails 

router = APIRouter()

@router.get("/bairros/listar", dependencies=[Depends(verify_api_key)])
async def listar_bairros_disponiveis(cd_produto: int, dt_start: date, dt_end: date, nm_rede: str = None) -> List[str]:
    rede_filter = f" AND nm_rede = '{nm_rede}'" if nm_rede else ""
    query = f"""
        SELECT DISTINCT nm_bairro
        FROM f_precos_completa
        WHERE nm_bairro IS NOT NULL
        AND cd_produto = ?
        AND dt_referencia >= ? AND dt_referencia <= ?
        {rede_filter}
        ORDER BY nm_bairro
    """
    bairros = query_duck_db(query, [cd_produto, dt_start, dt_end]).to_dict(orient='records')
    return [bairro['nm_bairro'] for bairro in bairros]

@router.get("/redes/listar", dependencies=[Depends(verify_api_key)])
async def listar_redes_disponiveis(cd_produto: int, dt_start: date, dt_end: date, nm_bairro: str = None) -> List[str]:
    bairro_filter = f" AND nm_bairro = '{nm_bairro}'" if nm_bairro else ""
    query = f"""
        SELECT DISTINCT nm_rede
        FROM f_precos_completa
        WHERE cd_produto = ?
        AND dt_referencia >= ? AND dt_referencia <= ? 
        {bairro_filter}
        ORDER BY nm_rede
    """
    redes = query_duck_db(query, [cd_produto, dt_start, dt_end]).to_dict(orient='records')
    return [rede['nm_rede'] for rede in redes]

@router.get("/{cd_produto}", dependencies=[Depends(verify_api_key)])
async def get_produto(
    cd_produto: int,
    dt_start: date,
    dt_end: date,
    nm_bairro: str = None,
    nm_rede: str = None,
) -> ProdutoDetails:
    import time
    start = time.time()

    bairro_filter = f" AND nm_bairro = '{nm_bairro}'" if nm_bairro else ""
    rede_filter = f" AND nm_rede = '{nm_rede}'" if nm_rede else ""

    query_produto = f"""
        SELECT
            cd_produto,
            nm_produto,
            nm_tipo,
            nm_marca,
            COALESCE(nm_url_thumbnail, 'https://cdn-icons-png.flaticon.com/512/1178/1178479.png') AS nm_url_imagem,
            COALESCE(CONCAT('[', nm_source_name, '](', nm_source_link, ')'), '') AS nm_imagem_creditos_markdown
        FROM d_produtos
        WHERE cd_produto = ?
        LIMIT 1
    """
    produto = query_duck_db(
        query_produto, [cd_produto]
    ).to_dict(orient='records')[0]

    query_precos = f"""
        SELECT
            dt_referencia,
            AVG(vl_preco_atacado) AS vl_preco_medio, 
            MIN(vl_preco_atacado) AS vl_preco_minimo, 
            MAX(vl_preco_atacado) AS vl_preco_maximo
        FROM f_precos_completa
        WHERE dt_referencia >= ? AND dt_referencia <= ?
        AND cd_produto = ?
        {bairro_filter}
        {rede_filter}
        GROUP BY dt_referencia
        ORDER BY dt_referencia ASC
    """
    
    precos = query_duck_db(
        query_precos, [dt_start, dt_end, cd_produto]
    ).to_dict(orient='records')

    query_metricas = f"""
        WITH 
            precos_filtrados AS ({query_precos}),
            data_menor_preco AS (
                SELECT 
                    dt_referencia AS dt_menor_preco
                FROM precos_filtrados
                ORDER BY vl_preco_minimo ASC
                LIMIT 1
            ),
            data_menor_preco_estimado AS (
                SELECT 
                    dt_referencia AS dt_menor_preco_estimado
                FROM precos_filtrados
                ORDER BY vl_preco_minimo ASC
                LIMIT 1
            ),
            preco_menor_periodo AS (
                SELECT MIN(vl_preco_minimo) AS vl_menor_preco_periodo
                FROM precos_filtrados
            ),
            preco_final_periodo AS (
                SELECT LAST(vl_preco_minimo) AS vl_preco_final_periodo
                FROM precos_filtrados
            ),
            preco_estimado_periodo AS (
                SELECT
                    MAX(0) AS vl_preco_estimado_periodo
                FROM precos_filtrados
            ),
            preco_estimado_menor_periodo AS (
                SELECT
                    MAX(0) AS vl_menor_preco_estimado_periodo
                FROM precos_filtrados
            )
        SELECT
            dt_menor_preco,
            dt_menor_preco_estimado,
            COALESCE(ROUND(vl_menor_preco_periodo, 2), 0) AS vl_menor_preco_periodo,
            COALESCE(ROUND(vl_preco_final_periodo, 2), 0) AS vl_preco_final_periodo,
            COALESCE(ROUND(vl_preco_estimado_periodo, 2), 0) AS vl_preco_estimado_periodo,
            COALESCE(ROUND(vl_menor_preco_estimado_periodo, 2), 0) AS vl_menor_preco_estimado_periodo,
            COALESCE(ROUND(
                (vl_preco_final_periodo - vl_menor_preco_periodo)
            , 2), 0) AS vl_variacao_preco_periodo,
            COALESCE(ROUND(
                ((vl_preco_final_periodo - vl_menor_preco_periodo) / NULLIF(vl_menor_preco_periodo, 0)) * 100
            , 2), 0) AS pc_variacao_preco_periodo,
            COALESCE(ROUND(
                ((vl_preco_estimado_periodo - vl_menor_preco_estimado_periodo) / NULLIF(vl_menor_preco_estimado_periodo, 0)) * 100
            , 2), 0) AS pc_variacao_preco_estimado_periodo
        FROM 
            data_menor_preco,
            data_menor_preco_estimado,
            preco_menor_periodo, 
            preco_final_periodo, 
            preco_estimado_periodo, 
            preco_estimado_menor_periodo
    """
    metricas = query_duck_db(
        query_metricas, [dt_start, dt_end, cd_produto]
    ).to_dict(orient='records') or []
    metricas = metricas[0] if metricas else {}

    query_comparativo = f"""
        SELECT
            nm_rede,
            nm_bairro,
            CONCAT(nm_rede, ' (', nm_bairro, ')') AS nm_estabelecimento, 
            vl_preco_atacado,
            dt_referencia
        FROM f_precos_completa
        WHERE dt_referencia >= ? AND dt_referencia <= ?
        AND cd_produto = ?
        {bairro_filter}
        {rede_filter}
    """
    comparativo = query_duck_db(
        query_comparativo, [dt_start, dt_end, cd_produto]
    ).to_dict(orient='records')

    query_enderecos_mais_baratos = f"""
        WITH precos AS ({query_comparativo})
        SELECT
            '- **' || p.nm_rede ||
            ' - ' || p.nm_bairro || '**: ' ||
            '[' || p.nm_rede || ' (' || p.nm_bairro || ')]' ||
            '(https://www.google.com/maps/search/?api=1&query=' ||
            url_encode(
                e.nm_endereco_logradouro || ' ' || e.nm_endereco_numero
            ) ||
            ') *Atualizado:* ' ||
            strftime(p.dt_referencia, '%d/%m/%Y') AS descricao
        FROM f_precos_completa p
        LEFT JOIN d_empresas e
            ON p.nm_rede = e.nm_rede
            AND p.nm_bairro = e.nm_bairro
        QUALIFY 
            ROW_NUMBER() OVER (PARTITION BY p.nm_rede, p.nm_bairro ORDER BY p.vl_preco_atacado ASC) == 1
        ORDER BY p.vl_preco_atacado ASC
        LIMIT 5
    """
    enderecos_mais_baratos = query_duck_db(
        query_enderecos_mais_baratos, [dt_start, dt_end, cd_produto]
    ).to_dict(orient='records') or []

    end = time.time()
    print(f"get_produto executed in {end - start} seconds")

    return ProdutoDetails(
        **produto,
        obj_metricas=metricas,
        obj_chart_trend=precos,
        obj_chart_comparativo=comparativo,
        obj_enderecos_mais_baratos=enderecos_mais_baratos,
    )
