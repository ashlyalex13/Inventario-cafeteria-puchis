import streamlit as st
import requests

st.title("Cafetería Puchis ☕")
st.write("Sistema de inventario")

# BOTÓN INVENTARIO
if st.button("Ver inventario"):
    res = requests.get("http://127.0.0.1:8000/productos/")
    st.write(res.json())