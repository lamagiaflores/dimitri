# Arquitectura final — Dimitri System

## Componentes

1. **PWA única (Vercel)**  
   - Detecta dispositivo → Mobile (cara + voz) o Desktop (consola interactiva).  
   - Login + selector Personal / Empresarial.  
   - Misma cuenta vincula ambos dispositivos.

2. **Backend FastAPI**  
   - `/api/v1/voice/command` — entrada desde el celular.  
   - `/api/v1/chat/message` — entrada desde la consola de PC (texto + adjuntos).  
   - `/api/v1/files/download/{filename}` — descarga de entregables.  
   - Motor adaptativo + Groq Function Calling + herramientas (PDF, Excel, DOCX, código).

3. **Firebase**  
   - Auth (email/password).  
   - Firestore: perfiles, status, deliverables, sessions/messages.  
   - Storage (opcional): archivos grandes.

## Principios

- Cero respuestas negativas.  
- Una sola app, dos roles de UI.  
- Entregables siempre van al panel de la PC.  
- Stack 100 % en free tiers.