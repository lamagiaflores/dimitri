# Dimitri System — Arquitectura Final

**Filosofía:** Cero respuestas negativas.  
Siempre entrega una solución, alternativa o archivo funcional.

## Visión del producto

Una única PWA en Vercel que se adapta al dispositivo y al perfil del usuario:

| Dispositivo | Interfaz | Función principal |
|-------------|----------|-------------------|
| **Celular / Tablet** | Cara animada + voz | Entrada rápida por voz + captura |
| **PC / Laptop** | Consola tipo ChatGPT | Historial, chat, adjuntos, entregables descargables |

| Perfil | Enfoque |
|--------|---------|
| **Personal** | Música, notas, consultas diarias, entretenimiento |
| **Empresarial** | Mostrador, inventario (foto/precio/stock), WhatsApp, reportes |

---

## 1. Estructura definitiva de archivos

```
dimitri-final/
├── README.md
├── docs/
│   ├── ARCHITECTURE.md
│   └── DATA_FLOW.md
│
├── frontend/                          # PWA (Vercel)
│   ├── index.html                     # Entrada única (detecta rol + perfil)
│   ├── manifest.json
│   ├── sw.js
│   ├── icons/
│   │   ├── icon-192.jpg
│   │   └── icon-512.jpg
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── app.js                     # Orquestador
│       ├── auth.js                    # Firebase Auth + selector perfil
│       ├── device.js                  # Detección mobile/desktop
│       ├── voice-face.js              # Cara + STT + TTS + música
│       ├── desktop-console.js         # Consola ChatGPT-like
│       └── firebase-config.js
│
└── backend/                           # FastAPI (Railway / Render / Fly.io)
    ├── main.py
    ├── requirements.txt
    ├── .env.example
    ├── models/
    │   └── schemas.py
    ├── routers/
    │   ├── auth_proxy.py
    │   ├── voice.py
    │   ├── chat.py
    │   ├── files.py
    │   └── sync.py
    └── services/
        ├── llm.py                     # Groq + Function Calling
        ├── adaptive.py                # Motor cero-negativas
        ├── tools.py                   # PDF, Excel, código, etc.
        ├── firebase_admin.py
        └── storage.py                 # Subida/descarga de archivos
```

---

## 2. Flujo técnico: Voz móvil → Archivo en PC

```
[Usuario habla al celular]
        │  "Dimitri, genérame un Excel con las ventas de hoy"
        ▼
[SpeechRecognition → transcript]
        │
        ▼
POST /api/v1/voice/command
{
  uid, transcript, device: "mobile",
  mode: "business" | "personal",
  session_id
}
        │
        ▼
[FastAPI]
  1. Verifica UID (Firebase Admin)
  2. Adaptive Engine (cero negativas)
  3. LLM + Function Calling → elige herramienta
     ej: generate_excel_report
  4. Ejecuta herramienta → crea archivo .xlsx
  5. Sube a Firebase Storage (o genera URL firmada)
  6. Escribe en Firestore:
     /users/{uid}/deliverables/{taskId}
     {
       type: "xlsx",
       title: "Ventas de hoy",
       downloadUrl: "...",
       status: "ready",
       origin: "voice",
       createdAt: ...
     }
  7. Actualiza /users/{uid}/status → "ready"
        │
        ▼
[Firestore Realtime Listener en la PC]
        │
        ▼
[Consola Desktop]
  - Aparece tarjeta en panel de entregables
  - Botón "Descargar Excel"
  - También se registra en el historial de la sesión
```

---

## 3. Consola de escritorio (UX)

```
┌──────────────┬─────────────────────────────┬──────────────────────┐
│  Historial   │     Chat / Resultados       │   Entregables        │
│  (sidebar)   │                             │   (panel derecho)    │
│              │  [mensajes del sistema]     │                      │
│  • Sesión 1  │  [respuestas del asistente] │  📄 reporte.pdf      │
│  • Sesión 2  │                             │  📊 ventas.xlsx      │
│  + Nueva     │                             │  💻 query.sql        │
│              │  ┌─────────────────────┐    │                      │
│              │  │ Escribe o adjunta…  │ 📎 │                      │
│              │  └─────────────────────┘    │                      │
└──────────────┴─────────────────────────────┴──────────────────────┘
```

- **Barra lateral:** historial de conversaciones / sesiones.
- **Centro:** chat + zona de resultados.
- **Inferior:** input de texto + botón adjuntar archivos/imágenes.
- **Derecha (o pestaña):** lista de entregables listos para descargar (PDF, DOCX, XLSX, SQL, código…).

---

## 4. Stack 100 % gratuito (recomendado)

| Capa              | Tecnología                          |
|-------------------|-------------------------------------|
| Frontend PWA      | Vercel                              |
| Backend           | Railway / Render / Fly.io (FastAPI) |
| Auth + DB         | Firebase (Auth + Firestore)         |
| Storage archivos  | Firebase Storage (free tier)        |
| LLM               | Groq (Llama 3.3 / 3.1)              |
| Generación docs   | ReportLab (PDF), openpyxl (Excel)   |

---

## Cómo empezar

1. Crea proyecto Firebase → Auth (Email/Password) + Firestore + Storage.
2. Copia credenciales en `frontend/js/firebase-config.js` y `backend/.env`.
3. Obtén API Key de Groq → `GROQ_API_KEY`.
4. Backend: `cd backend && pip install -r requirements.txt && uvicorn main:app --reload`
5. Frontend: despliega carpeta `frontend/` en Vercel.

Cuando el backend y Firebase estén activos, los entregables dejan de ser simulados y pasan a ser archivos reales descargables.