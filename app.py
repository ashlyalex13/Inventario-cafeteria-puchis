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

st.sidebar.title("☕ Cafetería Puchis")

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

# ======================
# HEADER SUPERIOR
# ======================
col1, col2 = st.columns([1, 6])

with col1:
    st.markdown(f"⏰ {datetime.now().strftime('%H:%M:%S')}")

with col2:
    st.markdown(
        "<div style='text-align: right;'>"
        "<button style='padding:8px 15px; border-radius:8px; border:none; background-color:#eee;'>👤 Admin</button>"
        "</div>",
        unsafe_allow_html=True
    )

# TITULO
st.title("☕ Cafetería Puchis - Sistema de Inventario")

st.divider()
