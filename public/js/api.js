// Küçük fetch() sarmalayıcısı — tüm /api/* istekleri buradan geçer.
const API_BASE = "/api";

async function apiRequest(path, { method = "GET", body } = {}) {
  const res = await fetch(API_BASE + path, {
    method,
    credentials: "include",
    headers: body !== undefined ? { "Content-Type": "application/json" } : {},
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  let data = null;
  try {
    data = await res.json();
  } catch {
    // no-content (ör. logout 204) — yoksay
  }

  if (!res.ok) {
    const detail = data && data.detail;
    let message = "İstek başarısız oldu";
    if (typeof detail === "string") {
      message = detail;
    } else if (Array.isArray(detail) && detail.length) {
      // FastAPI/Pydantic validasyon hatası formatı
      message = detail.map((d) => d.msg).join(", ");
    }
    const err = new Error(message);
    err.status = res.status;
    throw err;
  }

  return data;
}

window.api = {
  get: (path) => apiRequest(path),
  post: (path, body) => apiRequest(path, { method: "POST", body }),
};

// Basit göreli zaman gösterimi: "3 saat önce" gibi.
function timeAgo(isoString) {
  const date = new Date(isoString);
  const seconds = Math.floor((Date.now() - date.getTime()) / 1000);

  const steps = [
    ["yıl", 31536000],
    ["ay", 2592000],
    ["hafta", 604800],
    ["gün", 86400],
    ["saat", 3600],
    ["dakika", 60],
  ];

  for (const [label, secondsInUnit] of steps) {
    const value = Math.floor(seconds / secondsInUnit);
    if (value >= 1) {
      return `${value} ${label} önce`;
    }
  }
  return "az önce";
}
