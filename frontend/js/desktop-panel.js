/**
 * Panel de Recepción / Agencia de Despacho
 * Solo se muestra cuando detectRole() === "desktop"
 */

import { API_BASE_URL } from "./firebase-config.js";

export function initDesktopPanel(uid, firestore) {
  const root = document.getElementById("desktop-root");
  if (!root) return;

  root.innerHTML = `
    <div class="desktop-layout">
      <header class="desktop-header">
        <h1>🤖 Dimitri — Agencia de Despacho</h1>
        <p>Entregables generados por voz desde el celular aparecen aquí en tiempo real.</p>
      </header>

      <section class="deliverables-section">
        <h2>📦 Entregables listos</h2>
        <div id="deliverables-list" class="deliverables-list">
          <p class="empty">Esperando pedidos por voz...</p>
        </div>
      </section>

      <section class="status-section">
        <h2>Estado actual</h2>
        <div id="assistant-status" class="status-card">Escuchando...</div>
      </section>
    </div>
  `;

  // Listener en tiempo real de Firestore
  if (firestore && uid) {
    const listEl = document.getElementById("deliverables-list");
    const statusEl = document.getElementById("assistant-status");

    // Deliverables
    firestore
      .collection("users")
      .doc(uid)
      .collection("deliverables")
      .orderBy("createdAt", "desc")
      .limit(20)
      .onSnapshot(snap => {
        if (snap.empty) {
          listEl.innerHTML = `<p class="empty">Aún no hay entregables. Habla al celular diciendo «Dimitri, créame un reporte...»</p>`;
          return;
        }
        listEl.innerHTML = "";
        snap.forEach(doc => {
          const d = doc.data();
          const card = document.createElement("div");
          card.className = "deliverable-card";
          card.innerHTML = `
            <div class="type-badge">${d.type || "file"}</div>
            <h3>${d.title || "Sin título"}</h3>
            <p class="meta">${d.transcript ? `"${d.transcript.slice(0, 60)}..."` : ""}</p>
            <button class="download-btn" data-id="${doc.id}">Descargar / Ver</button>
          `;
          listEl.appendChild(card);
        });
      });

    // Status
    firestore
      .collection("users")
      .doc(uid)
      .collection("status")
      .doc("current")
      .onSnapshot(doc => {
        if (doc.exists) {
          const s = doc.data();
          statusEl.textContent = `${s.state || "idle"} — ${s.message || ""}`;
        }
      });
  }
}