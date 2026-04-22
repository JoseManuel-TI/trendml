"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { apiPost, setToken } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    try {
      await apiPost("/api/auth/register", { email, phone, password });
      const data = await apiPost<{ access_token: string }>("/api/auth/login", { email, password });
      setToken(data.access_token);
      router.push("/dashboard");
    } catch {
      setError("No fue posible registrarte.");
    }
  }

  return (
    <main className="mx-auto max-w-md px-4 py-14">
      <div className="card p-7">
        <h1 className="text-3xl font-semibold">Crear cuenta</h1>
        <form className="mt-6 space-y-4" onSubmit={onSubmit}>
          <input className="w-full rounded-xl border border-slate-300 px-4 py-3" type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <input className="w-full rounded-xl border border-slate-300 px-4 py-3" type="tel" placeholder="WhatsApp (ej: 5491170644758)" value={phone} onChange={(e) => setPhone(e.target.value)} />
          <input className="w-full rounded-xl border border-slate-300 px-4 py-3" type="password" placeholder="Contraseña" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} />
          {error ? <p className="text-sm text-red-600">{error}</p> : null}
          <button className="w-full rounded-xl bg-brand-500 text-white py-3 font-medium hover:bg-brand-700" type="submit">Crear cuenta</button>
        </form>
      </div>
    </main>
  );
}
