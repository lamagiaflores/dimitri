# Flujo de datos detallado — Dimitri System

## 1. Login + selector de perfil

```
Usuario abre PWA
      │
      ▼
[Pantalla Login]
  - Email + Password
  - Selector: Personal | Empresarial
      │
      ▼
Firebase Auth → UID
      │
      ▼
Firestore /users/{uid}
  {
    email,
    mode: "personal" | "business",
    createdAt,
    lastDevice: "mobile" | "desktop"
  }
```

El `mode` se usa en todo el backend para adaptar herramientas disponibles
(música/notas vs inventario/WhatsApp/reportes).

---

## 2. Orden de voz (móvil) → entregable (PC)

### Paso a paso

1. **Celular** captura audio → `SpeechRecognition` → `transcript`.
2. Frontend móvil envía:
   ```http
   POST /api/v1/voice/command
   Authorization: Bearer <Firebase ID Token>
   {
     "uid": "...",
     "transcript": "genérame un Excel con las ventas de hoy",
     "device": "mobile",
     "mode": "business",
     "session_id": "sess_abc123"
   }
   ```
3. **FastAPI**:
   - Valida token → obtiene UID.
   - Llama a `adaptive.handle_command(...)`.
   - LLM (Groq) + Function Calling decide: `generate_excel`.
   - `tools.generate_excel(...)` crea el `.xlsx` en disco temporal.
   - `storage.upload_file(...)` sube a Firebase Storage.
   - Escribe documento en Firestore:
     ```
     /users/{uid}/deliverables/{autoId}
     {
       type: "xlsx",
       title: "Ventas de hoy",
       filename: "ventas_2026-10-30.xlsx",
       downloadUrl: "https://...",
       size: 15234,
       status: "ready",
       origin: "voice",
       transcript: "...",
       sessionId: "sess_abc123",
       createdAt: serverTimestamp()
     }
     ```
   - Actualiza `/users/{uid}/status/current` → `{ state: "ready", message: "..." }`.
4. **PC** tiene un `onSnapshot` sobre `deliverables`:
   - Al aparecer el documento, renderiza tarjeta con botón Descargar.
5. **Celular** recibe respuesta de voz:
   > “Listo. El Excel de ventas ya está disponible en el panel de tu computadora.”

---

## 3. Consola de escritorio (chat + adjuntos)

```
Usuario escribe o adjunta archivo en la PC
      │
      ▼
POST /api/v1/chat/message
{
  uid, sessionId, text?,
  attachments: [{ name, mime, storagePath }]
}
      │
      ▼
Adaptive Engine + herramientas
      │
      ▼
Respuesta en chat + posible nuevo entregable
(mismo path de Firestore /deliverables)
```

El historial de cada sesión se guarda en:
```
/users/{uid}/sessions/{sessionId}/messages
```

---

## 4. Sincronización en tiempo real

| Colección Firestore              | Quién escribe     | Quién escucha          |
|----------------------------------|-------------------|------------------------|
| `/users/{uid}/status/current`    | Backend           | Mobile + Desktop       |
| `/users/{uid}/deliverables`      | Backend           | Desktop (principal)    |
| `/users/{uid}/sessions/...`      | Backend + Desktop | Desktop                |
| `/users/{uid}/inventory`         | Mobile (foto)     | Desktop (modo business)|

---

## 5. Filosofía cero-negativas (implementación)

En `services/adaptive.py`:

1. Intentar herramienta exacta.
2. Si falla → herramienta alternativa o generación parcial.
3. Si no hay herramienta → respuesta útil generada por LLM + sugerencia de siguiente paso.
4. Nunca devolver al usuario frases del tipo “no puedo”, “no sé” o “no disponible”.