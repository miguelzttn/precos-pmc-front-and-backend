import streamlit as st


def apply_custom_style():

    st.markdown(
        f"""
        <style>
            /* Estilo do Card */
            [data-testid="stMetric"] {{
                background-color: #267D69;
                padding: 10px;
                border-radius: 10px;
            }}
            
            /* Padronização das imagens nos cards */
            .product-img-container {{
                background-color: white;
                border-radius: 8px;
                padding: 5px;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100px;
            }}

            /* Padronização das imagens nos highlights */
            .product-img-highlight {{
                background-color: white;
                border-radius: 8px;
                padding: 5px;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 150px;
            }}


            /* Botão Primário (Verde limão com texto escuro) */
            div.stButton > button[kind="primary"] {{
                color: #1C6B59 !important;
                background-color: #99FF00 !important;
                border: none;
                transition: transform 0.2s ease;
            }}
            
            div.stButton > button[kind="primary"]:hover {{
                transform: scale(1.02);
            }}

            /* Inputs e Toggles */
            .stTextInput input {{
                border-radius: 20px;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )
