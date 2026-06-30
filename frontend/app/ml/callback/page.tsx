"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";

export const dynamic = "force-dynamic";

export default function MlCallbackPage() {
  const params = useSearchParams();
  const success = params.get("success");
  const error = params.get("error");

  return (
    <main className="mx-auto max-w-lg px-4 py-20 text-center">
      {success ? (
        <div className="card p-8">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100 text-3xl text-emerald-600">
            ✓
          </div>
          <h1 className="text-2xl font-semibold">MercadoLibre conectado</h1>
          <p className="mt-2 text-slate-600">
            Tu cuenta de MercadoLibre se vinculó correctamente. Ya podés usar los datos enriquecidos.
          </p>
          <Link
            href="/dashboard"
            className="mt-6 inline-block rounded-xl bg-brand-500 px-6 py-3 text-white hover:bg-brand-700"
          >
            Ir al dashboard
          </Link>
        </div>
      ) : (
        <div className="card p-8">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-red-100 text-3xl text-red-600">
            ✕
          </div>
          <h1 className="text-2xl font-semibold">Error de conexión</h1>
          <p className="mt-2 text-slate-600">
            No se pudo conectar MercadoLibre. {error === "oauth_error" ? "Ocurrió un error en la autorización." : "Intentalo de nuevo."}
          </p>
          <Link
            href="/dashboard"
            className="mt-6 inline-block rounded-xl bg-brand-500 px-6 py-3 text-white hover:bg-brand-700"
          >
            Volver al dashboard
          </Link>
        </div>
      )}
    </main>
  );
}
