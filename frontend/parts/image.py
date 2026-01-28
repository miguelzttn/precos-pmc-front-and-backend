from streamlit import markdown as st_markdown


def display_product_image(img_url: str) -> None:
    return st_markdown(
        f"""
            <div class="product-img-container">
                <img src="{img_url}" style="max-height: 90px; max-width: 100%;">
            </div>
        """,
        unsafe_allow_html=True,
    )
