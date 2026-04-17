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

if menu == "Inicio":
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

.fila-producto {
    display: grid;
    grid-template-columns: 1fr 2fr 1fr 1fr;
    padding: 10px;
    border-bottom: 1px solid #eee;
    align-items: center;
}

.fila-producto:hover {
    background-color: #f9f9f9;
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


if menu == "Productos":

    st.markdown("""
    <h2 style='margin-bottom:10px;'>
    Gestión de Inventario
    </h2>
    """, unsafe_allow_html=True)


    # ======================
    # OBTENER PRODUCTOS
    # ======================
    try:
        response = requests.get(f"{API_URL}/productos/")
        if response.status_code == 200:
            productos = response.json()

            from collections import defaultdict

            categorias = defaultdict(list)

            for p in productos:
                categorias[p["categoria"]].append(p)

        else:
            productos = []
    except Exception as e:
        st.error(f"Error API: {e}")
        productos = []

    # ======================
    # RANGOS
    # ======================
    rangos_categoria = {
        "Cafeteria": (100, 199),
        "Helados": (200, 299),
        "Bebidas": (300, 399),
        "Paquetes": (400, 499),
        "Otros": (500, 599),
    }

    # ======================
    # FORMULARIO
    # ======================
    with st.expander("Añadir nuevo producto +"):
        with st.form("form_producto"):

            categoria = st.selectbox(
                "Categoría",
                list(rangos_categoria.keys())
            )

            nombre = st.text_input("Nombre")
            precio = st.number_input("Precio", min_value=0.0)
            cantidad = st.number_input("Cantidad", min_value=0)

            rango_min, rango_max = rangos_categoria[categoria]

            codigos_usados = [
                p["codigo"] for p in productos
                if rango_min <= p["codigo"] <= rango_max
            ]

            if codigos_usados:
                nuevo_codigo = max(codigos_usados) + 1
            else:
                nuevo_codigo = rango_min

            st.text_input("Código generado", value=nuevo_codigo, disabled=True)

            guardar = st.form_submit_button("Guardar")

            if guardar:
                try:
                    res = requests.post(
                        f"{API_URL}/productos/",
                        json={
                            "codigo": nuevo_codigo,
                            "nombre": nombre,
                            "precio": precio,
                            "cantidad": cantidad,
                            "categoria": categoria
                        }
                    )

                    if res.status_code == 200:
                        st.success("Producto creado")
                        st.rerun()
                    else:
                        st.error(f"Error: {res.text}")

                except Exception as e:
                    st.error(f"Error real: {e}")

    st.divider()

    # ======================
    # LISTA
    # ======================
    st.subheader("Categoría")


    if not productos:
        st.info("No hay productos")
    else:
        for categoria, items in categorias.items():

            with st.expander(f"{categoria}", expanded=False):

                # ENCABEZADO TIPO TABLA
                st.markdown("""
                <div style="
                    display: grid;
                    grid-template-columns: 1fr 2fr 1fr 1fr 60px;
                    font-weight: bold;
                    padding: 10px;
                    border-bottom: 2px solid #ddd;
                ">
                    <div>Código</div>
                    <div>Nombre</div>
                    <div>Precio</div>
                    <div>Stock</div>
                    <div></div>
                </div>
                """, unsafe_allow_html=True)

                if "editando" not in st.session_state:
                    st.session_state.editando = None

                for p in items:

                    col1, col2 = st.columns([10,1])

                    with col1:
                        st.markdown(f"""
                        <div class="fila-producto">
                            <div>{p['codigo']}</div>
                            <div>{p['nombre']}</div>
                            <div>${p['precio']}</div>
                            <div>{p['cantidad']}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    # INICIALIZAR estado
                    if "confirm_delete" not in st.session_state:
                        st.session_state.confirm_delete = None


                    with col2:
                        with st.popover("⚙"):
                            
                            if st.button("Editar", key=f"edit_{p['id']}"):
                                st.session_state.editando = p
                        

                            # BOTÓN ELIMINAR (primer paso)
                            if st.button("Eliminar", key=f"del_{p['id']}"):
                                st.session_state.confirm_delete = p["id"]


                    if st.session_state.editando and st.session_state.editando["id"] == p["id"]:

                                  with st.form(f"form_edit_{p['id']}"):

                                    nombre = st.text_input("Nombre", value=p["nombre"])
                                    precio = st.number_input("Precio", value=float(p["precio"]))
                                    cantidad = st.number_input("Cantidad", value=int(p["cantidad"]))

                                    guardar = st.form_submit_button("Guardar cambios")

                                    if guardar:
                                        try:
                                            res = requests.put(
                                                f"{API_URL}/productos/{p['id']}",
                                                json={
                                                    "codigo": p["codigo"],
                                                    "nombre": nombre,
                                                    "precio": precio,
                                                    "cantidad": cantidad,
                                                    "categoria": p["categoria"]
                                                }
                                            )

                                            if res.status_code == 200:
                                                st.success("Producto actualizado")
                                                st.session_state.editando = None
                                                st.rerun()
                                            else:
                                                st.error(res.text)

                                        except Exception as e:
                                            st.error(f"Error: {e}")
                    # CONFIRMACIÓN
                    if st.session_state.confirm_delete == p["id"]:
                                    st.warning("¿Seguro que quieres eliminar este producto?")

                                    col_yes, col_no = st.columns(2)

                                    with col_yes:
                                        if st.button("Sí, eliminar", key=f"yes_{p['id']}"):
                                            try:
                                                res = requests.delete(f"{API_URL}/productos/{p['id']}")
                                                if res.status_code == 200:
                                                    st.success("Producto eliminado")
                                                    st.session_state.confirm_delete = None
                                                    st.rerun()
                                                else:
                                                    st.error(f"Error: {res.text}")
                                            except Exception as e:
                                                st.error(f"Error conectando con la API: {e}")

                                    with col_no:
                                        if st.button("Cancelar", key=f"no_{p['id']}"):
                                            st.session_state.confirm_delete = None
