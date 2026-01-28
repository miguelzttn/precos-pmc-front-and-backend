import streamlit as st

from parts.image import display_product_image


def display_item_card(
    img_url: str,
    cd_produto: str,
    descricao: str,
    marca: str,
    ultima_atualizacao: str,
    produto_search_str: str,
):
    col_img, col_txt, col_btn = st.columns([1, 3, 1.2])

    with col_img:
        img = display_product_image(img_url)

    with col_txt:
        st.markdown(f"### {descricao.title()}")
        st.markdown(f"**Marca:** {marca.title()}")
        st.caption(f"Atualizado em: {ultima_atualizacao}")

    with col_btn:
        btn_key = f"btn_{cd_produto}_{ultima_atualizacao}_card_button"

        if st.button(
            label="Ver Preços",
            key=btn_key,
            type="primary",
            width="stretch",
        ):

            if "produto_selected_cd" in st.session_state:
                del st.session_state["produto_selected_cd"]

            if "produto_search_str" in st.session_state:
                del st.session_state["produto_search_str"]

            st.session_state["produto_selected_cd"] = cd_produto
            st.session_state["produto_search_str"] = produto_search_str

            st.switch_page("pages/produto.py")
