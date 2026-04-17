from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from datetime import datetime
from typing import List, Literal
from pydantic import BaseModel
from typing import List

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
    total = Column(Float)
    fecha = Column(String)
    turno = Column(String)

class VentaItemDB(Base):
    __tablename__ = "venta_items"

    id = Column(Integer, primary_key=True, index=True)
    venta_id = Column(Integer)
    codigo = Column(Integer)
    cantidad = Column(Integer)
    subtotal = Column(Float)


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

class VentaItem(BaseModel):
    codigo: int
    cantidad: int

class VentaMultiple(BaseModel):
    items: List[VentaItem]
    turno: Literal["mañana", "tarde"]


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

    hora_actual = datetime.now().strftime("%H:%M:%S")

    venta = VentaDB(
        codigo=codigo,
        cantidad=cantidad,
        total=total,
        fecha=hora_actual,
        turno=turno
    )

    db.add(venta)
    db.commit()

    return {"mensaje": "Venta realizada", "total": total}

@app.post("/ventas-multiples/")
def registrar_venta_multiple(data: VentaMultiple, db: Session = Depends(get_db)):

    hora_actual = datetime.now().strftime("%H:%M:%S")
    total_general = 0

    nueva_venta = VentaDB(
        total=0,
        fecha=hora_actual,
        turno=data.turno
    )

    db.add(nueva_venta)
    db.commit()
    db.refresh(nueva_venta)

    for item in data.items:

        producto = db.query(ProductoDB).filter(ProductoDB.codigo == item.codigo).first()

        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto {item.codigo} no existe")

        if producto.cantidad < item.cantidad:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente para {producto.nombre}")

        subtotal = producto.precio * item.cantidad
        total_general += subtotal

        producto.cantidad -= item.cantidad

        venta_item = VentaItemDB(
            venta_id=nueva_venta.id,
            codigo=item.codigo,
            cantidad=item.cantidad,
            subtotal=subtotal
        )

        db.add(venta_item)

    nueva_venta.total = total_general

    db.commit()

    return {"mensaje": "Venta completa", "total": total_general}


@app.get("/ventas/")
def obtener_ventas(db: Session = Depends(get_db)):

    ventas = db.query(VentaDB).all()
    resultado = []

    for venta in ventas[-10:][::-1]:

        items = db.query(VentaItemDB).filter(VentaItemDB.venta_id == venta.id).all()

        resultado.append({
            "id": venta.id,
            "hora": venta.fecha,
            "turno": venta.turno,
            "total": venta.total,
            "items": [
                {
                    "codigo": i.codigo,
                    "cantidad": i.cantidad,
                    "subtotal": i.subtotal
                }
                for i in items
            ]
        })

    return resultado

# ======================
# CAJA
# ======================
@app.get("/caja/")
def ver_caja(turno: Literal["mañana", "tarde"], db: Session = Depends(get_db)):

    hora_actual = datetime.now().strftime("%H:%M:%S")

    ventas = db.query(VentaDB).filter(VentaDB.fecha == hora_actual).all()

    if turno == "mañana":
        total = sum(v.total for v in ventas if v.turno == "mañana")
    else:
        total = sum(v.total for v in ventas)

    return {"turno": turno, "total": total}


@app.post("/cierre-caja/")
def cerrar_caja(db: Session = Depends(get_db)):

    hora_actual = datetime.now().strftime("%H:%M:%S")

    caja_existente = db.query(CajaDB).filter(CajaDB.fecha == hora_actual).first()
    if caja_existente:
        raise HTTPException(status_code=400, detail="La caja ya fue cerrada")

    ventas = db.query(VentaDB).filter(VentaDB.fecha == hora_actual).all()
    total = sum(v.total for v in ventas)

    nueva_caja = CajaDB(fecha=hora_actual, total=total)

    db.add(nueva_caja)
    db.commit()

    return {"mensaje": "Caja cerrada", "total": total}
