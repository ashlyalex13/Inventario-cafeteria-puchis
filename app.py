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

col1, col2, col3, col4 = st.columns(4)

def card(titulo, contenido, color):
    st.markdown(f"""
    <div style="
        background-color:{color};
        padding:20px;
        border-radius:15px;
        text-align:center;
        color:white;
        font-weight:bold;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
    ">
        <div style="font-size:28px; margin-bottom:10px;">
            {contenido}
        </div>
        <div style="font-size:16px;">
            {titulo}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col1:
    if st.button(""):
        st.session_state.menu = "Ventas"
    card("Nueva Venta", "➕", "#28a745")

with col2:
    if st.button(" "):
        st.session_state.menu = "Productos"
    card("Usuarios", "3", "#17a2b8")  # 👈 luego lo conectamos a BD

with col3:
    if st.button("  "):
        st.info("Pedidos próximamente")
    card("Pedidos", "5", "#ffc107")

with col4:
    if st.button("   "):
        st.info("Transferencias próximamente")
    card("Transferencias", "2", "#dc3545")