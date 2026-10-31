/**
 * Detección automática de rol según el dispositivo.
 * Móvil / Tablet → Hub de Voz (cara)
 * Escritorio → Panel de Recepción
 */

export function detectRole() {
  const ua = navigator.userAgent.toLowerCase();
  const isMobile = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(ua);
  const isTablet = /ipad|android(?!.*mobile)/i.test(ua) || (navigator.maxTouchPoints > 1 && window.innerWidth >= 768);
  const isDesktop = !isMobile && !isTablet && window.innerWidth >= 1024;

  // Preferencia manual (para testing)
  const forced = localStorage.getItem("dimitri_force_role");
  if (forced === "mobile" || forced === "desktop") return forced;

  if (isDesktop) return "desktop";
  return "mobile"; // por defecto cara + voz
}

export function isMobileRole() {
  return detectRole() === "mobile";
}

export function isDesktopRole() {
  return detectRole() === "desktop";
}