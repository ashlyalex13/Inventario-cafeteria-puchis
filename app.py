import streamlit as st
import requests
import pandas as pd
from datetime import datetime


API_URL = "http://localhost:8000"

st.set_page_config(page_title="Cafetería Puchis ☕", layout="wide")
st.title("☕ Sistema de Caja - Cafetería Puchis")

# ======================
# FUNCIONES API
# ======================


# ======================
# SIDEBAR 
# ======================

st.sidebar.title("☕ Cafetería Puchis")

menu = st.sidebar.radio(
    "Dashboard",
    ["Inicio", "Productos", "Ventas", "Gastos", "Pérdidas", "Cierre de caja"]
)

# ======================
# HEADER SUPERIOR
# ======================
col1, col2 = st.columns([1, 3])

with col1:
    st.write(datetime.now().strftime("%H:%M:%S"))

with col2:
    st.markdown("### Usuario: Admin")

st.divider()


if menu == "Inicio":
    st.title("☕ Cafetería Puchis")
    st.subheader("Sistema de Caja e Inventario")

elif menu == "Productos":
    st.title("📦 Gestión de Productos")

elif menu == "Ventas":
    st.title("💰 Ventas")

elif menu == "Gastos":
    st.title("💸 Gastos")

elif menu == "Pérdidas":
    st.title("📉 Pérdidas")

elif menu == "Cierre de caja":
    st.title("🧾 Cierre de Caja")
