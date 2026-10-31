const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function getToken() {
  if (typeof window === "undefined") return "";
  return localStorage.getItem("trendml_token") || "";
}

export function setToken(token: string) {
  if (typeof window === "undefined") return;
  localStorage.setItem("trendml_token", token);
}

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: {
      Authorization: `Bearer ${getToken()}`,
      "Content-Type": "application/json",
    },
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error(await errorMessage(res));
  }

  return res.json();
}

export async function apiPost<T>(path: string, body: object): Promise<T> {
  const token = getToken();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    throw new Error(await errorMessage(res));
  }

  return res.json();
}

async function errorMessage(res: Response): Promise<string> {
  if (res.status === 401) return "Sesión inválida o vencida. Inicia sesión nuevamente.";
  if (res.status === 403) return "No tienes permisos para esta función. Inicia sesión y revisa tu plan.";
  const body = await res.json().catch(() => null);
  return typeof body?.detail === "string" ? body.detail : `No se pudo completar la solicitud (${res.status}).`;
}
