import streamlit as st
import altair as alt
import polars as pl
import urllib.parse
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo
from typing import List

from parts.styles import apply_custom_style
from parts.image import display_product_image
from src.api import APIClient, backend as api

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Detalhes do Produto", layout="wide")

apply_custom_style()

# ------------------------------------------------------------------------------
# Placeholders

# --- HEADER ---

col_buton, col_image, col_title, col_filters = st.columns([1, 2, 4, 2])

with col_buton:
    st.write("")
    placeholder_title_button_return = st.empty()

with col_image:
    st.write("")  # Skip line
    placeholder_highlight_product_image = st.empty()

with col_title:
    placeholder_title = st.empty()

    col_marca, col_tipo, _ = st.columns([2, 2, 3])
    with col_tipo:
        placeholder_title_tipo = st.empty()
    with col_marca:
        placeholder_title_marca = st.empty()

with col_filters:
    st.write("")  # Skip line
    placeholder_title_filter_date = st.empty()

    col_bairro, col_rede = st.columns([2, 2])
    with col_bairro:
        placeholder_title_filter_bairro = st.empty()
    with col_rede:
        placeholder_title_filter_rede = st.empty()

placeholder_hero_divider = st.empty()

# --- MAIN SECTION ---
col_highlights, col_chart = st.columns([1, 2.5])

with col_highlights:

    col_highlights_l1_1, col_highlights_l1_2 = st.columns(2)
    with col_highlights_l1_1:
        placeholder_highlight_menor_preco = st.empty()

    with col_highlights_l1_2:
        placeholder_highlight_estimado_atual = st.empty()

    col_highlights_l2_1, col_highlights_l2_2 = st.columns(2)
    with col_highlights_l2_1:
        placeholder_highlight_minimo_periodo = st.empty()

    with col_highlights_l2_2:
        placeholder_highlight_estimado_minimo = st.empty()


with col_chart:
    placeholder_chart = st.empty()

placeholder_main_divider = st.empty()

# --- COMPARATIVO POR ESTABELECIMENTO ---
placeholder_comparativo_subheader = st.empty()
placeholder_comparativo_chart = st.empty()
placeholder_comparativo_divider = st.empty()

# --- ENDERECOS DOS ESTABELECIMENTOS ---
placeholder_enderecos_subheader = st.empty()
placeholder_enderecos_bullet_1 = st.empty()
placeholder_enderecos_bullet_2 = st.empty()
placeholder_enderecos_bullet_3 = st.empty()
placeholder_enderecos_bullet_4 = st.empty()
placeholder_enderecos_bullet_5 = st.empty()

# ------------------------------------------------------------------------------
# Dependem do Cache

cd_produto = st.session_state.get("produto_selected_cd")
if not cd_produto:
    placeholder_title.error(
        "Nenhum produto selecionado. Por favor, volte à página principal e selecione um produto."
    )
    st.stop()

end_date = st.session_state.get("dt_produto_end")
end_date = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.now()

start_date = st.session_state.get("dt_produto_start")
start_date = (
    datetime.strptime(start_date, "%Y-%m-%d")
    if start_date
    else end_date - timedelta(days=30)
)

selected_dates = placeholder_title_filter_date.date_input(
    label="Filtrar período", value=(start_date, end_date), format="DD/MM/YYYY"
)

# Atualiza o session_state se um intervalo completo [início, fim] for selecionado
is_intervalo_selecionado = (
    isinstance(selected_dates, tuple) and len(selected_dates) == 2
)
if is_intervalo_selecionado:
    if "dt_produto_start" in st.session_state:
        del st.session_state["dt_produto_start"]
    st.session_state["dt_produto_start"] = selected_dates[0].strftime("%Y-%m-%d")

    if "dt_produto_end" in st.session_state:
        del st.session_state["dt_produto_end"]
    st.session_state["dt_produto_end"] = selected_dates[1].strftime("%Y-%m-%d")

# ------------------------------------------------------------------------------
# Estaticos

if placeholder_title_button_return.button("← Voltar", width=100):
    if "nm_bairro_selected" in st.session_state:
        del st.session_state["nm_bairro_selected"]
    if "nm_rede_selected" in st.session_state:
        del st.session_state["nm_rede_selected"]
    if "produto_selected_cd" in st.session_state:
        del st.session_state["produto_selected_cd"]
    if "dt_produto_start" in st.session_state:
        del st.session_state["dt_produto_start"]
    if "dt_produto_end" in st.session_state:
        del st.session_state["dt_produto_end"]
    st.switch_page("main.py")

placeholder_comparativo_subheader.subheader("🟢 Comparativo por Estabelecimento")

placeholder_enderecos_subheader.subheader(
    "📍 Endereço dos estabelecimentos mais em conta"
)

placeholder_hero_divider.divider()
placeholder_main_divider.divider()
placeholder_comparativo_divider.divider()

# ------------------------------------------------------------------------------
# Busca de Dados


def _get_bairro_filter_values_from_api(
    cd_produto: int, dt_start: date, dt_end: date, nm_rede_selected: str = None
) -> List[str]:
    params = {"cd_produto": cd_produto, "dt_start": dt_start, "dt_end": dt_end}
    if nm_rede_selected and nm_rede_selected != "Todas":
        params["nm_rede"] = nm_rede_selected
    else:
        params["nm_rede"] = None
    return api.get("produtos/bairros/listar", params=params)


def _get_rede_filter_values_from_api(
    cd_produto: int, dt_start: date, dt_end: date, nm_bairro_selected: str = None
) -> List[str]:
    params = {"cd_produto": cd_produto, "dt_start": dt_start, "dt_end": dt_end}
    if nm_bairro_selected and nm_bairro_selected != "Todos":
        params["nm_bairro"] = nm_bairro_selected
    else:
        params["nm_bairro"] = None
    return api.get("produtos/redes/listar", params=params)


def _get_produto_from_api(
    cd_produto: int,
    dt_start: date,
    dt_end: date,
    nm_bairro: str = None,
    nm_rede: str = None,
) -> dict:
    return api.get(
        f"produtos/{cd_produto}",
        params={
            "dt_start": dt_start,
            "dt_end": dt_end,
            "nm_bairro": nm_bairro if nm_bairro != "Todos" else None,
            "nm_rede": nm_rede if nm_rede != "Todas" else None,
        },
    )


with st.spinner("Carregando dados do produto..."):

    filtro_bairro = _get_bairro_filter_values_from_api(
        cd_produto=cd_produto,
        dt_start=start_date.date(),
        dt_end=end_date.date(),
        nm_rede_selected=st.session_state.get("nm_rede_selected"),
    )
    filtro_rede = _get_rede_filter_values_from_api(
        cd_produto=cd_produto,
        dt_start=start_date.date(),
        dt_end=end_date.date(),
        nm_bairro_selected=st.session_state.get("nm_bairro_selected"),
    )

    produto = (
        _get_produto_from_api(
            cd_produto=cd_produto,
            dt_start=start_date.date(),
            dt_end=end_date.date(),
            nm_bairro=st.session_state.get("nm_bairro_selected"),
            nm_rede=st.session_state.get("nm_rede_selected"),
        )
        or {}
    )

    if produto.get("cd_produto", 0) != cd_produto:
        placeholder_chart.error("Produto não encontrado para o período selecionado.")
        st.stop()

    metricas = produto.get("obj_metricas", {})
    precos = produto.get("obj_chart_trend", [])
    comparativo = produto.get("obj_chart_comparativo", [])
    enderecos_mais_baratos = produto.get("obj_enderecos_mais_baratos", [])

    if len(precos) == 0:
        placeholder_chart.error("Preços não encontrados para o período selecionado.")
        st.stop()

    df_precos = pl.from_dicts(precos)
    df_melted = df_precos.to_pandas().melt(
        id_vars=["dt_ultima_atualizacao"],
        value_vars=["vl_preco_minimo", "vl_preco_maximo", "vl_preco_medio"],
        var_name="Tipo",
        value_name="Preço",
    )

    df_all_pd = pl.from_dicts(comparativo).to_pandas()

# ------------------------------------------------------------------------------
# Preenche Placeholders

with st.spinner("Atualizando painel..."):

    # Informacoes do produto
    placeholder_title.title(f"{produto.get('nm_produto', '').strip()}")
    placeholder_title_marca.badge(f"{produto.get('nm_marca')}", color="yellow")
    placeholder_title_tipo.badge(
        f"**Código:** {produto.get('cd_produto')}", color="gray"
    )

    # Atualiza listas de opções
    if not st.session_state.get("nm_redes_disponiveis"):
        st.session_state["nm_redes_disponiveis"] = ["Todas"] + filtro_rede
    if not st.session_state.get("nm_bairros_disponiveis"):
        st.session_state["nm_bairros_disponiveis"] = ["Todos"] + filtro_bairro

    idx_bairro = st.session_state.get("nm_bairros_disponiveis", ["Todos"]).index(
        st.session_state.get("nm_bairro_selected")
        if isinstance(st.session_state.get("nm_bairro_selected"), str)
        else "Todos"
    )

    idx_rede = st.session_state.get("nm_redes_disponiveis", ["Todas"]).index(
        st.session_state.get("nm_rede_selected") or 0
        if isinstance(st.session_state.get("nm_rede_selected"), str)
        else "Todas"
    )

    placeholder_title_filter_bairro.selectbox(
        "Filtrar Bairro",
        options=st.session_state.get("nm_bairros_disponiveis", []),
        index=idx_bairro,
        key="nm_bairro_selected",
    )

    placeholder_title_filter_rede.selectbox(
        "Filtrar Rede",
        options=st.session_state.get("nm_redes_disponiveis", []),
        index=idx_rede,
        key="nm_rede_selected",
    )

    # Métricas
    placeholder_highlight_menor_preco.metric(
        "Menor Preço " + metricas.get("dt_menor_preco", ""),
        f"R$ {metricas.get('vl_menor_preco_periodo', 0):,.2f}".replace(".", ","),
        delta=(
            f"R$ {metricas.get('vl_variacao_preco_periodo', 0):,.2f} ({metricas.get('pc_variacao_preco_periodo', 0):.2f}%)"
            if metricas.get("pc_variacao_preco_periodo", 0) > 0
            else "Melhor preço!"
        ),
        delta_color="inverse",
    )

    placeholder_highlight_minimo_periodo.metric(
        "Mínimo no Período",
        f"R$ {metricas.get('vl_menor_preco_periodo', 0):,.2f}".replace(".", ","),
    )

    placeholder_highlight_estimado_atual.metric(
        "✨ " + metricas.get("dt_menor_preco_estimado", ""),
        f":yellow[R$ {metricas.get('vl_preco_estimado_periodo', 0):,.2f}]".replace(
            ".", ","
        ),
        delta=(
            f"R$ {metricas.get('vl_variacao_preco_estimado_periodo', 0):,.2f} ({metricas.get('pc_variacao_preco_estimado_periodo', 0):.2f}%)"
            if metricas.get("pc_variacao_preco_estimado_periodo", 0) > 0
            else "Melhor preço!"
        ),
        delta_color="inverse",
        help="Projeção realizada",
    )

    placeholder_highlight_estimado_minimo.metric(
        "✨ Mínimo estimado",
        f":yellow[R$ {metricas.get('vl_menor_preco_estimado_periodo', 0):,.2f}]".replace(
            ".", ","
        ),
        help="Projeção realizada",
    )

    # Imagem do produto
    img_url = produto.get("nm_url_imagem")
    placeholder_highlight_product_image.markdown(
        f"""
        <div class="product-img-highlight">
            <img src="{img_url}" style="max-height: 90px; max-width: 50%;">
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Gráfico de variação de preço
    chart = (
        alt.Chart(df_melted)
        .mark_line(interpolate="monotone")
        .encode(
            x=alt.X("dt_ultima_atualizacao:T", title="Data"),
            y=alt.Y("Preço:Q", title="Preço (R$)", scale=alt.Scale(zero=False)),
            color=alt.Color(
                "Tipo:N", scale=alt.Scale(range=["#FFFFFF", "#FFE600", "#99FF00"])
            ),
            strokeDash=alt.condition(
                alt.datum.Tipo == "Média",
                alt.value([0, 0]),
                alt.value([4, 4]),
            ),
            tooltip=["dt_ultima_atualizacao", "Tipo", "Preço"],
        )
        .properties(height=400)
        .interactive()
    )
    placeholder_chart.altair_chart(chart, width="stretch")

    # Gráfico comparativo por estabelecimento
    if not df_all_pd.empty:
        selection = alt.selection_point(fields=["nm_rede", "nm_bairro"], name="sel")

        chart_estab = (
            alt.Chart(df_all_pd)
            .mark_tick(thickness=4, size=20, orient="horizontal", cursor="pointer")
            .encode(
                x=alt.X(
                    "vl_preco_atacado:Q",
                    title="Preço Atacado (R$)",
                    scale=alt.Scale(zero=False),
                ),
                y=alt.Y(
                    "nm_estabelecimento:N",
                    title=None,
                    sort=alt.EncodingSortField(field="vl_preco_atacado", op="mean"),
                ),
                color=alt.condition(
                    selection, alt.value("#99FF00"), alt.value("#267D69")
                ),
                tooltip=[
                    "nm_rede",
                    "nm_bairro",
                    "vl_preco_atacado",
                    "dt_ultima_atualizacao",
                ],
            )
            .add_params(selection)
            .properties(height=df_all_pd["nm_estabelecimento"].nunique() * 35 + 50)
        )

        placeholder_comparativo_chart.altair_chart(
            chart_estab,
            width="stretch",
        )

    # Endereços dos estabelecimentos mais baratos
    for i, endereco in enumerate(enderecos_mais_baratos):

        if i == 0:
            placeholder_enderecos_bullet_1.markdown(endereco.get("descricao", ""))
        elif i == 1:
            placeholder_enderecos_bullet_2.markdown(endereco.get("descricao", ""))
        elif i == 2:
            placeholder_enderecos_bullet_3.markdown(endereco.get("descricao", ""))
        elif i == 3:
            placeholder_enderecos_bullet_4.markdown(endereco.get("descricao", ""))
        elif i == 4:
            placeholder_enderecos_bullet_5.markdown(endereco.get("descricao", ""))
