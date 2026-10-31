"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

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
  predicted_sales_next_week: number | null;
  status: string;
  horizon_days: number;
  model_version: string;
  captured_at: string;
};

type Seller = {
  seller_id: string;
  total_products: number;
  avg_sales: number;
};

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [trending, setTrending] = useState<Trending[]>([]);
  const [alerts, setAlerts] = useState<PriceAlert[]>([]);
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [predictionError, setPredictionError] = useState("");
  const [sellers, setSellers] = useState<Seller[]>([]);
  const [alertError, setAlertError] = useState("");
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
        } catch (cause) {
          setAlertError(cause instanceof Error ? cause.message : "Error al consultar alertas");
          setAlerts([]);
        }

        try {
          const predictionsData = await apiGet<Prediction[]>("/api/predictions");
          setPredictions(predictionsData);
        } catch (cause) {
          setPredictionError(cause instanceof Error ? cause.message : "Error de predicciones");
          setPredictions([]);
        }

        try {
          const sellersData = await apiGet<Seller[]>("/api/top-sellers");
          setSellers(sellersData);
        } catch {
          setSellers([]);
        }

        try {
          await apiGet("/api/auth/ml/token-info");
          setMlConnected(true);
        } catch {
          setMlConnected(false);
        }
      } catch (cause) {
        setError(cause instanceof Error ? cause.message : "No se pudo cargar el dashboard.");
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
                try {
                  const { url } = await apiGet<{ url: string }>("/api/auth/ml/login");
                  window.location.href = url;
                } catch (cause) {setError(cause instanceof Error ? cause.message : "No se pudo conectar");}
              }}
            >
              Conectar ML
            </button>
          )}
          <Link href="/pricing" className="rounded-xl bg-brand-500 text-white px-4 py-2 hover:bg-brand-700">Mejorar plan</Link>
        </div>
      </section>

      <p className="rounded-xl bg-amber-50 p-4">Catálogo compartido de demostración académica. Los productos DEMO utilizan datos sintéticos, no ventas reales de Mercado Libre. <Link href="/forecast" className="underline">Probar el modelo con datos históricos UCI</Link>.</p>
      <section className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Trending" value={`${trending.length}`} subtitle="Disponible en todos los planes" />
        <StatCard title="Price Alerts" value={`${alerts.length}`} subtitle="Pro y Premium" />
        <StatCard title="Predicciones" value={`${predictions.length}`} subtitle="Pro y Premium" />
        <StatCard title="Top Sellers" value={`${sellers.length}`} subtitle="Solo Premium" />
      </section>

      <section className="card p-6">
        <h2 className="text-xl font-semibold">Predicción de ventas</h2>
        <p className="mt-2 text-sm text-slate-600">
          Incremento estimado de unidades en los próximos 7 días. El resultado no garantiza ventas.
        </p>
        {user?.subscription_plan === "starter" ? (
          <p className="mt-4">Disponible en Pro y Premium.</p>
        ) : predictionError ? (
          <p className="mt-4 text-red-600">No se pudo consultar el modelo. Reintenta recargando la página.</p>
        ) : predictions.length === 0 ? (
          <p className="mt-4">Todavía no hay resultados procesados con el modelo semanal.</p>
        ) : (
          <table className="w-full mt-4 text-sm">
            <thead><tr className="text-left"><th>Producto</th><th>Unidades en 7 días</th><th>Observación</th></tr></thead>
            <tbody>{predictions.map(item => (
              <tr key={item.product_id} className="border-b border-slate-100">
                <td className="py-2">{item.title}</td>
                <td>{item.status === "available" && item.predicted_sales_next_week !== null
                  ? item.predicted_sales_next_week.toFixed(1)
                  : item.status === "unverified_data" ? "Datos demo o sin procedencia verificada"
                  : item.status === "model_error" ? "Modelo no disponible"
                  : "Sin historial suficiente"}</td>
                <td>{new Date(item.captured_at + (item.captured_at.endsWith("Z") ? "" : "Z")).toLocaleString()}</td>
              </tr>
            ))}</tbody>
          </table>
        )}
      </section>

      <section className="grid lg:grid-cols-2 gap-6">
        <div className="card p-6 overflow-x-auto">
          <h3 className="text-lg font-semibold">Productos tendencia</h3>
          {trending.length === 0 && <p className="mt-3">No hay tendencias disponibles.</p>}
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
          {user?.subscription_plan === "starter" ? (
            <p className="mt-3 text-slate-600">Función Pro/Premium. <Link className="text-brand-700 underline" href="/pricing">Desbloquear</Link>.</p>
          ) : alertError ? <p role="alert" className="mt-3 text-red-600">{alertError}</p> : alerts.length === 0 ? <p className="mt-3">No se detectaron bajas de precio comparables.</p> : (
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

    </main>
  );
}
