from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# ======================
# BASE DE DATOS
# ======================
DATABASE_URL = "sqlite:///./inventario.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ======================
# MODELO
# ======================
class ProductoDB(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(Integer, unique=True)  # 👈 TU CONTROLAS ESTE
    nombre = Column(String)
    precio = Column(Float)
    cantidad = Column(Integer)

class VentaDB(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(Integer)
    cantidad = Column(Integer)
    total = Column(Float)

Base.metadata.create_all(bind=engine)

# ======================
# APP
# ======================
app = FastAPI(title="Cafetería Puchis ☕")

# ======================
# DB SESSION
# ======================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ======================
# RUTAS
# ======================
@app.post("/productos/")
def crear_producto(
    codigo: int,
    nombre: str,
    precio: float,
    cantidad: int,
    db: Session = Depends(get_db)
):
    nuevo = ProductoDB(
        codigo=codigo,
        nombre=nombre,
        precio=precio,
        cantidad=cantidad
    )

    db.add(nuevo)
    db.commit()
    return {"mensaje": "Producto creado"}

@app.get("/productos/")
def obtener_productos(db: Session = Depends(get_db)):
    return db.query(ProductoDB).all()

@app.post("/ventas/")
def registrar_venta(codigo: int, cantidad: int, db: Session = Depends(get_db)):
    
    producto = db.query(ProductoDB).filter(ProductoDB.codigo == codigo).first()

    if not producto:
        return {"error": "Producto no existe"}

    if producto.cantidad < cantidad:
        return {"error": "Stock insuficiente"}

    total = producto.precio * cantidad

    producto.cantidad -= cantidad

    venta = VentaDB(codigo=codigo, cantidad=cantidad, total=total)
    db.add(venta)

    db.commit()

    return {"mensaje": "Venta realizada", "total": total}

@app.get("/ventas/")
def obtener_ventas(db: Session = Depends(get_db)):
    return db.query(VentaDB).all()