from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from datetime import datetime
from typing import List
from pydantic import BaseModel

# ======================
# BASE DE DATOS
# ======================
DATABASE_URL = "sqlite:///./inventario.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# CONTROL DE CAJA
caja_abierta = False
turno_actual = None

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


class UsuarioDB(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    username = Column(String, unique=True)
    password = Column(String)
    rol = Column(String)


Base.metadata.create_all(bind=engine)

# ======================
# CREAR ADMIN
# ======================
def crear_admin():
    db = SessionLocal()

    existe = db.query(UsuarioDB).filter(UsuarioDB.username == "admin").first()

    if not existe:
        admin = UsuarioDB(
            nombre="Ashly",
            username="admin",
            password="1234",
            rol="admin"
        )
        db.add(admin)
        db.commit()

    db.close()

# ======================
# SCHEMAS
# ======================
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


class LoginData(BaseModel):
    username: str
    password: str


class UsuarioCreate(BaseModel):
    nombre: str
    username: str
    password: str | None = None
    rol: str | None = None

# ======================
# APP
# ======================
app = FastAPI(title="Cafetería Puchis")

@app.on_event("startup")
def startup_event():
    crear_admin()

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
# CAJA
# ======================
def iniciar_caja(db: Session):
    global caja_abierta, turno_actual

    if caja_abierta:
        return turno_actual

    fecha_hoy = datetime.now().strftime("%Y-%m-%d")

    cajas_hoy = db.query(CajaDB).filter(
        CajaDB.fecha.like(f"{fecha_hoy}%")
    ).count()

    turno_actual = "mañana" if cajas_hoy == 0 else "tarde"
    caja_abierta = True

    return turno_actual

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
@app.post("/ventas-multiples/")
def registrar_venta_multiple(data: VentaMultiple, db: Session = Depends(get_db)):
    global caja_abierta, turno_actual

    if not caja_abierta:
        iniciar_caja(db)

    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    total_general = 0

    nueva_venta = VentaDB(
        total=0,
        fecha=fecha_hoy,
        turno=turno_actual
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

        db.add(VentaItemDB(
            venta_id=nueva_venta.id,
            codigo=item.codigo,
            cantidad=item.cantidad,
            subtotal=subtotal
        ))

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
            "fecha": venta.fecha,
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
def ver_caja(db: Session = Depends(get_db)):
    global caja_abierta, turno_actual

    if not caja_abierta:
        return {"turno": None, "total": 0}

    fecha_hoy = datetime.now().strftime("%Y-%m-%d")

    ventas = db.query(VentaDB).filter(
        VentaDB.fecha == fecha_hoy,
        VentaDB.turno == turno_actual
    ).all()

    total = sum(v.total for v in ventas)

    return {"turno": turno_actual, "total": total}


@app.post("/cuadre-caja/")
def cuadre_caja(db: Session = Depends(get_db)):
    global caja_abierta, turno_actual

    if not caja_abierta:
        raise HTTPException(status_code=400, detail="No hay caja abierta")

    fecha_hoy = datetime.now().strftime("%Y-%m-%d")

    ventas = db.query(VentaDB).filter(
        VentaDB.fecha == fecha_hoy,
        VentaDB.turno == turno_actual
    ).all()

    total = sum(v.total for v in ventas)

    db.add(CajaDB(
        fecha=f"{fecha_hoy}-{turno_actual}",
        total=total
    ))

    caja_abierta = False
    turno_actual = None

    db.commit()

    return {"mensaje": "Cuadre realizado", "total": total}

# ======================
# LOGIN
# ======================
@app.post("/login/")
def login(data: LoginData, db: Session = Depends(get_db)):
    user = db.query(UsuarioDB).filter(
        UsuarioDB.username == data.username,
        UsuarioDB.password == data.password
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    return {"username": user.username, "rol": user.rol}

# ======================
# USUARIOS
# ======================
@app.post("/usuarios/")
def crear_usuario(data: UsuarioCreate, db: Session = Depends(get_db)):

    existe = db.query(UsuarioDB).filter(UsuarioDB.username == data.username).first()

    if existe:
        raise HTTPException(status_code=400, detail="Usuario ya existe")

    if not data.password:
        raise HTTPException(status_code=400, detail="La contraseña es obligatoria")

    nuevo = UsuarioDB(
        nombre=data.nombre,
        username=data.username,
        password=data.password,
        rol="empleado"
    )

    db.add(nuevo)
    db.commit()

    return {"mensaje": "Usuario creado"}


@app.get("/usuarios/")
def obtener_usuarios(db: Session = Depends(get_db)):
    return db.query(UsuarioDB).all()


@app.put("/usuarios/{usuario_id}")
def actualizar_usuario(usuario_id: int, data: UsuarioCreate, db: Session = Depends(get_db)):
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.nombre = data.nombre
    usuario.username = data.username

    if data.password:
        usuario.password = data.password

    db.commit()

    return {"mensaje": "Usuario actualizado"}


@app.delete("/usuarios/{usuario_id}")
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if usuario.username == "admin":
        raise HTTPException(status_code=400, detail="No puedes eliminar el admin")

    db.delete(usuario)
    db.commit()

    return {"mensaje": "Usuario eliminado"}


@app.get("/usuarios/count")
def contar_usuarios(db: Session = Depends(get_db)):
    total = db.query(UsuarioDB).count()
    return {"total": total}