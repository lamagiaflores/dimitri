/**
 * Orquestador principal de Dimitri PWA
 * Detecta el rol y carga la interfaz correspondiente.
 */

import { detectRole, isMobileRole } from "./device.js";
import { onUserChanged, login, register, getCurrentUser } from "./auth.js";
import { initDesktopPanel } from "./desktop-panel.js";
import { API_BASE_URL } from "./firebase-config.js";

// Firebase modular (Firestore) — se carga bajo demanda
let db = null;

async function loadFirestore() {
  if (db) return db;
  const { getFirestore } = await import("https://www.gstatic.com/firebasejs/10.14.0/firebase-firestore.js");
  const { initializeApp } = await import("https://www.gstatic.com/firebasejs/10.14.0/firebase-app.js");
  const { firebaseConfig } = await import("./firebase-config.js");
  const app = initializeApp(firebaseConfig);
  db = getFirestore(app);
  return db;
}

function showLogin() {
  const overlay = document.createElement("div");
  overlay.className = "login-overlay";
  overlay.id = "loginOverlay";
  overlay.innerHTML = `
    <div class="login-card">
      <h2>Dimitri</h2>
      <p style="margin-bottom:16px;opacity:.7">Inicia sesión para vincular móvil y PC</p>
      <input type="email" id="email" placeholder="Correo electrónico" />
      <input type="password" id="password" placeholder="Contraseña" />
      <button id="btnLogin">Entrar</button>
      <button id="btnRegister" style="background:transparent;color:#00e5ff;border:1px solid #00e5ff;margin-top:10px">Crear cuenta</button>
    </div>
  `;
  document.body.appendChild(overlay);

  document.getElementById("btnLogin").onclick = async () => {
    const email = document.getElementById("email").value;
    const pass = document.getElementById("password").value;
    try {
      await login(email, pass);
      overlay.remove();
    } catch (e) {
      alert("Error: " + e.message);
    }
  };

  document.getElementById("btnRegister").onclick = async () => {
    const email = document.getElementById("email").value;
    const pass = document.getElementById("password").value;
    try {
      await register(email, pass);
      overlay.remove();
    } catch (e) {
      alert("Error: " + e.message);
    }
  };
}

async function boot() {
  const role = detectRole();
  console.log("[Dimitri] Rol detectado:", role);

  // Auth
  onUserChanged(async (user) => {
    if (!user) {
      showLogin();
      return;
    }

    const firestore = await loadFirestore();

    if (role === "desktop") {
      // Ocultar cara y mostrar panel
      document.getElementById("face")?.style.setProperty("display", "none");
      document.getElementById("startOverlay")?.classList.add("hidden");
      document.getElementById("status")?.style.setProperty("display", "none");
      document.querySelector(".settings-btn")?.style.setProperty("display", "none");
      document.querySelector(".mic-reset-btn")?.style.setProperty("display", "none");

      // Crear contenedor desktop si no existe
      let desktopRoot = document.getElementById("desktop-root");
      if (!desktopRoot) {
        desktopRoot = document.createElement("div");
        desktopRoot.id = "desktop-root";
        document.body.appendChild(desktopRoot);
      }
      initDesktopPanel(user.uid, firestore);
    } else {
      // Rol móvil: la cara ya está en index.html
      // Aquí se puede conectar el envío de comandos al backend
      console.log("[Dimitri] Modo Hub de Voz listo. UID:", user.uid);
      window.DIMITRI_UID = user.uid;
      window.DIMITRI_API = API_BASE_URL;
    }
  });
}

// Arrancar cuando el DOM esté listo
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", boot);
} else {
  boot();
}