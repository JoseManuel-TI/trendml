"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { apiPost, setToken } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    try {
      const data = await apiPost<{ access_token: string }>("/api/auth/login", { email, password });
      setToken(data.access_token);
      router.push("/dashboard");
    } catch {
      setError("Credenciales inválidas o backend no disponible");
    }
  }

  async function loginAsDemo() {
    setError("");
    try {
      const demoEmail = "seller1@example.com";
      const demoPassword = "Password123!";
      setEmail(demoEmail);
      setPassword(demoPassword);
      const data = await apiPost<{ access_token: string }>("/api/auth/login", {
        email: demoEmail,
        password: demoPassword,
      });
      setToken(data.access_token);
      router.push("/dashboard");
    } catch {
      setError("No se pudo iniciar sesión demo. Ejecuta: bash scripts/seed_local.sh");
    }
  }

  return (
    <main className="mx-auto max-w-md px-4 py-14">
      <div className="card p-7">
        <h1 className="text-3xl font-semibold">Iniciar sesión</h1>
        <form className="mt-6 space-y-4" onSubmit={onSubmit}>
          <input className="w-full rounded-xl border border-slate-300 px-4 py-3" type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <input className="w-full rounded-xl border border-slate-300 px-4 py-3" type="password" placeholder="Contraseña" value={password} onChange={(e) => setPassword(e.target.value)} required />
          {error ? <p className="text-sm text-red-600">{error}</p> : null}
          <button className="w-full rounded-xl bg-brand-500 text-white py-3 font-medium hover:bg-brand-700" type="submit">Entrar</button>
          <button
            className="w-full rounded-xl border border-slate-300 bg-white py-3 font-medium hover:bg-slate-100"
            type="button"
            onClick={loginAsDemo}
          >
            Entrar como demo
          </button>
        </form>
      </div>
    </main>
  );
}
