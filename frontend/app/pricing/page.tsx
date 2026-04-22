"use client";

import { useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { apiPost, getToken } from "@/lib/api";

const plans = [
  { id: "starter", name: "Starter", price: "$9.000 ARS/mes", features: ["Trend básico", "Alertas de precio", "1 usuario"] },
  { id: "pro", name: "Pro", price: "$29.000 ARS/mes", features: ["Predicciones ML", "Top sellers", "3 usuarios"] },
  { id: "premium", name: "Premium", price: "$59.000 ARS/mes", features: ["Todas las features", "Admin metrics", "Usuarios ilimitados"] },
];

type CheckoutResponse = {
  status: string;
  plan: string;
  provider: "mercadopago" | "mock";
  checkout_url?: string | null;
};

export default function PricingPage() {
  const router = useRouter();
  const params = useSearchParams();
  const [loadingPlan, setLoadingPlan] = useState("");
  const [error, setError] = useState("");

  const billingMessage = useMemo(() => {
    const billing = params.get("billing");
    if (billing === "success") return "Pago aprobado. Tu plan se activará en segundos.";
    if (billing === "pending") return "Pago pendiente. Mercado Pago confirmará cuando se acredite.";
    if (billing === "failure") return "Pago cancelado o rechazado. Puedes intentarlo otra vez.";
    return "";
  }, [params]);

  async function handleCheckout(plan: string) {
    setError("");

    if (!getToken()) {
      router.push("/login");
      return;
    }

    setLoadingPlan(plan);
    try {
      const result = await apiPost<CheckoutResponse>("/api/subscriptions/checkout", { plan });
      if (result.checkout_url) {
        window.location.href = result.checkout_url;
        return;
      }
      router.push("/dashboard?upgraded=1");
    } catch {
      setError("No se pudo iniciar el checkout. Revisa la configuración de pagos.");
    } finally {
      setLoadingPlan("");
    }
  }

  return (
    <main className="mx-auto max-w-6xl px-4 py-14">
      <h1 className="text-4xl font-semibold">Precios simples y escalables</h1>
      <p className="mt-3 text-slate-600">Empieza con el plan que mejor se ajuste a tu operación.</p>
      {billingMessage ? <p className="mt-4 rounded-xl bg-emerald-50 text-emerald-700 px-4 py-3 border border-emerald-200">{billingMessage}</p> : null}
      {error ? <p className="mt-4 rounded-xl bg-red-50 text-red-700 px-4 py-3 border border-red-200">{error}</p> : null}
      <section className="mt-10 grid md:grid-cols-3 gap-5">
        {plans.map((plan) => (
          <article key={plan.id} className="card p-6">
            <h2 className="text-2xl font-semibold">{plan.name}</h2>
            <p className="mt-2 text-3xl font-bold text-brand-700">{plan.price}</p>
            <ul className="mt-4 space-y-2 text-sm text-slate-700">
              {plan.features.map((feature) => (
                <li key={feature}>• {feature}</li>
              ))}
            </ul>
            <button
              className="mt-6 w-full rounded-xl bg-slate-900 text-white px-4 py-2 hover:bg-slate-700 disabled:opacity-50"
              onClick={() => handleCheckout(plan.id)}
              disabled={loadingPlan === plan.id}
            >
              {loadingPlan === plan.id ? "Redirigiendo..." : `Elegir ${plan.name}`}
            </button>
          </article>
        ))}
      </section>
    </main>
  );
}
