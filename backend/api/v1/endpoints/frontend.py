import time
from typing import List
from fastapi import APIRouter, Depends

from core.security import verify_api_key
from services.data_lake import query_duck_db, mount_query
from schemas.precos import Preco, PrecoResponse 
from schemas.empresas import Empresa, EmpresaResponse 
from schemas.produtos import Produto, ProdutoGetResposte, ProdutoResponse 

router = APIRouter(prefix="/frontend")

@router.put("/precos", dependencies=[Depends(verify_api_key)])
async def list_precos(preco: Preco = None, page: int = 1, results_per_page: int = 100) -> List[PrecoResponse]:
    
    fields = preco.model_dump() if preco else None
    query, params = mount_query('f_precos', fields, page, results_per_page)

    results = query_duck_db(query, params).to_dict(orient='records')
    response = []

    for i, result in enumerate(results):
        prod_response = PrecoResponse(**result)
        response.append(prod_response)


    return response

@router.put("/empresas", dependencies=[Depends(verify_api_key)])
async def list_empresas(empresa: Empresa = None, page: int = 1, results_per_page: int = 100) -> List[EmpresaResponse]:

    fields = empresa.model_dump() if empresa else None
    query, params = mount_query('d_empresas', fields, page, results_per_page)

    results = query_duck_db(query, params).to_dict(orient='records')
    response = []

    for result in results:
        prod_response = EmpresaResponse(**result)
        response.append(prod_response)

    return response

@router.put("/produtos", dependencies=[Depends(verify_api_key)])
async def detail_produtos(produto: Produto = None, page: int = 1, results_per_page: int = 100) -> List[ProdutoResponse]:
    start_time = time.time()
    fields = produto.model_dump() if produto else None
    print(f"PUT /produtos received with fields: {fields}")
    query, params = mount_query('d_produtos', fields, page, results_per_page)

    results = query_duck_db(query, params).to_dict(orient='records')
    response = []

    for result in results:
        prod_response = ProdutoResponse(**result)
        response.append(prod_response)

    print(f"PUT /produtos took {(time.time() - start_time):.2f} seconds")

    return response

@router.get("/produtos", dependencies=[Depends(verify_api_key)])
async def list_produtos(page: int = 1, results_per_page: int = 100) -> List[ProdutoGetResposte]:

    query, params = mount_query(
        table='d_produtos', 
        dump=None, 
        page=page, 
        results_per_page=results_per_page, 
        columns=['cd_produto', 'nm_descricao_original']
    )

    results = query_duck_db(query, params).to_dict(orient='records')
    response = []

    for result in results:
        prod_response = ProdutoGetResposte(**result)
        response.append(prod_response)

    return response