import streamlit as st
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from src.api import APIClient
from parts.styles import apply_custom_style
from parts.image import display_product_image
from parts.cards import display_item_card

PLACEHOLDER_IMG = "https://cdn-icons-png.flaticon.com/512/1178/1178479.png"
MAX_RESULTS_PER_PAGE = 5

st.set_page_config(
    page_title="Clique Economia Customizado", page_icon="🛒", layout="centered"
)

apply_custom_style()
api = APIClient()

# ------------------------------------------------------------------------------
# Placeholders

# --- HERO ---

placeholder_hero_image = st.empty()
placeholder_hero_title = st.empty()
placeholder_hero_subtitle = st.empty()


# --- FILTERS ---

with st.container():
    c1, c2 = st.columns([4, 1])
    with c1:
        placeholder_filters_search_input = st.empty()
    with c2:
        placeholder_filters_recent_toggle = st.empty()

placeholder_hero_image.image(
    "https://cliqueeconomia.curitiba.pr.gov.br/img/logo_prefeitura_branco.png",
    width=100,
)
placeholder_hero_title.title("🛒 Clique Economia")
placeholder_hero_subtitle.markdown(
    "##### Encontre os menores preços em Curitiba e economize."
)

filtro_busca = placeholder_filters_search_input.text_input(
    label="Filtro de busca",
    placeholder="O que você procura hoje? (Ex: Arroz, Leite...)",
    value=st.session_state.get("produto_search_str", ""),
    label_visibility="collapsed",
)
if filtro_busca:
    if "produto_search_str" in st.session_state:
        del st.session_state["produto_search_str"]
    st.session_state["produto_search_str"] = filtro_busca


placeholder_filters_recent_toggle.toggle(
    "Recentes", value=True, key="recent", help="Apenas preços dos últimos 30 dias"
)

# --- DADOS ---


def _query_from_api(query: str, recent_only: bool, results_per_page: int):
    return api.get(
        "busca/buscar",
        params={
            "query": query,
            "recent_only": recent_only,
            "results_per_page": results_per_page,
        },
    )


is_query_state = st.session_state.get("produto_search_str", "") != ""
is_initial_state = not is_query_state

data = {}
if is_query_state:
    data = _query_from_api(
        query=st.session_state.get("produto_search_str", ""),
        recent_only=st.session_state.get("recent", True),
        results_per_page=st.session_state.get("limit", MAX_RESULTS_PER_PAGE),
    )

is_not_found_state = is_query_state and data.get("total_count", 0) == 0

# ------------------------------------------------------------------------------
# Logica

if is_initial_state:

    st.divider()
    st.subheader("Sugestões de busca")

    exemplos = ["Café", "Açúcar", "Óleo"]

    cols = st.columns(len(exemplos))
    for i, ex in enumerate(exemplos):

        if cols[i].button(ex, use_container_width=True):
            if "produto_search_str" in st.session_state:
                del st.session_state["produto_search_str"]
            st.session_state["produto_search_str"] = ex
            st.rerun()
    
    # - disclaimer
    st.warning(
        "Este projeto é independente e não possui vínculo com a Prefeitura de Curitiba. \n\n"
        "Os dados apresentados são coletados de forma automatizada e podem conter imprecisões. \n\n"
        "Não nos responsabilizamos por eventuais erros ou omissões. \n\n"
        "Para mais informações, visite o [repositório no GitHub](https://github.com/miguelzttn/precos-pmc-front-and-backend)",
        icon="⚠️",
    )

    st.stop()

elif is_not_found_state:
    st.info("Nenhum produto encontrado. Tente termos mais genéricos.")
    st.stop()

else:

    search_string = st.session_state.get("produto_search_str", "")
    caption_text = "Exibindo {n} resultados para '{search}'".format(
        n=data.get("total_count", 0),
        search=data.get("query", ""),
    )

    st.caption(caption_text)

    for i, item in enumerate(data.get("produtos", [])):

        with st.container(border=True):
            img_url = item.get("nm_url_imagem") or PLACEHOLDER_IMG

            display_item_card(
                produto_search_str=data.get("query", ""),
                img_url=img_url,
                cd_produto=item.get("cd_produto"),
                descricao=item.get("nm_descricao_original"),
                marca=item.get("nm_marca", "N/A"),
                ultima_atualizacao=item.get("dt_ultima_atualizacao"),
                vl_ultimo_preco_mais_baixo=item.get("vl_ultimo_preco_mais_baixo"),
            )

        if i >= st.session_state.get("limit", MAX_RESULTS_PER_PAGE) - 1:

            load_more_btn = st.button(
                "Carregar mais resultados",
                width="stretch",
            )

            if load_more_btn:
                if "limit" in st.session_state:
                    del st.session_state["limit"]
                st.session_state["limit"] = (
                    st.session_state.get("limit", MAX_RESULTS_PER_PAGE)
                    + MAX_RESULTS_PER_PAGE
                )
                st.rerun()

            break


