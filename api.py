from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Comparador de Precios API", version="1.0")

# Configurar CORS para permitir peticiones desde tu app de Flutter u otros clientes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "¡API del Comparador de Precios funcionando correctamente en Render!"}

# Endpoint para devolver el catálogo de productos que consume Flutter
@app.get("/api/productos")
def obtener_productos():
    return [
        {"id": "patatas", "nombre": "Patatas (Bolsa 5kg)", "icono": "🥔"},
        {"id": "langostinos", "nombre": "Langostinos Cocidos", "icono": "🦐"},
        {"id": "naranjas", "nombre": "Naranjas", "icono": "🍊"},
        {"id": "pina", "nombre": "Piña", "icono": "🍍"}
    ]

# Endpoint para consultar la comparativa de precios de un producto
@app.get("/comparar/{producto_id}")
def comparar_precios(producto_id: str):
    return [
        {
            "super": "Alcampo",
            "nombre": f"Producto {producto_id}",
            "kg": "2.30 €/kg",
            "actual": "4.60 €"
        },
        {
            "super": "Mercadona",
            "nombre": f"Producto {producto_id}",
            "kg": "2.45 €/kg",
            "actual": "4.90 €"
        },
        {
            "super": "Carrefour",
            "nombre": f"Producto {producto_id}",
            "kg": "2.60 €/kg",
            "actual": "5.20 €"
        }
    ]