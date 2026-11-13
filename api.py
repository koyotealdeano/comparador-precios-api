from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Permitir conexiones desde Flutter Web y móvil
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PRODUCTOS_DB = [
    {"id": "patatas", "nombre": "Patatas (Malla 3kg)"},
    {"id": "langostinos", "nombre": "Langostinos Cocidos (1kg)"},
    {"id": "naranjas", "nombre": "Naranjas de Mesa (2kg)"},
    {"id": "pina", "nombre": "Piña Natural (Unidad)"},
]

PRECIOS_DB = {
    "patatas": [
        {"supermercado": "Alcampo", "precio": 3.45},
        {"supermercado": "Mercadona", "precio": 3.60},
        {"supermercado": "Carrefour", "precio": 3.89},
    ],
    "langostinos": [
        {"supermercado": "Mercadona", "precio": 8.95},
        {"supermercado": "Carrefour", "precio": 9.20},
        {"supermercado": "Alcampo", "precio": 9.50},
    ],
    "naranjas": [
        {"supermercado": "Carrefour", "precio": 2.75},
        {"supermercado": "Alcampo", "precio": 2.80},
        {"supermercado": "Mercadona", "precio": 2.95},
    ],
    "pina": [
        {"supermercado": "Alcampo", "precio": 2.15},
        {"supermercado": "Mercadona", "precio": 2.30},
        {"supermercado": "Carrefour", "precio": 2.49},
    ],
}

@app.get("/")
def inicio():
    return {"message": "¡API del Comparador de Precios funcionando correctamente en Render!"}

@app.get("/api/productos")
def obtener_productos():
    return PRODUCTOS_DB

@app.get("/api/comparar/{producto_id}")
def comparar_producto(producto_id: str):
    return PRECIOS_DB.get(producto_id.lower(), [])