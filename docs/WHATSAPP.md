# Módulo WhatsApp (Modo Empresarial)

## Qué ve el usuario

En el celular, si el perfil es **Empresarial**, antes de la cara aparece:

1. Bloque **WhatsApp del negocio**
2. Botón **Generar QR**
3. Estado: Desconectado / Escanea el QR / Conectado
4. Inventario de productos
5. Botón **Ir a Dimitri (voz)**

## Qué está armado

| Pieza | Estado |
|-------|--------|
| UI QR + estados | ✅ Frontend |
| Endpoints FastAPI `/api/v1/whatsapp/*` | ✅ Esqueleto |
| Respuesta automática a clientes | ⏳ Requiere bridge real |

## Cómo activarlo de verdad (cuando configures APIs)

Opción recomendada (gratis / barata):

1. **Evolution API** (o Baileys) en un VPS / Docker.
2. Al crear sesión, Evolution devuelve el QR en base64.
3. En `routers/whatsapp.py` → `create_or_get_session`:
   - llamar a Evolution
   - devolver `{ "qr": "data:image/png;base64,..." }`
4. Webhook de mensajes entrantes → `POST /api/v1/whatsapp/webhook`
5. Ahí llamar a `adaptive.handle_command` y contestar por la API de Evolution.

Mientras el bridge no esté, el frontend muestra un **QR demo** y permite simular “conectado” para probar la interfaz.

## Flujo objetivo final

```
Cliente escribe al WhatsApp del negocio
        │
        ▼
Evolution / Baileys → webhook Dimitri
        │
        ▼
Adaptive Engine (inventario + cero negativas)
        │
        ▼
Respuesta automática al cliente por WhatsApp
```