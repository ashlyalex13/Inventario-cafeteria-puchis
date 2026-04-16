import streamlit as st
import requests
import pandas as pd
from datetime import datetime


st.markdown("""
    <style>
        header {visibility: hidden;}
        .block-container {
            padding-top: 0rem;
        }
    </style>
""", unsafe_allow_html=True)


API_URL = "http://localhost:8000"

st.set_page_config(page_title="Cafetería Puchis ☕", layout="wide")


# ======================
# SIDEBAR 
# ======================

st.sidebar.title("Cafetería Puchis")

if "menu" not in st.session_state:
    st.session_state.menu = "Inicio"

if st.sidebar.button("🏠 Inicio", use_container_width=True):
    st.session_state.menu = "Inicio"

if st.sidebar.button("📦 Productos", use_container_width=True):
    st.session_state.menu = "Productos"

if st.sidebar.button("💰 Ventas", use_container_width=True):
    st.session_state.menu = "Ventas"

if st.sidebar.button("💸 Gastos", use_container_width=True):
    st.session_state.menu = "Gastos"

if st.sidebar.button("📉 Pérdidas", use_container_width=True):
    st.session_state.menu = "Pérdidas"

if st.sidebar.button("🧾 Cierre de caja", use_container_width=True):
    st.session_state.menu = "Cierre de caja"

menu = st.session_state.menu


col1, col2 = st.columns([1, 6])

with col1:
    st.markdown(f"{datetime.now().strftime('%H:%M:%S')}")

with col2:
    st.markdown(
        "<div style='text-align: right;'>"
        "<button style='padding:8px 15px; border-radius:8px; border:none; background-color:#eee;'>👤 Admin</button>"
        "</div>",
        unsafe_allow_html=True
    )

# TITULO
st.markdown("""
<h2 style='margin-bottom:10px;'>
☕ Cafetería Puchis - Sistema de Inventario
</h2>
""", unsafe_allow_html=True)

st.divider()

st.markdown("""
<style>

/* BOTONES GRANDES */
div.stButton > button {
    height: 110px;
    font-size: 18px;
    font-weight: bold;
    border-radius: 15px;
    white-space: pre-line;
    border: 2px solid #ddd;
}

/* CONTENEDOR PRINCIPAL (NO SIDEBAR) */
section.main div.block-container div.stButton:nth-of-type(1) > button {
    background-color: #28a745 !important;
    color: white !important;
}

section.main div.block-container div.stButton:nth-of-type(2) > button {
    background-color: #17a2b8 !important;
    color: white !important;
}

section.main div.block-container div.stButton:nth-of-type(3) > button {
    background-color: #ffc107 !important;
    color: black !important;
}

section.main div.block-container div.stButton:nth-of-type(4) > button {
    background-color: #dc3545 !important;
    color: white !important;
}

/* HOVER */
div.stButton > button:hover {
    transform: scale(1.05);
    transition: 0.2s;
}

/* SIDEBAR NORMAL */
section[data-testid="stSidebar"] div.stButton > button {
    height: auto !important;
    font-size: 14px !important;
    background-color: #f0f2f6 !important;
    color: black !important;
    border: 1px solid #ccc !important;
}

</style>
""", unsafe_allow_html=True)

if menu == "Inicio":
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.button("+\nNuevo", use_container_width=True)
    with col2:
        st.button("3\nUsuarios", use_container_width=True)
    with col3:
        st.button("2\nPedidos", use_container_width=True)
    with col4:
        st.button("5\nTransferencias", use_container_width=True)


menu = st.session_state.menu

if menu == "Productos":
    st.subheader("Gestión de Productos")

    try:
        st.write(productos)
        response = requests.get(f"{API_URL}/productos/")
        productos = response.json()
    except:
        st.error("No se pudo conectar a la API")
        productos = []