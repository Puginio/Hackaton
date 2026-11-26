# PuestoYa

**Equipo:** Los Nueces  
**Integrantes:** Aguirre García Víctor Jesús, Vargas Morales Marco Alexis  
**Campus:** Campus UVM Coyoacán  
**Enlace en vivo:** [PENDIENTE: Agregar enlace de descarga del APK o video demostración]  
**Repositorio:** (https://github.com/Puginio/Hackaton)
- **Problema a resolver:** Combatir la exclusión laboral en las ciudades causada por las barreras digitales (dificultad para elaborar un CV o usar plataformas complejas) y las barreras de movilidad (imposibilidad de realizar traslados largos) para ofrecer oficios de manera digna y sin intermediarios.
- **Usuarios objetivo:** Adultos mayores, personas con discapacidad, migrantes, cuidadores y trabajadores esenciales de oficios locales, así como vecinos y comercios de su misma colonia que requieren servicios cercanos.
- **Alineación con los ODS 10 y 11:** Se atiende el **ODS 10 (Reducción de las desigualdades)** mediante una aplicación móvil gratuita y accesible por voz que permite a poblaciones vulnerables monetizar sus habilidades en igualdad de condiciones; y se impulsa el **ODS 11 (Ciudades y comunidades sostenibles)** al fomentar la contratación hiperlocal dentro del mismo barrio, fortaleciendo el tejido comunitario y reduciendo traslados urbanos contaminantes.
- **Integración de la IA (Gemini) y Google Workspace:** Se utiliza `gemini-2.5-flash` desde un backend en Python para convertir notas de voz y fotografías de trabajos manuales en perfiles profesionales verificados en formato JSON (con CV en PDF, tarifas justas sugeridas y tarjetas para WhatsApp), almacenando y consultando el directorio comunitario mediante **Google Workspace** (Google Sheets y Google Drive) para potenciar un buscador semántico hiperlocal que conecta en lenguaje natural las necesidades de los vecinos con los trabajadores más cercanos.

---

## 1. Resumen ejecutivo

**PuestoYa** es una aplicación móvil hiperlocal para Android que conecta a trabajadores en situación de vulnerabilidad —adultos mayores, personas con discapacidad, migrantes y cuidadores— con vecinos que requieren servicios de oficios en su misma colonia. A diferencia de las bolsas de trabajo tradicionales que exigen currículums escritos y traslados largos, PuestoYa utiliza inteligencia artificial multimodal (`gemini-2.5-flash`) en Python junto con **Google Workspace** para transformar notas de voz y fotografías de trabajos manuales en fichas profesionales verificadas, currículums en PDF y anuncios listos para WhatsApp. Con ello, elimina barreras digitales, sugiere tarifas justas y fomenta el empleo digno de proximidad.

---

## 2. Boceto y concepto

### El problema
En las zonas urbanas, grupos vulnerables como adultos mayores, personas con discapacidad, personas migrantes y cuidadores enfrentan una doble exclusión laboral:
1. **Barreras digitales:** Desconocen cómo redactar un currículum vitae (CV) o navegar en portales de empleo complejos.
2. **Barreras de movilidad:** No cuentan con el tiempo, los recursos o las condiciones físicas para realizar traslados diarios de varias horas hacia otras zonas de la ciudad.

### Propuesta de solución
PuestoYa reemplaza los formularios extensos por una aplicación móvil accesible impulsada por voz e imágenes. El trabajador habla sobre su experiencia o toma fotos de sus labores (plomería, cocina, cuidados, reparaciones) desde su teléfono Android y la aplicación estructura automáticamente su perfil laboral, calcula tarifas justas, lo registra en el directorio de Google Workspace y facilita el contacto directo con vecinos de su propio barrio sin intermediarios.

### Alineación con los Objetivos de Desarrollo Sostenible (ODS)
- **ODS 10 (Reducción de las desigualdades):** Brinda herramientas tecnológicas accesibles y gratuitas para que poblaciones históricamente excluidas del mercado formal puedan dignificar y monetizar sus oficios de manera autónoma.
- **ODS 11 (Ciudades y comunidades sostenibles) e Iniciativa Actúa Ahora de la ONU:** Impulsa la contratación y el consumo local dentro de un radio cercano al hogar del trabajador. Esto reduce la necesidad de largos desplazamientos urbanos, disminuye la huella ambiental asociada al transporte y fortalece el tejido social de la colonia.

### Boceto visual de la aplicación
> [PENDIENTE: Insertar capturas de pantalla o enlaces a los wireframes/mockups de la interfaz de registro y búsqueda en Android Studio]

---

## 3. Documentación funcional

- **Creación de perfil por voz e imagen:** Permite al trabajador grabar una nota de voz describiendo sus habilidades y tomar o subir fotografías de sus trabajos. El sistema genera automáticamente su perfil dentro de la aplicación y un currículum descargable en formato PDF.
- **Directorio comunitario en Google Workspace:** Registra y organiza los perfiles verificados de los trabajadores en Google Sheets / Google Drive, permitiendo consultar disponibilidad, oficios y colonias de cobertura en tiempo real.
- **Sugerencia de tarifas justas:** Analiza el oficio y las actividades descritas por el trabajador para proponer un rango de precios adecuado y competitivo.
- **Emparejamiento hiperlocal inteligente:** Conecta las solicitudes de los vecinos con trabajadores compatibles dentro de un radio geográfico cercano, priorizando la proximidad y las condiciones de horario o movilidad del trabajador.
- **Canal de comunicación directo:** Genera un mensaje de contacto prellenado para que el vecino y el trabajador acuerden el servicio directamente por WhatsApp, sin intermediarios ni comisiones.
- **Generador de anuncios para difusión:** Crea un tarjetón o anuncio promocional del perfil del trabajador, optimizado para compartirse con un clic a través de WhatsApp o dentro de la misma aplicación.
- **Lectura en voz alta y dictado:** Permite navegar, dictar información y escuchar tanto el perfil generado como las ofertas disponibles mediante síntesis y reconocimiento de voz nativos de Android.

---

## 4. Documentación técnica

### Arquitectura general
PuestoYa sigue una arquitectura cliente-servidor desacoplada e integrada con Google Workspace:
1. **Capa de presentación (Frontend Móvil):** Aplicación nativa en Android Studio con interfaz de alto contraste que captura entradas de voz (mediante el micrófono del dispositivo) y archivos de imagen (cámara o galería), y presenta los perfiles y resultados de búsqueda.
2. **Capa de servicios e IA (Backend / API):** Servidor desarrollado en Python (desde VS Code) que recibe los datos multimodales desde la app Android, gestiona las peticiones a la API de Google Gemini y devuelve respuestas estructuradas en formato JSON.
3. **Capa de almacenamiento y gestión (Google Workspace):** Integración con Google Sheets y Google Drive para almacenar el directorio de trabajadores y respaldar la información generada.

### Stack tecnológico
- **Aplicación Móvil (Frontend):** Android Studio (Kotlin / Java con XML) bajo estándares de accesibilidad WCAG de alto contraste.
- **Backend / Conexión API:** Python (FastAPI / Flask) desarrollado en VS Code con el SDK oficial `google-genai`.
- **Inteligencia Artificial (Obligatorio):** Google Gemini API (modelo `gemini-2.5-flash`).
- **Ecosistema Colaborativo y Datos (Obligatorio):** Google Workspace (Google Sheets API y Google Drive / Docs).
- **Accesibilidad nativa:** Android Speech API (`SpeechRecognizer` / `RecognizerIntent` para entrada por voz y `TextToSpeech` para lectura en voz alta).
- **Control de versiones:** GitHub (`https://github.com/Puginio/Hackaton`).

### Integración de Google Gemini (`gemini-2.5-flash`) y Google Workspace
La inteligencia artificial junto con Google Workspace actúan como el núcleo operativo en tres puntos del flujo de la aplicación:

1. **Módulo de Registro Multimodal (`Voz + Imagen -> Perfil Laboral + Google Sheets`):**
  - *Ubicación:* Pantalla de alta del trabajador en Android (*"Cuéntanos qué sabes hacer"*).
  - *Funcionamiento:* La app envía al backend en Python el audio transcrito (o texto coloquial) junto con las fotografías de los trabajos realizados. El modelo `gemini-2.5-flash` valida visualmente el oficio, redacta una descripción profesional digna, extrae habilidades clave, calcula un rango de tarifas justas y devuelve toda la información en un esquema **JSON estructurado** que se guarda en **Google Sheets** y se envía a Android para renderizar el perfil, exportar a PDF y compartir por WhatsApp.
2. **Motor de Emparejamiento Hiperlocal:**
  - *Ubicación:* Buscador comunitario para vecinos y comercios locales.
  - *Funcionamiento:* Procesa consultas en lenguaje natural (por ejemplo: *"Necesito alguien de confianza que arregle una fuga en la colonia Centro"*). El servidor en Python consulta los registros activos en **Google Sheets** y utiliza Gemini para cruzar semánticamente la solicitud con los perfiles registrados, priorizando la cercanía geográfica y las restricciones de movilidad u horario del trabajador. Además, redacta un mensaje inicial personalizado para facilitar el contacto directo por WhatsApp.
3. **Soporte al Diseño y Documentación en Google Workspace:**
  - *Ubicación:* Ciclo de desarrollo del proyecto.
  - *Funcionamiento:* Utilizado para estructurar los bocetos conceptuales iniciales, validar la arquitectura cliente-servidor y redactar la documentación técnica y de usuario final respaldada en Google Workspace.

---

## 5. Manual de usuario

### Cómo instalar y acceder a la aplicación
1. Descarga el archivo de instalación (`PuestoYa.apk`) en tu teléfono celular Android desde: `[PENDIENTE: Insertar enlace de descarga de la app]`.
2. Abre el archivo descargado y autoriza la instalación en tu dispositivo.
3. Al abrir **PuestoYa** por primera vez, acepta los permisos de **micrófono** (para hablar en lugar de escribir) y **cámara o galería** (para mostrar fotos de tus trabajos).

---

### Guía para trabajadores: Crea tu perfil y consigue clientes

1. **Inicia tu registro:** En la pantalla principal, toca el botón grande que dice **"Ofrecer mis servicios"** (o **"Crear mi perfil"**).
2. **Cuéntanos qué sabes hacer:**
  - Toca el botón del **micrófono** y habla con naturalidad. Por ejemplo: *"Hola, soy Don José, sé arreglar fugas de agua, cambiar llaves y hacer reparaciones sencillas en casa. Puedo trabajar por las mañanas en mi colonia"*.
  - Si lo prefieres, también puedes escribirlo en el cuadro de texto.
3. **Muestra tu trabajo (opcional):** Toca **"Subir foto"** para tomar una foto con tu cámara o agregar imágenes de algún trabajo que hayas hecho antes (una reparación, un platillo cocinado, etc.).
4. **Revisa tu ficha profesional:** Espera unos segundos mientras la aplicación organiza tus datos y los guarda en el directorio. Verás en pantalla tu nuevo perfil profesional, una sugerencia de cuánto cobrar por tu trabajo y un botón de **bocina** por si deseas que el teléfono te lea en voz alta lo que escribió.
5. **Comparte tu trabajo:**
  - Toca **"Descargar CV en PDF"** si deseas guardar tu currículum en tu teléfono.
  - Toca **"Compartir en WhatsApp"** para enviar tu tarjeta de presentación a tus conocidos o grupos de vecinos.

---

### Guía para vecinos: Encuentra ayuda en tu colonia

1. **Abre el buscador:** En la pantalla principal, selecciona la opción **"Busco un servicio"**.
2. **Escribe o dicta lo que necesitas:** Explica tu problema con tus propias palabras y menciona tu colonia. Ejemplo: *"Busco alguien cerca de la colonia Coyoacán que me ayude a cuidar a un adulto mayor por las tardes"*.
3. **Elige a un trabajador:** La aplicación consultará el directorio comunitario y te mostrará a las personas registradas más cercanas a tu domicilio que saben hacer ese trabajo, junto con una tarifa estimada.
4. **Contacta directamente:** Toca el botón **"Contactar"** en el perfil que elijas. La aplicación preparará un mensaje listo para enviarse directamente por WhatsApp al trabajador y que puedan ponerse de acuerdo sin intermediarios.

---

## 6. Accesibilidad e impacto

### Diseño inclusivo y accesibilidad
PuestoYa fue diseñada bajo estándares internacionales de accesibilidad (**WCAG**) pensando en usuarios con poca experiencia digital o con alguna discapacidad:
- **Interacción sin teclado:** Gracias a la integración nativa de reconocimiento y síntesis de voz en Android (`SpeechRecognizer` y `TextToSpeech`), personas con baja alfabetización digital o dificultades motrices pueden crear su perfil hablando y escuchar toda la información de la pantalla en voz alta.
- **Alto contraste y tipografía legible:** La interfaz utiliza colores con alto contraste visual y botones amplios diseñados
