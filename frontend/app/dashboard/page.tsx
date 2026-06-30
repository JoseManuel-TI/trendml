"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import { LineChart } from "@/components/LineChart";
import { StatCard } from "@/components/StatCard";
import { apiGet, apiPost } from "@/lib/api";

type User = {
  id: number;
  email: string;
  subscription_plan: "starter" | "pro" | "premium";
};

type Trending = {
  product_id: string;
  title: string;
  growth_rate: number;
  last_price: number;
};

type PriceAlert = {
  product_id: string;
  title: string;
  previous_price: number;
  current_price: number;
  diff_percentage: number;
};

type Prediction = {
  product_id: string;
  title: string;
  predicted_sales_next_week: number;
  current_sales: number;
};

type Seller = {
  seller_id: string;
  total_products: number;
  avg_sales: number;
};

type Funnel = {
  window_days: number;
  checkouts_started: number;
  payments_approved: number;
  payments_pending: number;
  recovered_after_reminder: number;
  conversion_rate_pct: number;
  recovered_rate_pct: number;
  estimated_mrr_ars: number;
  approved_by_plan: {
    starter: number;
    pro: number;
    premium: number;
  };
};

type PendingLead = {
  user_id: number;
  email: string;
  phone: string | null;
  plan: "starter" | "pro" | "premium";
  provider: string;
  checkout_url: string | null;
  created_at: string;
  hours_pending: number;
  reminder_sent: boolean;
};

type PendingLeadsResponse = {
  total: number;
  leads: PendingLead[];
  captured_at: string;
};

function normalizeWhatsAppNumber(raw: string): string {
  const digits = raw.replace(/\D/g, "");
  if (!digits) return "";
  if (digits.startsWith("54")) return digits;
  if (digits.length === 10) return `549${digits}`;
  return digits;
}

function buildWhatsAppLink(lead: PendingLead): string {
  const number = normalizeWhatsAppNumber(lead.phone || "");
  if (!number) return "";
  const message = [
    `Hola ${lead.email}, soy de TrendML.`,
    `Veo que dejaste pendiente el plan ${lead.plan.toUpperCase()}.`,
    `Si quieres te ayudo a activarlo ahora.`,
    lead.checkout_url ? `Link de pago: ${lead.checkout_url}` : "",
  ].join("\n");

  return `https://wa.me/${number}?text=${encodeURIComponent(message)}`;
}

export default function DashboardPage() {
  const params = useSearchParams();
  const [user, setUser] = useState<User | null>(null);
  const [trending, setTrending] = useState<Trending[]>([]);
  const [alerts, setAlerts] = useState<PriceAlert[]>([]);
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [sellers, setSellers] = useState<Seller[]>([]);
  const [funnel, setFunnel] = useState<Funnel | null>(null);
  const [pendingLeads, setPendingLeads] = useState<PendingLeadsResponse | null>(null);
  const [mlConnected, setMlConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError("");

      try {
        const profile = await apiGet<User>("/api/auth/me");
        setUser(profile);

        const trendingData = await apiGet<Trending[]>("/api/trending");
        setTrending(trendingData);

        try {
          const alertsData = await apiGet<PriceAlert[]>("/api/price-alerts");
          setAlerts(alertsData);
        } catch {
          setAlerts([]);
        }

        try {
          const predictionsData = await apiGet<Prediction[]>("/api/predictions");
          setPredictions(predictionsData);
        } catch {
          setPredictions([]);
        }

        try {
          const sellersData = await apiGet<Seller[]>("/api/top-sellers");
          setSellers(sellersData);
        } catch {
          setSellers([]);
        }

        try {
          const funnelData = await apiGet<Funnel>("/api/admin/funnel");
          setFunnel(funnelData);
        } catch {
          setFunnel(null);
        }

        try {
          const leadsData = await apiGet<PendingLeadsResponse>("/api/admin/pending-leads");
          setPendingLeads(leadsData);
        } catch {
          setPendingLeads(null);
        }

        try {
          await apiGet("/api/auth/ml/token-info");
          setMlConnected(true);
        } catch {
          setMlConnected(false);
        }
      } catch {
        setError("No autorizado. Inicia sesión para ver el dashboard.");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  const planLabel = useMemo(() => {
    if (!user) return "-";
    return user.subscription_plan.toUpperCase();
  }, [user]);

  if (loading) {
    return <main className="mx-auto max-w-6xl px-4 py-12">Cargando dashboard...</main>;
  }

  if (error) {
    return (
      <main className="mx-auto max-w-4xl px-4 py-12">
        <div className="card p-8">
          <p className="text-red-600">{error}</p>
          <Link href="/login" className="mt-4 inline-block rounded-xl bg-slate-900 text-white px-4 py-2">Ir a login</Link>
        </div>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-7xl px-4 py-10 space-y-8">
      {params.get("upgraded") === "1" ? (
        <p className="rounded-xl bg-emerald-50 text-emerald-700 px-4 py-3 border border-emerald-200">
          Plan actualizado correctamente.
        </p>
      ) : null}

      <section className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-semibold">Dashboard</h1>
          <p className="text-slate-600">Plan actual: <strong>{planLabel}</strong></p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-sm">
            <span className={`inline-block h-2.5 w-2.5 rounded-full ${mlConnected ? "bg-emerald-500" : "bg-slate-300"}`} />
            <span className="text-slate-600">ML {mlConnected ? "Conectado" : "Desconectado"}</span>
          </div>
          {mlConnected ? (
            <button
              className="rounded-xl border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-100"
              onClick={async () => {
                await apiPost("/api/auth/ml/disconnect", {});
                setMlConnected(false);
              }}
            >
              Desconectar
            </button>
          ) : (
            <button
              className="rounded-xl bg-yellow-500 text-white px-3 py-1.5 text-sm hover:bg-yellow-600"
              onClick={async () => {
                const { url } = await apiGet<{ url: string }>("/api/auth/ml/login");
                window.location.href = url;
              }}
            >
              Conectar ML
            </button>
          )}
          <Link href="/pricing" className="rounded-xl bg-brand-500 text-white px-4 py-2 hover:bg-brand-700">Mejorar plan</Link>
        </div>
      </section>

      <section className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Trending" value={`${trending.length}`} subtitle="Disponible en todos los planes" />
        <StatCard title="Price Alerts" value={`${alerts.length}`} subtitle="Pro y Premium" />
        <StatCard title="Predicciones" value={`${predictions.length}`} subtitle="Pro y Premium" />
        <StatCard title="Top Sellers" value={`${sellers.length}`} subtitle="Solo Premium" />
      </section>

      <section className="card p-6">
        <h2 className="text-xl font-semibold">Predicción de ventas</h2>
        {predictions.length === 0 ? (
          <p className="mt-4 text-slate-600">Función bloqueada para tu plan. <Link className="text-brand-700 underline" href="/pricing">Actualizar ahora</Link>.</p>
        ) : (
          <div className="mt-4">
            <LineChart
              labels={predictions.slice(0, 10).map((item) => item.title.slice(0, 20))}
              values={predictions.slice(0, 10).map((item) => item.predicted_sales_next_week)}
              label="Ventas estimadas"
            />
          </div>
        )}
      </section>

      <section className="grid lg:grid-cols-2 gap-6">
        <div className="card p-6 overflow-x-auto">
          <h3 className="text-lg font-semibold">Productos tendencia</h3>
          <table className="w-full mt-4 text-sm">
            <thead>
              <tr className="text-left border-b border-slate-200">
                <th className="py-2">Producto</th>
                <th>Crecimiento</th>
                <th>Precio</th>
              </tr>
            </thead>
            <tbody>
              {trending.slice(0, 10).map((item) => (
                <tr key={item.product_id} className="border-b border-slate-100">
                  <td className="py-2">{item.title}</td>
                  <td>{(item.growth_rate * 100).toFixed(1)}%</td>
                  <td>${item.last_price.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card p-6 overflow-x-auto">
          <h3 className="text-lg font-semibold">Alertas de precio</h3>
          {alerts.length === 0 ? (
            <p className="mt-3 text-slate-600">Función Pro/Premium. <Link className="text-brand-700 underline" href="/pricing">Desbloquear</Link>.</p>
          ) : (
            <table className="w-full mt-4 text-sm">
              <thead>
                <tr className="text-left border-b border-slate-200">
                  <th className="py-2">Producto</th>
                  <th>Actual</th>
                  <th>Baja</th>
                </tr>
              </thead>
              <tbody>
                {alerts.slice(0, 10).map((item) => (
                  <tr key={item.product_id} className="border-b border-slate-100">
                    <td className="py-2">{item.title}</td>
                    <td>${item.current_price.toLocaleString()}</td>
                    <td className="text-orange-600">-{item.diff_percentage}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>

      <section className="card p-6">
        <h3 className="text-lg font-semibold">Revenue Funnel (30 días)</h3>
        {!funnel ? (
          <p className="mt-3 text-slate-600">
            Disponible en plan Premium. <Link className="text-brand-700 underline" href="/pricing">Desbloquear</Link>.
          </p>
        ) : (
          <div className="mt-4 space-y-5">
            <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-3">
              <StatCard title="Checkouts" value={`${funnel.checkouts_started}`} subtitle="Iniciados" />
              <StatCard title="Aprobados" value={`${funnel.payments_approved}`} subtitle="Pagos exitosos" />
              <StatCard title="Recuperados" value={`${funnel.recovered_after_reminder}`} subtitle="Por reminder 24h" />
              <StatCard title="Conversión" value={`${funnel.conversion_rate_pct}%`} subtitle="Aprobados / iniciados" />
              <StatCard title="MRR Est." value={`$${funnel.estimated_mrr_ars.toLocaleString()} ARS`} subtitle="Base 30 días" />
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left border-b border-slate-200">
                    <th className="py-2">Plan</th>
                    <th>Pagos aprobados</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-slate-100">
                    <td className="py-2">Starter</td>
                    <td>{funnel.approved_by_plan.starter}</td>
                  </tr>
                  <tr className="border-b border-slate-100">
                    <td className="py-2">Pro</td>
                    <td>{funnel.approved_by_plan.pro}</td>
                  </tr>
                  <tr>
                    <td className="py-2">Premium</td>
                    <td>{funnel.approved_by_plan.premium}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}
      </section>

      <section className="card p-6">
        <h3 className="text-lg font-semibold">Leads Pendientes (Cierre Manual)</h3>
        {!pendingLeads ? (
          <p className="mt-3 text-slate-600">
            Disponible en plan Premium. <Link className="text-brand-700 underline" href="/pricing">Desbloquear</Link>.
          </p>
        ) : pendingLeads.total === 0 ? (
          <p className="mt-3 text-slate-600">No hay checkouts pendientes de más de 2 horas.</p>
        ) : (
          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left border-b border-slate-200">
                  <th className="py-2">Email</th>
                  <th>WhatsApp</th>
                  <th>Plan</th>
                  <th>Horas pendiente</th>
                  <th>Reminder</th>
                  <th>Acción</th>
                </tr>
              </thead>
              <tbody>
                {pendingLeads.leads.slice(0, 20).map((lead) => (
                  <tr key={`${lead.user_id}-${lead.created_at}`} className="border-b border-slate-100">
                    <td className="py-2">{lead.email}</td>
                    <td>{lead.phone || "-"}</td>
                    <td>{lead.plan.toUpperCase()}</td>
                    <td>{lead.hours_pending}h</td>
                    <td>{lead.reminder_sent ? "Sí" : "No"}</td>
                    <td className="space-x-3">
                      <a className="text-brand-700 underline" href={`mailto:${lead.email}?subject=Tu plan TrendML ${lead.plan.toUpperCase()}&body=Hola, te ayudo a activar tu plan ahora mismo.`}>
                        Email
                      </a>
                      {buildWhatsAppLink(lead) ? (
                        <a className="text-emerald-700 underline" href={buildWhatsAppLink(lead)} target="_blank" rel="noreferrer">
                          WhatsApp
                        </a>
                      ) : (
                        <span className="text-slate-400">Sin WhatsApp</span>
                      )}
                      {lead.checkout_url ? (
                        <a className="text-slate-800 underline" href={lead.checkout_url} target="_blank" rel="noreferrer">
                          Link pago
                        </a>
                      ) : null}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}
