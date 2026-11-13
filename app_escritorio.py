import os
import threading
import uvicorn
import webview
from api import app

def iniciar_servidor():
    # Arranca FastAPI en segundo plano para que la API y los scrapers sigan funcionando por debajo
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")

if __name__ == "__main__":
    # 1. Arrancamos el servidor backend en un hilo secundario
    hilo_servidor = threading.Thread(target=iniciar_servidor, daemon=True)
    hilo_servidor.start()

    # 2. Obtenemos la ruta absoluta de tu archivo index.html en la carpeta actual
    ruta_html = os.path.abspath("index.html")

    # 3. Creamos la ventana de escritorio cargando el HTML directamente del disco
    ventana = webview.create_window(
        title="Comparador de Precios - UGT Supercor",
        url=f"file:///{ruta_html}",
        width=1100, 
        height=800,
        resizable=True,
        min_size=(800, 600)
    )

    # 4. Lanzamos la aplicación de escritorio
    webview.start()