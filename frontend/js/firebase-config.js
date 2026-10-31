// Rellena con tu proyecto Firebase
const firebaseConfig = {
  apiKey: "AIzaSyBQrrDcUXJwbq3A8YRNQr0fXO0RGfpKN_w",
  authDomain: "dimitri-system.firebaseapp.com",
  projectId: "dimitri-system",
  storageBucket: "dimitri-system.firebasestorage.app",
  messagingSenderId: "742406022917",
  appId: "1:742406022917:web:3def5ccc885344ff83f96c"
};

// Inicialización del SDK
firebase.initializeApp(firebaseConfig);

// URL del backend FastAPI (cambia en producción)
export const API_BASE_URL = "http://localhost:8000";
