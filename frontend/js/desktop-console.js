/**
 * Consola de Agencia Interactiva (estilo ChatGPT / Gemini)
 * - Sidebar: historial de sesiones
 * - Centro: chat + resultados
 * - Inferior: input + adjuntar archivos
 * - Derecha: panel de entregables descargables
 */

import { API_BASE_URL } from "./firebase-config.js";

export function initDesktopConsole(user, firestore) {
  const root = document.getElementById("desktop-root") || document.body;
  const uid = user.uid;
  const mode = user.mode || "personal";
  let currentSessionId = "sess_" + Date.now().toString(36);

  root.innerHTML = `
  <div class="console-layout">
    <!-- SIDEBAR HISTORIAL -->
    <aside class="console-sidebar">
      <div class="sidebar-header">
        <h2>Dimitri</h2>
        <span class="mode-pill">${mode === "business" ? "Empresarial" : "Personal"}</span>
      </div>
      <button class="btn-new-session" id="btnNewSession">+ Nueva sesión</button>
      <div class="sessions-list" id="sessionsList">
        <div class="session-item active" data-id="${currentSessionId}">Sesión actual</div>
      </div>
      <div class="sidebar-footer">
        <span class="user-email">${user.email || uid}</span>
        <button id="btnLogoutConsole">Salir</button>
      </div>
    </aside>

    <!-- CHAT CENTRAL -->
    <main class="console-main">
      <div class="chat-messages" id="chatMessages">
        <div class="msg assistant">
          <div class="msg-bubble">
            Hola. Soy Dimitri. Escribe un comando, adjunta un archivo o pide un reporte.
            También puedes usar la voz desde tu celular con la misma cuenta.
          </div>
        </div>
      </div>
      <div class="chat-input-area">
        <label class="attach-btn" title="Adjuntar archivo">
          📎
          <input type="file" id="fileInput" multiple hidden accept="image/*,.pdf,.txt,.csv,.json,.py,.js,.sql,.md">
        </label>
        <textarea id="chatInput" rows="1" placeholder="Escribe un mensaje o pide un Excel, PDF, análisis..."></textarea>
        <button id="btnSend">Enviar</button>
      </div>
      <div class="attachments-preview" id="attachmentsPreview"></div>
    </main>

    <!-- PANEL ENTREGABLES -->
    <aside class="console-deliverables">
      <h3>📦 Entregables</h3>
      <div class="deliverables-list" id="deliverablesPanel">
        <p class="empty-d">Los archivos generados aparecerán aquí</p>
      </div>
    </aside>
  </div>
  `;

  // Estilos inyectados (si no hay CSS global)
  if (!document.getElementById("console-styles")) {
    const style = document.createElement("style");
    style.id = "console-styles";
    style.textContent = `
      .console-layout{display:grid;grid-template-columns:240px 1fr 280px;height:100dvh;background:#0a0e17;color:#e0f7fa;font-family:system-ui,sans-serif}
      .console-sidebar{background:#0c1220;border-right:1px solid rgba(0,229,255,.15);display:flex;flex-direction:column;padding:16px}
      .sidebar-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}
      .sidebar-header h2{color:#00e5ff;font-size:1.2rem}
      .mode-pill{font-size:.68rem;background:rgba(0,229,255,.15);color:#00e5ff;padding:3px 8px;border-radius:8px;text-transform:uppercase}
      .btn-new-session{width:100%;padding:10px;border:1px dashed rgba(0,229,255,.35);background:transparent;color:#7dd3fc;border-radius:10px;cursor:pointer;margin-bottom:14px;font-size:.85rem}
      .sessions-list{flex:1;overflow:auto}
      .session-item{padding:10px 12px;border-radius:8px;cursor:pointer;font-size:.85rem;margin-bottom:4px;opacity:.75}
      .session-item.active,.session-item:hover{background:rgba(0,229,255,.12);opacity:1}
      .sidebar-footer{border-top:1px solid rgba(0,229,255,.12);padding-top:12px;font-size:.78rem;display:flex;justify-content:space-between;align-items:center}
      .sidebar-footer button{background:none;border:none;color:#f87171;cursor:pointer;font-size:.78rem}
      .console-main{display:flex;flex-direction:column;min-width:0}
      .chat-messages{flex:1;overflow:auto;padding:24px;display:flex;flex-direction:column;gap:14px}
      .msg{display:flex;max-width:85%}
      .msg.user{align-self:flex-end}
      .msg.assistant{align-self:flex-start}
      .msg-bubble{padding:12px 16px;border-radius:14px;line-height:1.5;font-size:.95rem}
      .msg.user .msg-bubble{background:rgba(0,229,255,.18);border:1px solid rgba(0,229,255,.25)}
      .msg.assistant .msg-bubble{background:#0f172a;border:1px solid rgba(0,229,255,.12)}
      .chat-input-area{display:flex;gap:10px;padding:14px 18px;border-top:1px solid rgba(0,229,255,.12);align-items:flex-end}
      .chat-input-area textarea{flex:1;resize:none;border-radius:12px;border:1px solid rgba(0,229,255,.25);background:#0c1220;color:#e0f7fa;padding:12px 14px;font-size:.95rem;max-height:120px}
      .chat-input-area textarea:focus{outline:none;border-color:#00e5ff}
      .attach-btn{width:42px;height:42px;display:flex;align-items:center;justify-content:center;border-radius:10px;background:rgba(0,229,255,.1);cursor:pointer;font-size:1.2rem}
      #btnSend{background:#00e5ff;color:#04121a;border:none;padding:0 18px;height:42px;border-radius:10px;font-weight:700;cursor:pointer}
      .attachments-preview{padding:0 18px 10px;font-size:.8rem;opacity:.7}
      .console-deliverables{background:#0c1220;border-left:1px solid rgba(0,229,255,.15);padding:16px;overflow:auto}
      .console-deliverables h3{color:#7dd3fc;font-size:.95rem;margin-bottom:14px}
      .deliverable-item{background:#0f172a;border:1px solid rgba(0,229,255,.2);border-radius:12px;padding:12px;margin-bottom:10px}
      .deliverable-item .type{font-size:.65rem;text-transform:uppercase;color:#00e5ff;margin-bottom:4px}
      .deliverable-item h4{font-size:.9rem;margin-bottom:6px}
      .deliverable-item a,.deliverable-item button{display:inline-block;margin-top:6px;background:#00e5ff;color:#04121a;border:none;padding:6px 10px;border-radius:7px;font-size:.8rem;font-weight:600;cursor:pointer;text-decoration:none}
      .empty-d{opacity:.45;font-size:.85rem;text-align:center;padding:20px 0}
      @media(max-width:900px){.console-layout{grid-template-columns:1fr}.console-sidebar,.console-deliverables{display:none}}
    `;
    document.head.appendChild(style);
  }

  const chatMessages = document.getElementById("chatMessages");
  const chatInput = document.getElementById("chatInput");
  const btnSend = document.getElementById("btnSend");
  const fileInput = document.getElementById("fileInput");
  const attachmentsPreview = document.getElementById("attachmentsPreview");
  const deliverablesPanel = document.getElementById("deliverablesPanel");
  let pendingFiles = [];

  function appendMsg(role, text) {
    const div = document.createElement("div");
    div.className = `msg ${role}`;
    div.innerHTML = `<div class="msg-bubble">${text.replace(/\n/g, "<br>")}</div>`;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  fileInput.addEventListener("change", () => {
    pendingFiles = Array.from(fileInput.files || []);
    attachmentsPreview.textContent = pendingFiles.length
      ? "Adjuntos: " + pendingFiles.map(f => f.name).join(", ")
      : "";
  });

  async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text && !pendingFiles.length) return;

    appendMsg("user", text || "(archivo adjunto)");
    chatInput.value = "";
    const filesInfo = pendingFiles.map(f => ({ name: f.name, mime: f.type }));
    pendingFiles = [];
    attachmentsPreview.textContent = "";
    fileInput.value = "";

    appendMsg("assistant", "Procesando...");

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/chat/message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          uid,
          session_id: currentSessionId,
          text,
          attachments: filesInfo,
          mode,
        }),
      });
      const data = await res.json();
      // Quitar "Procesando..."
      chatMessages.lastChild.remove();
      appendMsg("assistant", data.chat_reply || data.spoken || "Listo.");
      if (data.deliverable_created) {
        // El listener de Firestore actualizará el panel; refuerzo local:
        refreshDeliverables();
      }
    } catch (e) {
      chatMessages.lastChild.remove();
      appendMsg("assistant", "Estoy trabajando en tu pedido. Cuando el backend esté conectado verás el resultado aquí.");
    }
  }

  btnSend.addEventListener("click", sendMessage);
  chatInput.addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  document.getElementById("btnNewSession").onclick = () => {
    currentSessionId = "sess_" + Date.now().toString(36);
    chatMessages.innerHTML = "";
    appendMsg("assistant", "Nueva sesión iniciada. ¿En qué te ayudo?");
    document.querySelectorAll(".session-item").forEach(el => el.classList.remove("active"));
    const item = document.createElement("div");
    item.className = "session-item active";
    item.dataset.id = currentSessionId;
    item.textContent = "Sesión actual";
    document.getElementById("sessionsList").prepend(item);
  };

  document.getElementById("btnLogoutConsole").onclick = () => {
    localStorage.removeItem("dimitri_user");
    location.reload();
  };

  // Listener entregables (Firestore o localStorage fallback)
  function refreshDeliverables() {
    const key = "dimitri_deliverables_" + uid;
    const items = JSON.parse(localStorage.getItem(key) || "[]");
    if (firestore) {
      // Preferir Firestore cuando esté configurado
      firestore.collection("users").doc(uid).collection("deliverables")
        .orderBy("createdAt", "desc").limit(30)
        .onSnapshot(snap => {
          if (snap.empty) {
            deliverablesPanel.innerHTML = `<p class="empty-d">Los archivos generados aparecerán aquí</p>`;
            return;
          }
          deliverablesPanel.innerHTML = "";
          snap.forEach(doc => {
            const d = doc.data();
            const el = document.createElement("div");
            el.className = "deliverable-item";
            const fname = d.filename || d.title || "archivo";
            el.innerHTML = `
              <div class="type">${d.type || "file"}</div>
              <h4>${d.title || fname}</h4>
              <a href="${API_BASE_URL}/api/v1/files/download/${encodeURIComponent(fname)}" target="_blank">Descargar</a>
            `;
            deliverablesPanel.appendChild(el);
          });
        });
      return;
    }
    // Fallback local
    if (!items.length) return;
    deliverablesPanel.innerHTML = "";
    items.slice().reverse().forEach(d => {
      const el = document.createElement("div");
      el.className = "deliverable-item";
      el.innerHTML = `
        <div class="type">${d.type || "file"}</div>
        <h4>${d.title || "Entregable"}</h4>
        <button onclick="alert('Conecta el backend para descargar el archivo real')">Ver</button>
      `;
      deliverablesPanel.appendChild(el);
    });
  }

  refreshDeliverables();
}