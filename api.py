
import os
import json
import re
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from comparar_super import (
    comparar_supermercados as comparar_calabazas,
    url_carrefour as c_carrefour,
    url_dia as c_dia,
    url_alcampo as c_alcampo,
    url_alimerka as c_alimerka,
    url_aldi as c_aldi,
    url_mercadona as c_mercadona,
    url_familia as c_familia,
    url_masymas as c_masymas
)

from comparar_patatas import (
    comparar_supermercados as comparar_patatas,
    url_carrefour as p_carrefour,
    url_dia as p_dia,
    url_alcampo as p_alcampo,
    url_alimerka as p_alimerka,
    url_aldi as p_aldi,
    url_mercadona as p_mercadona,
    url_familia as p_familia,
    url_masymas as p_masymas
)

from comparar_carne import (
    comparar_supermercados as comparar_carne,
    url_carrefour as ca_carrefour,
    url_dia as ca_dia,
    url_alcampo as ca_alcampo,
    url_alimerka as ca_alimerka,
    url_aldi as ca_aldi,
    url_mercadona as ca_mercadona,
    url_familia as ca_familia,
    url_masymas as ca_masymas
)

from comparar_pina import (
    comparar_supermercados as comparar_pina,
    url_carrefour as pi_carrefour,
    url_dia as pi_dia,
    url_alcampo as pi_alcampo,
    url_alimerka as pi_alimerka,
    url_aldi as pi_aldi,
    url_mercadona as pi_mercadona,
    url_familia as pi_familia,
    url_masymas as pi_masymas
)

from comparar_langostinos import (
    comparar_supermercados as comparar_langostinos,
    url_carrefour as l_carrefour,
    url_dia as l_dia,
    url_alcampo as l_alcampo,
    url_alimerka as l_alimerka,
    url_aldi as l_aldi,
    url_mercadona as l_mercadona,
    url_familia as l_familia,
    url_masymas as l_masymas
)

from comparar_naranjas import (
    comparar_supermercados as comparar_naranjas,
    url_carrefour as n_carrefour,
    url_dia as n_dia,
    url_alcampo as n_alcampo,
    url_alimerka as n_alimerka,
    url_aldi as n_aldi,
    url_mercadona as n_mercadona,
    url_familia as n_familia,
    url_masymas as n_masymas
)


# ==========================================
# CONFIGURACIÓN DE FASTAPI
# ==========================================

app = FastAPI(
    title="API Comparador de Supermercados",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# RUTAS DE COMPROBACIÓN
# ==========================================

@app.get("/")
def inicio():
    return {
        "status": "ok",
        "mensaje": "API Comparador de Supermercados funcionando"
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "servidor": "activo"
    }


# ==========================================
# CATÁLOGO DE PRODUCTOS
# ==========================================

@app.get("/api/productos")
def listar_productos():
    return [
        {
            "id": "calabazas",
            "nombre": "Calabazas",
            "icono": "🎃"
        },
        {
            "id": "patatas",
            "nombre": "Patatas (Bolsa 5kg)",
            "icono": "🥔"
        },
        {
            "id": "carne",
            "nombre": "Carne",
            "icono": "🥩"
        },
        {
            "id": "langostinos",
            "nombre": "Langostinos Cocidos",
            "icono": "🦐"
        },
        {
            "id": "naranjas",
            "nombre": "Naranjas",
            "icono": "🍊"
        },
        {
            "id": "pina",
            "nombre": "Piña",
            "icono": "🍍"
        }
    ]


# ==========================================
# PERSISTENCIA DE DATOS
# ==========================================

ARCHIVO_DATOS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "datos_guardados.json"
)


def guardar_en_disco(producto, datos):

    registro = {}

    if os.path.exists(ARCHIVO_DATOS):
        try:
            with open(
                ARCHIVO_DATOS,
                "r",
                encoding="utf-8"
            ) as f:
                registro = json.load(f)

        except Exception as e:
            print(f"Error leyendo archivo: {e}")
            registro = {}

    ahora = datetime.now().strftime(
        "%d/%m/%Y a las %H:%M"
    )

    registro[producto] = {
        "datos": datos,
        "ultima_actualizacion": ahora
    }

    try:
        with open(
            ARCHIVO_DATOS,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                registro,
                f,
                ensure_ascii=False,
                indent=4
            )

        print(
            f"[Guardado] {producto} guardado correctamente"
        )

    except Exception as e:
        print(f"[Error guardando datos] {e}")


def leer_de_disco(producto):

    if os.path.exists(ARCHIVO_DATOS):
        try:
            with open(
                ARCHIVO_DATOS,
                "r",
                encoding="utf-8"
            ) as f:

                registro = json.load(f)

                return registro.get(producto)

        except Exception as e:
            print(f"[Error leyendo datos] {e}")

    return None


# ==========================================
# ORDENAR PRECIOS
# ==========================================

def limpiar_precio(item):

    val = item.get("actual", "N/D")

    if not val or val in ("N/D", "No disponible"):
        return 999999.0

    try:
        limpio = (
            str(val)
            .replace("€", "")
            .replace(" ", "")
            .replace(",", ".")
        )

        match = re.search(
            r"\d+\.\d+|\d+",
            limpio
        )

        if match:
            return float(match.group())

    except Exception:
        pass

    return 999999.0


# ==========================================
# GESTIÓN DE CONSULTAS
# ==========================================

def manejar_peticion(
    producto,
    funcion_comparacion,
    *args,
    actualizar=False
):

    if not actualizar:

        guardado = leer_de_disco(producto)

        if guardado and guardado.get("datos"):

            datos_ordenados = guardado["datos"]

            datos_ordenados.sort(
                key=limpiar_precio
            )

            return {
                "status": "ok",
                "datos": datos_ordenados,
                "ultima_actualizacion":
                    guardado.get(
                        "ultima_actualizacion",
                        "Desconocida"
                    )
            }

        return {
            "status": "ok",
            "datos": [],
            "ultima_actualizacion":
                "Nunca (Pulsa actualizar para buscar)"
        }

    try:

        resultados = funcion_comparacion(*args)

        if resultados is None:
            resultados = []

        resultados.sort(
            key=limpiar_precio
        )

        guardar_en_disco(
            producto,
            resultados
        )

        guardado = leer_de_disco(producto)

        if guardado:
            datos_ordenados = guardado["datos"]
            ultima = guardado["ultima_actualizacion"]
        else:
            datos_ordenados = resultados
            ultima = "Recién actualizado"

        datos_ordenados.sort(
            key=limpiar_precio
        )

        return {
            "status": "ok",
            "datos": datos_ordenados,
            "ultima_actualizacion": ultima
        }

    except Exception as e:

        print(
            f"[ERROR COMPARANDO {producto}] {e}"
        )

        raise


# ==========================================
# RUTAS DE COMPARACIÓN
# ==========================================

@app.get("/api/calabazas")
def obtener_calabazas(actualizar: bool = False):

    return manejar_peticion(
        "calabazas",
        comparar_calabazas,
        c_carrefour,
        c_dia,
        c_alcampo,
        c_alimerka,
        c_aldi,
        c_mercadona,
        c_familia,
        c_masymas,
        actualizar=actualizar
    )


@app.get("/api/patatas")
def obtener_patatas(actualizar: bool = False):

    return manejar_peticion(
        "patatas",
        comparar_patatas,
        p_carrefour,
        p_dia,
        p_alcampo,
        p_alimerka,
        p_aldi,
        p_mercadona,
        p_familia,
        p_masymas,
        actualizar=actualizar
    )


@app.get("/api/carne")
def obtener_carne(actualizar: bool = False):

    return manejar_peticion(
        "carne",
        comparar_carne,
        ca_carrefour,
        ca_dia,
        ca_alcampo,
        ca_alimerka,
        ca_aldi,
        ca_mercadona,
        ca_familia,
        ca_masymas,
        actualizar=actualizar
    )


@app.get("/api/pina")
def obtener_pina(actualizar: bool = False):

    return manejar_peticion(
        "pina",
        comparar_pina,
        pi_carrefour,
        pi_dia,
        pi_alcampo,
        pi_alimerka,
        pi_aldi,
        pi_mercadona,
        pi_familia,
        pi_masymas,
        actualizar=actualizar
    )


@app.get("/api/langostinos")
def obtener_langostinos(actualizar: bool = False):

    return manejar_peticion(
        "langostinos",
        comparar_langostinos,
        l_carrefour,
        l_dia,
        l_alcampo,
        l_alimerka,
        l_aldi,
        l_mercadona,
        l_familia,
        l_masymas,
        actualizar=actualizar
    )


@app.get("/api/naranjas")
def obtener_naranjas(actualizar: bool = False):

    return manejar_peticion(
        "naranjas",
        comparar_naranjas,
        n_carrefour,
        n_dia,
        n_alcampo,
        n_alimerka,
        n_aldi,
        n_mercadona,
        n_familia,
        n_masymas,
        actualizar=actualizar
    )


# ==========================================
# ARRANQUE LOCAL
# ==========================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )
