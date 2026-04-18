# Sistema de Inventario - Cafetería Puchis

## Descripción del Proyecto

Sistema de gestión de inventario y ventas para una cafetería. Permite administrar productos, registrar ventas, controlar turnos de caja y gestionar usuarios con diferentes roles.

## Tecnologías Utilizadas

| Tecnología | Uso |
|------------|-----|
| **Python** | Lenguaje principal |
| **Streamlit** | Interfaz de usuario |
| **FastAPI** | API REST |
| **SQLite** | Base de datos |
| **SQLAlchemy** | ORM |
| **Requests** | Comunicación Frontend-Backend |

## Cómo Ejecutar

### 1. Crear y activar entorno virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Instalar dependencias
```bash
pip install streamlit fastapi uvicorn sqlalchemy requests pandas
```

### 3. Ejecutar Backend
```bash
uvicorn main:app --reload
```

### 4. Ejecutar Frontend
```bash
streamlit run app.py
```

### 5. Credenciales
| Usuario | Contraseña | Rol |
|---------|------------|-----|
| admin   | 1234567    | Administrador |

## Módulos del Sistema

### 1. Login
- Inicio de sesión con usuario y contraseña
- Sesión persistente (al recargar la página no pide login otra vez)
- Cierre de sesión (no permite si la caja está abierta)

### 2. Productos (CRUD completo)
| Funcionalidad | Estado |
|---------------|--------|
| Crear producto | ✅ |
| Listar productos | ✅ |
| Editar producto | ✅ |
| Eliminar producto | ✅ |

**Categorías con código automático:**
| Categoría | Rango |
|-----------|-------|
| Cafetería | 100-199 |
| Helados | 200-299 |
| Bebidas | 300-399 |
| Paquetes | 400-499 |
| Otros | 500-599 |

### 3. Ventas
- Solo permite vender si la caja está abierta
- Cuenta de compra temporal
- Descuento automático de stock
- Historial de últimas 10 ventas

### 4. Caja
- Abrir caja (turno mañana/tarde según hora)
- Persistencia del turno por día
- Ver total acumulado
- Cerrar caja con cuadre

### 5. Usuarios (solo Admin)
- Listar usuarios
- Crear usuario
- Editar usuario
- Eliminar usuario (excepto admin)

## Endpoints de la API

### Productos
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/productos/` | Listar productos |
| POST | `/productos/` | Crear producto |
| PUT | `/productos/{id}` | Actualizar producto |
| DELETE | `/productos/{id}` | Eliminar producto |

### Ventas
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/ventas-multiples/` | Registrar venta |
| GET | `/ventas/` | Últimas ventas |

### Caja
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/caja/` | Estado de caja |
| POST | `/abrir-caja/` | Abrir caja |
| POST | `/cuadre-caja/` | Cerrar caja |

### Usuarios
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/usuarios/` | Listar usuarios |
| POST | `/usuarios/` | Crear usuario |
| PUT | `/usuarios/{id}` | Actualizar usuario |
| DELETE | `/usuarios/{id}` | Eliminar usuario |
| GET | `/usuarios/count` | Contar usuarios |
| POST | `/login/` | Autenticar |

## Estructura de Base de Datos

### productos
| Campo | Tipo |
|-------|------|
| id | INTEGER |
| codigo | INTEGER |
| nombre | STRING |
| precio | FLOAT |
| cantidad | INTEGER |
| categoria | STRING |

### usuarios
| Campo | Tipo |
|-------|------|
| id | INTEGER |
| nombre | STRING |
| username | STRING |
| password | STRING |
| rol | STRING |

### ventas
| Campo | Tipo |
|-------|------|
| id | INTEGER |
| total | FLOAT |
| fecha | STRING |
| turno | STRING |

### venta_items
| Campo | Tipo |
|-------|------|
| id | INTEGER |
| venta_id | INTEGER |
| codigo | INTEGER |
| cantidad | INTEGER |
| subtotal | FLOAT |

### caja
| Campo | Tipo |
|-------|------|
| id | INTEGER |
| fecha | STRING |
| total | FLOAT |

## Autor

Ashly Hernandez - Estudiante de Tecnologia en Desarrollo de Software

## Fecha

Abril 2026
