# PuestoYa

**Equipo:** Los Nueces  
**Campus:** Campus UVM Coyoacán  
**Enlace en vivo:** [PENDIENTE: Agregar URL de despliegue en Vercel / Netlify]  
**Repositorio:** (https://github.com/Puginio/Hackaton)

---

## 1. Resumen ejecutivo

**PuestoYa** es una plataforma web hiperlocal que conecta a trabajadores en situación de vulnerabilidad —adultos mayores, personas con discapacidad, migrantes y cuidadores— con vecinos que requieren servicios de oficios en su misma colonia. A diferencia de las bolsas de trabajo tradicionales que exigen currículums escritos y traslados largos, PuestoYa utiliza inteligencia artificial multimodal (`gemini-2.5-flash`) para transformar notas de voz y fotografías de trabajos manuales en fichas profesionales verificadas, currículums en PDF y anuncios listos para WhatsApp. Con ello, elimina barreras digitales, sugiere tarifas justas y fomenta el empleo digno de proximidad.

---

## 2. Boceto y concepto

### El problema
En las zonas urbanas, grupos vulnerables como adultos mayores, personas con discapacidad, personas migrantes y cuidadores enfrentan una doble exclusión laboral:
1. **Barreras digitales:** Desconocen cómo redactar un currículum vitae (CV) o navegar en portales de empleo complejos.
2. **Barreras de movilidad:** No cuentan con el tiempo, los recursos o las condiciones físicas para realizar traslados diarios de varias horas hacia otras zonas de la ciudad.

### Propuesta de solución
PuestoYa reemplaza los formularios extensos por una interfaz accesible impulsada por voz e imágenes. El trabajador habla sobre su experiencia o sube fotos de sus labores (plomería, cocina, cuidados, reparaciones) y la aplicación estructura automáticamente su perfil laboral, calcula tarifas justas y facilita el contacto directo con vecinos de su propio barrio sin intermediarios.

### Alineación con los Objetivos de Desarrollo Sostenible (ODS)
* **ODS 10 (Reducción de las desigualdades):** Brinda herramientas tecnológicas accesibles y gratuitas para que poblaciones históricamente excluidas del mercado formal puedan dignificar y monetizar sus oficios de manera autónoma.
* **ODS 11 (Ciudades y comunidades sostenibles) e Iniciativa Actúa Ahora de la ONU:** Impulsa la contratación y el consumo local dentro de un radio cercano al hogar del trabajador. Esto reduce la necesidad de largos desplazamientos urbanos, disminuye la huella ambiental asociada al transporte y fortalece el tejido social de la colonia.

### Boceto visual de la plataforma
> [PENDIENTE: Insertar capturas de pantalla o enlaces a los wireframes/mockups de la interfaz de registro y búsqueda]

---

## 3. Documentación funcional

* **Creación de perfil por voz e imagen:** Permite al trabajador grabar una nota de voz describiendo sus habilidades y subir fotografías de sus trabajos. El sistema genera automáticamente su perfil dentro de la aplicación y un currículum descargable en formato PDF.
* **Sugerencia de tarifas justas:** Analiza el oficio y las actividades descritas por el trabajador para proponer un rango de precios adecuado y competitivo.
* **Emparejamiento hiperlocal inteligente:** Conecta las solicitudes de los vecinos con trabajadores compatibles dentro de un radio geográfico cercano, priorizando la proximidad y las condiciones de horario o movilidad del trabajador.
* **Canal de comunicación directo:** Genera un mensaje de contacto prellenado para que el vecino y el trabajador acuerden el servicio directamente, sin intermediarios ni comisiones.
* **Generador de anuncios para difusión:** Crea un tarjetón o anuncio promocional del perfil del trabajador, optimizado para compartirse con un clic a través de WhatsApp o dentro de la misma plataforma.
* **Lectura en voz alta y dictado:** Permite navegar, dictar información y escuchar tanto el perfil generado como las ofertas disponibles mediante síntesis y reconocimiento de voz en el navegador.

---

## 4. Documentación técnica

### Arquitectura general
PuestoYa sigue una arquitectura web **Mobile-First** desacoplada:
1. **Capa de presentación (Frontend):** Interfaz responsiva de alto contraste que captura entradas de audio (mediante el navegador) y archivos de imagen, y presenta los perfiles y resultados de búsqueda.
2. **Capa de servicios e IA (Backend / API):** Funciones serverless (o integración directa mediante SDK en entorno de desarrollo) que reciben los datos multimodales, gestionan las peticiones a la API de Google Gemini y devuelven respuestas estructuradas en formato JSON para alimentar la interfaz y el generador de PDF.

### Stack tecnológico
* **Frontend:** React + Vite + Tailwind CSS (con cumplimiento de estándares de accesibilidad WCAG de alto contraste).
* **Backend / Conexión API:** Node.js / Serverless Functions con el SDK oficial `@google/genai`.
* **Inteligencia Artificial:** Google Gemini API (modelo `gemini-2.5-flash`).
* **Accesibilidad nativa:** Web Speech API (`SpeechRecognition` para entrada por voz y `speechSynthesis` para lectura en voz alta).
* **Control de versiones y despliegue:** GitHub y Vercel / Netlify.

### Integración de Google Gemini (`gemini-2.5-flash`)
La inteligencia artificial actúa como el núcleo operativo en tres puntos del flujo de la aplicación:

1. **Módulo de Registro Multimodal (`Voz + Imagen -> Perfil Laboral`):**
   * *Ubicación:* Pantalla de alta del trabajador (*"Cuéntanos qué sabes hacer"*).
   * *Funcionamiento:* Recibe el audio transcrito (o texto coloquial) junto con las fotografías de los trabajos realizados. El modelo `gemini-2.5-flash` valida visualmente el oficio, redacta una descripción profesional digna, extrae habilidades clave, calcula un rango de tarifas justas y devuelve toda la información en un esquema **JSON estructurado** listo para renderizar en la app, exportar a PDF y convertir en un anuncio de WhatsApp.
2. **Motor de Emparejamiento Hiperlocal:**
   * *Ubicación:* Buscador comunitario para vecinos y comercios locales.
   * *Funcionamiento:* Procesa consultas en lenguaje natural (por ejemplo: *"Necesito alguien de confianza que arregle una fuga en la colonia Centro"*). Gemini realiza una búsqueda semántica cruzando la solicitud con los perfiles registrados, priorizando la cercanía geográfica y las restricciones de movilidad u horario del trabajador. Además, redacta un mensaje inicial personalizado para facilitar el contacto.
3. **Soporte al Diseño y Documentación:**
   * *Ubicación:* Ciclo de desarrollo del proyecto.
   * *Funcionamiento:* Utilizado para estructurar los bocetos conceptuales iniciales, validar la arquitectura del código y redactar la documentación técnica y de usuario.

---

## 5. Manual de usuario

### Cómo acceder a la aplicación
1. Abre el navegador de internet de tu teléfono celular o computadora (se recomienda Google Chrome o Microsoft Edge para usar las funciones de voz).
2. Ingresa a la dirección web de **PuestoYa**: `[PENDIENTE: Insertar enlace público de la app]`.
3. No necesitas descargar ni instalar ningún programa adicional; la página se adaptará automáticamente al tamaño de tu pantalla.

---

### Guía para trabajadores: Crea tu perfil y consigue clientes

1. **Inicia tu registro:** En la pantalla principal, presiona el botón grande que dice **"Ofrecer mis servicios"** (o **"Crear mi perfil"**).
2. **Cuéntanos qué sabes hacer:**
   * Presiona el botón del **micrófono** y habla con naturalidad. Por ejemplo: *"Hola, soy Don José, sé arreglar fugas de agua, cambiar llaves y hacer reparaciones sencillas en casa. Puedo trabajar por las mañanas en mi colonia"*.
   * Si lo prefieres, también puedes escribirlo en el cuadro de texto.
3. **Muestra tu trabajo (opcional):** Presiona **"Subir foto"** para agregar imágenes de algún trabajo que hayas hecho antes (una reparación, un platillo cocinado, etc.).
4. **Revisa tu ficha profesional:** Espera unos segundos mientras la aplicación organiza tus datos. Verás en pantalla tu nuevo perfil profesional, una sugerencia de cuánto cobrar por tu trabajo y un botón de **bocina** por si deseas que la aplicación te lea en voz alta lo que escribió.
5. **Comparte tu trabajo:**
   * Presiona **"Descargar CV en PDF"** si deseas guardar tu currículum en tu teléfono.
   * Presiona **"Compartir en WhatsApp"** para enviar tu tarjeta de presentación a tus conocidos o grupos de vecinos.

---

### Guía para vecinos: Encuentra ayuda en tu colonia

1. **Abre el buscador:** En la pantalla principal, selecciona la opción **"Busco un servicio"**.
2. **Escribe o dicta lo que necesitas:** Explica tu problema con tus propias palabras y menciona tu colonia. Ejemplo: *"Busco alguien cerca de la colonia Coyoacán que me ayude a cuidar a un adulto mayor por las tardes"*.
3. **Elige a un trabajador:** La aplicación te mostrará a las personas registradas más cercanas a tu domicilio que saben hacer ese trabajo, junto con una tarifa estimada.
4. **Contacta directamente:** Presiona el botón **"Contactar"** en el perfil que elijas. La aplicación preparará un mensaje listo para enviarse directamente al trabajador y que puedan ponerse de acuerdo sin intermediarios.

---

## 6. Accesibilidad e impacto

### Diseño inclusivo y accesibilidad
PuestoYa fue diseñada bajo estándares internacionales de accesibilidad web (**WCAG**) pensando en usuarios con poca experiencia digital o con alguna discapacidad:
* **Interacción sin teclado:** Gracias a la integración de *Web Speech API*, personas con baja alfabetización digital o dificultades motrices pueden crear su perfil hablando y escuchar toda la información de la pantalla en voz alta.
* **Alto contraste y tipografía legible:** La interfaz utiliza colores con alto contraste visual y botones amplios diseñados para dispositivos móviles (*Mobile-First*), facilitando su uso a adultos mayores o personas con debilidad visual.
* **Lenguaje natural:** Elimina los tecnicismos administrativos; tanto el trabajador como el vecino interactúan usando su forma cotidiana de hablar.

### Impacto social y comunitario esperado
* **Autonomía económica (ODS 10):** Permite que trabajadores vulnerables generen ingresos propios de manera digna, contando con un respaldo profesional (perfil verificado y CV en PDF) y referencias claras de cobro justo.
* **Economía circular de barrio (ODS 11):** Al priorizar la cercanía geográfica dentro de la misma colonia, el dinero circula dentro de la comunidad local, se reducen los tiempos y costos de transporte público o privado, y se fomenta la confianza y solidaridad entre vecinos.
