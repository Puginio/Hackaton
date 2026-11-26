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
        timeout=15000,
        retry_options=types.HttpRetryOptions(attempts=1)
    )
)

WORKSPACE_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyfGyx9UYDGVCEEm5DcpjxLPoW6q1PxZG3WD7z-TPsC8B0rVW1wHCrtiftRmWCuUJHVAQ/exec"

MODELOS_GEMINI = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-3.8-flash"]


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
    """Extractor inteligente de respaldo solo si todos los modelos de Gemini fallan."""
    texto_limpio = re.sub(r"\b(jajaja+|mmm+|este+|eh+|y listo)\b", "", texto, flags=re.IGNORECASE)
    texto_limpio = re.sub(r"\s+", " ", texto_limpio).strip()

    # 1. Extraer nombre
    nombre = "Trabajador Local"
    m_nombre = re.search(
        r"(?:mi nombre es|me llamo|soy)\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{2,35}?)(?=\s+(?:soy|y\s+soy|trabajo|tengo|del|de\s+la|en\s+la|en|por|cobro)\b|,|\.|$)",
        texto_limpio,
        re.IGNORECASE
    )
    if m_nombre:
        nombre = m_nombre.group(1).strip().title()

    # 2. Extraer colonia o alcaldía (evitando confundir "en esto" o "en sistemas")
    colonia = "CDMX"
    m_colonia = re.search(
        r"(?:colonia|alcald[ií]a|soy de la|soy del|soy de|calle de|calle)\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,30}?)(?=\s+(?:ciudad|trabajo|puedo|solo|cobro|por|tengo)\b|,|\.|$)",
        texto_limpio,
        re.IGNORECASE
    )
    if m_colonia:
        colonia = m_colonia.group(1).strip().title()

    # 3. Extraer tarifa (prioriza números con $, "pesos", "mxn" o después de "cobro"/"alrededor de")
    tarifa = "$350 MXN por servicio"
    m_tarifa = re.search(
        r"(?:\$\s*(\d[\d,]*)|(\d[\d,]*)\s*(?:pesos|mxn)|(?:cobro|alrededor de|como)\s+\$?\s*(\d[\d,]*))",
        texto_limpio,
        re.IGNORECASE
    )
    if m_tarifa:
        monto = next(g for g in m_tarifa.groups() if g is not None).replace(",", "")
        tarifa = f"${monto} MXN por servicio"

    # 4. Extraer horario
    horario = "Lunes a sábado de 8:00 AM a 6:00 PM"
    m_horario = re.search(
        r"((?:solo\s+)?(?:los\s+)?(?:fines de semana(?:\s+s[aá]bados y domingos)?|domingos|s[aá]bados|lunes a viernes|lunes a s[aá]bado))",
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
        "herrer": "Herrería y Soldadura",
        "sistema": "Soporte Técnico y Sistemas",
        "program": "Desarrollo y Soporte de Sistemas"
    }
    oficio = "Servicios Generales y Oficios Varios"
    for clave, titulo in oficios_map.items():
        if clave in texto_limpio.lower():
            oficio = titulo
            break

    # 6. Detectar años de experiencia si los menciona
    m_exp = re.search(r"(\d{1,2})\s*a[nñ]os", texto_limpio, re.IGNORECASE)
    exp_texto = f" con {m_exp.group(1)} años de experiencia comprobada" if m_exp else " con amplia experiencia en el ramo"

    descripcion_limpia = (
        f"Profesional especializado en {oficio.lower()}{exp_texto}. "
        f"Brinda atención confiable, puntual y de alta calidad en {colonia} y zonas cercanas ({horario.lower()})."
    )

    return {
        "nombre": nombre,
        "oficio": oficio,
        "descripcion_profesional": descripcion_limpia,
        "habilidades": [oficio.split(" ")[0], "Diagnóstico y solución rápida", f"Atención en {colonia}"],
        "colonia": colonia,
        "horario": horario,
        "tarifa_justa_mxn": tarifa,
        "mensaje_whatsapp": f"Hola, soy {nombre}, especialista en {oficio} en {colonia}. Contáctame al {telefono}."
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

    foto_b64 = ""
    foto_mime = ""
    if foto and foto.filename:
        foto_bytes = foto.file.read()
        if foto_bytes:
            foto_b64 = base64.b64encode(foto_bytes).decode("utf-8")
            foto_mime = foto.content_type or "image/jpeg"
            print(f"    Foto recibida ({len(foto_bytes)} bytes, {foto_mime})", flush=True)

    prompt_texto = f"""Eres el editor profesional de perfiles laborales de PuestoYa.
    Un trabajador grabó esta nota de voz informal: "{transcripcion}".
    
    Instrucciones estrictas:
    1. Extrae su nombre real, oficio, colonia/alcaldía/ciudad, horario y tarifa en MXN (ignora números de edad o bromas; toma el precio real que cobra por trabajo).
    2. En 'descripcion_profesional', redacta un párrafo formal, digno y vendedor en tercera persona para su CV (elimina por completo risas como 'jajaja', muletillas como 'mmm', 'y listo', y nunca pegues la transcripción literal).
    3. Genera 3 habilidades técnicas concretas de su oficio.
    4. Redacta un mensaje corto y amable para WhatsApp."""

    print("--> [2/3] Estructurando perfil con Gemini...", flush=True)
    perfil_json = None
    for modelo in MODELOS_GEMINI:
        try:
            print(f"    Consultando {modelo}...", flush=True)
            respuesta = client.models.generate_content(
                model=modelo,
                contents=prompt_texto,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=PerfilLaboral,
                    temperature=0.2
                )
            )
            perfil_json = json.loads(respuesta.text)
            print(f"    ¡Éxito con {modelo}!", flush=True)
            break
        except Exception as err:
            print(f"    {modelo} no disponible ({err})", flush=True)

    if not perfil_json:
        print("    Usando extractor local de respaldo...", flush=True)
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
    for modelo in MODELOS_GEMINI:
        try:
            respuesta = client.models.generate_content(
                model=modelo,
                contents=prompt_busqueda,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(respuesta.text)
        except Exception as err:
            print(f"    {modelo} búsqueda no disponible ({err})", flush=True)

    return {"resultados": []}