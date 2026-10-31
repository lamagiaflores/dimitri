# Notas de Integración Frontend

El archivo `index.html` actual contiene la interfaz completa de la **cara animada + voz** (rol móvil).

Para completar la arquitectura:

1. **Añadir al final del `<body>` de index.html** (antes de los scripts existentes):

```html
<link rel="stylesheet" href="css/styles.css">
<div id="desktop-root" style="display:none"></div>
<script type="module" src="js/app.js"></script>
```

2. **Conectar el reconocimiento de voz al backend**  
   En la función `handle()` o `processCommand()` del script original, después de detectar el wake-word, enviar:

```js
async function sendToBackend(transcript) {
  const uid = window.DIMITRI_UID;
  if (!uid) return;
  try {
    const res = await fetch(`${window.DIMITRI_API}/api/v1/voice/command`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        uid,
        transcript,
        device: "mobile",
        language: "es-PE"
      })
    });
    const data = await res.json();
    // data.spoken → usar speak(data.spoken, data.expression)
    // data.deliverable_created → avisar que ya está en el panel
    return data;
  } catch (e) {
    console.error(e);
    // Fallback local siempre positivo
    return { spoken: "Estoy trabajando en eso de la mejor forma posible.", expression: "thinking" };
  }
}
```

3. **Firebase**  
   Rellena `js/firebase-config.js` con tus credenciales reales.

4. **Service Worker**  
   Ya actualizado a v3 e incluye los nuevos JS.

Con estos pasos la PWA única detecta el dispositivo, autentica al usuario y sincroniza entregables entre celular y PC.