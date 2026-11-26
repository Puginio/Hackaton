import os
import re
import json
import base64
import tempfile
import requests
import speech_recognition as sr
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI(title="Motor PuestoYa - Audio/Texto + Gemini + CV Visual")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY"),
    http_options=types.HttpOptions(
        timeout=30000,
        retry_options=types.HttpRetryOptions(attempts=1)
    )
)

WORKSPACE_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyfGyx9UYDGVCEEm5DcpjxLPoW6q1PxZG3WD7z-TPsC8B0rVW1wHCrtiftRmWCuUJHVAQ/exec"


class PerfilLaboral(BaseModel):
    nombre: str
    oficio: str
    descripcion_profesional: str
    habilidades: list[str]
    colonia: str
    horario: str
    tarifa_justa_mxn: str
    mensaje_whatsapp: str


def extraer_perfil_desde_texto(texto: str, telefono: str) -> dict:
    """Extractor inteligente de respaldo si Gemini tiene saturación 503."""
    texto_limpio = texto.strip()

    # 1. Extraer nombre
    nombre = "Trabajador Local"
    m_nombre = re.search(
        r"(?:mi nombre es|me llamo|soy)\s+(.+?)(?=\s+(?:soy|y\s+soy|y\s+estoy|y\s+vivo|y\s+trabajo|estoy|vivo|trabajo|del|de\s+la|en\s+la|en\s+el|en|por|cobro)\b|,|\.|$)",
        texto_limpio,
        re.IGNORECASE
    )
    if m_nombre:
        nombre = m_nombre.group(1).strip().title()

    # 2. Extraer colonia o alcaldía
    colonia = "Coyoacán"
    m_colonia = re.search(
        r"(?:alcald[ií]a|colonia|del|de la|en la|en el|en)\s+(.+?)(?=\s+(?:puedo|y\s+puedo|y\s+cobro|y\s+trabajo|trabajo|solo|por|cobro)\b|,|\.|$)",
        texto_limpio,
        re.IGNORECASE
    )
    if m_colonia:
        colonia = m_colonia.group(1).strip().title()

    # 3. Extraer tarifa
    tarifa = "$250 - $400 MXN por servicio"
    m_tarifa = re.search(r"\$?\s*(\d[\d,\.]*)\s*(?:pesos|mxn)?", texto_limpio, re.IGNORECASE)
    if m_tarifa:
        monto = m_tarifa.group(1).replace(",", "")
        tarifa = f"${monto} MXN por servicio"

    # 4. Extraer horario
    horario = "Lunes a sábado de 8:00 AM a 6:00 PM"
    m_horario = re.search(
        r"((?:solo\s+)?(?:los\s+)?(?:domingos|s[aá]bados|fines de semana|lunes a viernes|lunes a s[aá]bado|todos los d[ií]as)[^,\.]*)",
        texto_limpio,
        re.IGNORECASE
    )
    if m_horario:
        horario = m_horario.group(1).strip().capitalize()

    # 5. Detectar oficio
    oficios_map = {
        "plomer": "Plomería y Reparaciones Hidráulicas",
        "electric": "Electricista Residencial",
        "carpinter": "Carpintería y Muebles",
        "albañil": "Albañilería y Remodelación",
        "pintor": "Pintura y Acabados",
        "jardiner": "Jardinería y Mantenimiento",
        "limpieza": "Limpieza y Cuidado del Hogar",
        "cocin": "Cocina y Preparación de Alimentos",
        "costur": "Costura y Arreglos de Ropa",
        "mecánic": "Mecánica Automotriz",
        "herrer": "Herrería y Soldadura"
    }
    oficio = "Servicios Generales y Oficios Varios"
    for clave, titulo in oficios_map.items():
        if clave in texto_limpio.lower():
            oficio = titulo
            break

    return {
        "nombre": nombre,
        "oficio": oficio,
        "descripcion_profesional": f"Especialista en {oficio.lower()} con atención en {colonia}. {texto_limpio.capitalize()}.",
        "habilidades": [oficio.split(" ")[0], "Atención puntual", f"Cobertura en {colonia}"],
        "colonia": colonia,
        "horario": horario,
        "tarifa_justa_mxn": tarifa,
        "mensaje_whatsapp": f"Hola, soy {nombre}, ofrezco servicios de {oficio} en {colonia}. Contáctame al {telefono}."
    }


@app.post("/procesar-trabajador")
def procesar_trabajador(
    audio: UploadFile = File(None),
    transcripcion_manual: str = Form(None),
    foto: UploadFile = File(None),
    telefono: str = Form(...)
):
    print("--> [1/3] Procesando entrada (Audio o Texto)...", flush=True)
    transcripcion = (transcripcion_manual or "").strip()
    if transcripcion.lower() == "string":
        transcripcion = ""

    # Prioriza transcribir el audio .wav si se sube archivo
    if audio and audio.filename:
        audio_bytes = audio.file.read()
        if audio_bytes:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name

            try:
                recognizer = sr.Recognizer()
                with sr.AudioFile(tmp_path) as source:
                    audio_data = recognizer.record(source)
                    transcripcion = recognizer.recognize_google(audio_data, language="es-MX")
            except Exception as e:
                print(f"    Error transcribiendo audio (.wav requerido): {e}", flush=True)
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

    print(f"    Texto listo para Gemini: '{transcripcion}'", flush=True)

    # Preparar imagen en Base64 si el usuario subió foto
    foto_b64 = ""
    foto_mime = ""
    if foto and foto.filename:
        foto_bytes = foto.file.read()
        if foto_bytes:
            foto_b64 = base64.b64encode(foto_bytes).decode("utf-8")
            foto_mime = foto.content_type or "image/jpeg"
            print(f"    Foto recibida ({len(foto_bytes)} bytes, {foto_mime})", flush=True)

    prompt_texto = f"""Eres el motor de inclusión laboral de PuestoYa.
    Analiza esta presentación de un trabajador: "{transcripcion}".
    Extrae sus datos reales (nombre, oficio, colonia o alcaldía, horario y tarifa en MXN).
    Redacta una descripción profesional digna y atractiva para su CV, 3 habilidades clave y un anuncio corto para WhatsApp."""

    print("--> [2/3] Estructurando perfil con Gemini...", flush=True)
    try:
        respuesta = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt_texto,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=PerfilLaboral,
                temperature=0.3,
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            )
        )
        perfil_json = json.loads(respuesta.text)
        print("    ¡Éxito con Gemini!", flush=True)
    except Exception as err:
        print(f"    Aviso Gemini ({err}), usando extractor local...", flush=True)
        perfil_json = extraer_perfil_desde_texto(transcripcion, telefono)

    perfil_json["telefono"] = telefono
    if foto_b64:
        perfil_json["foto_base64"] = foto_b64
        perfil_json["foto_mime"] = foto_mime

    print("--> [3/3] Generando CV visual PDF y guardando en Sheets...", flush=True)
    try:
        res_workspace = requests.post(WORKSPACE_WEBHOOK_URL, json=perfil_json, timeout=30)
        data_ws = res_workspace.json()
        perfil_json["url_cv_pdf"] = data_ws.get("url_pdf", "")
    except Exception as e:
        print(f"ERROR Workspace: {e}", flush=True)
        perfil_json["warning_workspace"] = str(e)

    perfil_json.pop("foto_base64", None)
    perfil_json.pop("foto_mime", None)

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
                response_mime_type="application/json",
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            )
        )
        return json.loads(respuesta.text)
    except Exception as err:
        print(f"ERROR Gemini búsqueda: {err}", flush=True)
        return {"resultados": []}