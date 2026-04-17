from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from datetime import datetime
from typing import List, Literal
from pydantic import BaseModel

# ======================
# BASE DE DATOS
# ======================
DATABASE_URL = "sqlite:///./inventario.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ======================
# MODELOS DB
# ======================
class ProductoDB(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(Integer, unique=True)
    nombre = Column(String)
    precio = Column(Float)
    cantidad = Column(Integer)
    categoria = Column(String)


class VentaDB(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(Integer)
    cantidad = Column(Integer)
    total = Column(Float)
    fecha = Column(String)
    turno = Column(String)


class CajaDB(Base):
    __tablename__ = "caja"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(String, unique=True)
    total = Column(Float)


Base.metadata.create_all(bind=engine)


class ProductoCreate(BaseModel):
    codigo: int
    nombre: str
    precio: float
    cantidad: int
    categoria: str

class ProductoUpdate(BaseModel):
    nombre: str
    precio: float
    cantidad: int

class ProductoResponse(ProductoCreate):
    id: int

    class Config:
        orm_mode = True


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
# PRODUCTOS
# ======================
@app.post("/productos/", response_model=ProductoResponse)
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    
    nuevo = ProductoDB(**producto.dict())

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


@app.get("/productos/", response_model=List[ProductoResponse])
def obtener_productos(db: Session = Depends(get_db)):
    return db.query(ProductoDB).all()


@app.delete("/productos/{producto_id}")
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    
    producto = db.query(ProductoDB).filter(ProductoDB.id == producto_id).first()

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    db.delete(producto)
    db.commit()

    return {"mensaje": "Producto eliminado"}

@app.put("/productos/{producto_id}", response_model=ProductoResponse)
def actualizar_producto(producto_id: int, data: ProductoUpdate, db: Session = Depends(get_db)):
    
    producto = db.query(ProductoDB).filter(ProductoDB.id == producto_id).first()

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    producto.nombre = data.nombre
    producto.precio = data.precio
    producto.cantidad = data.cantidad

    db.commit()
    db.refresh(producto)

    return producto


# ======================
# VENTAS
# ======================
@app.post("/ventas/")
def registrar_venta(
    codigo: int,
    cantidad: int,
    turno: Literal["mañana", "tarde"],
    db: Session = Depends(get_db)
):
    
    producto = db.query(ProductoDB).filter(ProductoDB.codigo == codigo).first()

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no existe")

    if producto.cantidad < cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente")

    total = producto.precio * cantidad

    producto.cantidad -= cantidad

    fecha_hoy = datetime.now().strftime("%Y-%m-%d")

    venta = VentaDB(
        codigo=codigo,
        cantidad=cantidad,
        total=total,
        fecha=fecha_hoy,
        turno=turno
    )

    db.add(venta)
    db.commit()

    return {"mensaje": "Venta realizada", "total": total}


@app.get("/ventas/")
def obtener_ventas(db: Session = Depends(get_db)):
    return db.query(VentaDB).all()


# ======================
# CAJA
# ======================
@app.get("/caja/")
def ver_caja(turno: Literal["mañana", "tarde"], db: Session = Depends(get_db)):

    fecha_hoy = datetime.now().strftime("%Y-%m-%d")

    ventas = db.query(VentaDB).filter(VentaDB.fecha == fecha_hoy).all()

    if turno == "mañana":
        total = sum(v.total for v in ventas if v.turno == "mañana")
    else:
        total = sum(v.total for v in ventas)

    return {"turno": turno, "total": total}


@app.post("/cierre-caja/")
def cerrar_caja(db: Session = Depends(get_db)):

    fecha_hoy = datetime.now().strftime("%Y-%m-%d")

    caja_existente = db.query(CajaDB).filter(CajaDB.fecha == fecha_hoy).first()
    if caja_existente:
        raise HTTPException(status_code=400, detail="La caja ya fue cerrada")

    ventas = db.query(VentaDB).filter(VentaDB.fecha == fecha_hoy).all()
    total = sum(v.total for v in ventas)

    nueva_caja = CajaDB(fecha=fecha_hoy, total=total)

    db.add(nueva_caja)
    db.commit()

    return {"mensaje": "Caja cerrada", "total": total}