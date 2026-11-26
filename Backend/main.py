import os
import json
import requests
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI(title="Motor PuestoYa - Gemini + Workspace")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY"),
    http_options=types.HttpOptions(
        timeout=45000,
        retry_options=types.HttpRetryOptions(attempts=1)
    )
)

WORKSPACE_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyhZ4mrBEml3dm7JHuFw_KMSQYvjgkFqyGKK-Wsi9G4GIpx7zPlWkCJGpdsnNRZFnZomQ/exec"


class PerfilLaboral(BaseModel):
    nombre: str
    oficio: str
    descripcion_profesional: str
    habilidades: list[str]
    colonia: str
    horario: str
    tarifa_justa_mxn: str
    mensaje_whatsapp: str


@app.post("/procesar-trabajador")
def procesar_trabajador(
    audio: UploadFile = File(...),
    foto: UploadFile = File(None),
    telefono: str = Form(...)
):
    print("--> [1/3] Leyendo archivos...", flush=True)
    contenido_prompt = [
        """Eres el motor de inclusión laboral de PuestoYa. 
        Escucha el audio del trabajador (adulto mayor, migrante o persona con discapacidad) 
        y analiza la foto de su trabajo si existe. 
        Extrae sus datos (si no dice su nombre, pon 'Trabajador Local'; si no dice colonia, pon 'Coyoacán'), 
        redacta una descripción profesional digna para su CV, 
        sugiere una tarifa justa en pesos mexicanos (ej. '$200 - $350 MXN por servicio') 
        y crea un anuncio corto para WhatsApp."""
    ]

    audio_bytes = audio.file.read()
    mime_audio = audio.content_type or "audio/mp4"
    if "video" in mime_audio or "octet-stream" in mime_audio or audio.filename.endswith((".ogg", ".opus")):
        mime_audio = "audio/ogg" if audio.filename.endswith((".ogg", ".opus")) else "audio/mp4"

    contenido_prompt.append(
        types.Part.from_bytes(data=audio_bytes, mime_type=mime_audio)
    )

    if foto:
        foto_bytes = foto.file.read()
        contenido_prompt.append(
            types.Part.from_bytes(data=foto_bytes, mime_type=foto.content_type or "image/jpeg")
        )

    print("--> [2/3] Consultando Gemini...", flush=True)
    try:
        respuesta = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=contenido_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=PerfilLaboral,
                temperature=0.3
            )
        )
    except Exception as err:
        print(f"ERROR Gemini: {err}", flush=True)
        return {"error": "No se pudo obtener respuesta de Gemini", "detalle": str(err)}

    perfil_json = json.loads(respuesta.text)
    perfil_json["telefono"] = telefono

    print("--> [3/3] Guardando en Google Workspace...", flush=True)
    try:
        res_workspace = requests.post(WORKSPACE_WEBHOOK_URL, json=perfil_json, timeout=25)
        data_ws = res_workspace.json()
        perfil_json["url_cv_pdf"] = data_ws.get("url_pdf", "")
    except Exception as e:
        print(f"ERROR Workspace: {e}", flush=True)
        perfil_json["warning_workspace"] = str(e)

    print("--> ¡Proceso completado!", flush=True)
    return perfil_json


@app.post("/buscar-vecino")
def buscar_vecino(solicitud: str = Form(...)):
    print("--> [1/2] Consultando directorio en Google Sheets...", flush=True)
    try:
        directorio = requests.get(WORKSPACE_WEBHOOK_URL, timeout=15).json()
    except Exception as e:
        return {"error": "No se pudo leer el directorio de Google Sheets", "detalle": str(e)}

    prompt_busqueda = f"""
    Un vecino necesita: "{solicitud}".
    Directorio de trabajadores en Google Sheets (fila 0 son encabezados): {json.dumps(directorio)}.
    Selecciona los trabajadores más compatibles priorizando la misma colonia o cercanía y el oficio.
    Devuelve estrictamente este formato JSON:
    {{
      "resultados": [
        {{
          "nombre": "...",
          "oficio": "...",
          "colonia": "...",
          "tarifa": "...",
          "telefono": "...",
          "mensaje_contacto": "Hola, vi tu perfil en PuestoYa y necesito ayuda con..."
        }}
      ]
    }}
    """

    print("--> [2/2] Buscando coincidencias con Gemini...", flush=True)
    try:
        respuesta = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt_busqueda,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
    except Exception as err:
        print(f"ERROR Gemini búsqueda: {err}", flush=True)
        return {"error": "No se pudo completar la búsqueda con Gemini", "detalle": str(err)}

    return json.loads(respuesta.text)