"use client";
import Link from "next/link";
import {useEffect, useState} from "react";
import {apiGet, apiPost} from "@/lib/api";

type Product = {product_id: string; title: string; as_of: string};
type Forecast = {prediction:number; baseline:number; title:string; as_of:string; target_start:string; target_end:string; model_version:string; computed_at:string};
export default function ForecastPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [selected, setSelected] = useState("");
  const [result, setResult] = useState<Forecast|null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  useEffect(() => {let active = true;
    apiGet<{products:Product[]}>("/api/lab/products").then(data => {
      if(active){setProducts(data.products);setSelected(data.products[0]?.product_id || "");}
    }).catch(e => {if(active)setError(e.message);}).finally(() => {if(active)setLoading(false);});
    return () => {active = false;};
  }, []);
  async function predict() {
    setBusy(true);setError("");setResult(null);
    try {setResult(await apiPost<Forecast>("/api/lab/forecast", {product_id:selected}));}
    catch(e){setError(e instanceof Error ? e.message : "No se pudo calcular");}
    finally{setBusy(false);}
  }
  return <main className="mx-auto max-w-4xl px-4 py-10 space-y-6">
    <h1 className="text-3xl font-semibold">Predicción histórica en vivo</h1>
    <p>El botón ejecuta el modelo entrenado en el servidor. No entrena nuevamente ni lee una predicción precalculada.</p>
    <div className="rounded-xl bg-amber-50 border border-amber-200 p-4">Datos reales históricos UCI Online Retail, Reino Unido, 2010–2011. El horizonte corresponde a la fecha histórica seleccionada, no a la semana actual. Resultado experimental sin validación comercial.</div>
    <p><Link className="underline" href="/login">Iniciar sesión</Link> · Requiere plan Pro o Premium para calcular. La cuenta demo local permite probarlo sin pagos.</p>
    <section className="card p-6 space-y-4">
      <label htmlFor="product" className="block font-medium">Producto del conjunto histórico</label>
      <select id="product" className="w-full rounded-lg border p-3" value={selected} disabled={busy || loading} onChange={e=>{setSelected(e.target.value);setResult(null);setError("");}}>
        {products.map(p=><option key={p.product_id} value={p.product_id}>{p.title} · {p.as_of}</option>)}
      </select>
      {loading ? <p>Cargando catálogo…</p> : products.length === 0 ? <p>No hay un catálogo disponible.</p> : null}
      <button className="rounded-xl bg-brand-500 text-white px-5 py-3 disabled:opacity-50" disabled={busy || !selected} onClick={predict}>{busy ? "Calculando…" : "Calcular predicción"}</button>
      {error && <p role="alert" className="text-red-700">{error}</p>}
    </section>
    {result && <section aria-live="polite" className="card p-6 space-y-3">
      <h2 className="text-xl font-semibold">{result.title}</h2>
      <p className="text-3xl font-semibold">{result.prediction.toFixed(1)} unidades estimadas</p>
      <p>Período: {result.target_start} al {result.target_end}. Datos hasta {result.as_of}.</p>
      <p>Referencia promedio de cuatro semanas: {result.baseline.toFixed(1)} unidades.</p>
      <p>Modelo: {result.model_version}. Cálculo ejecutado: {new Date(result.computed_at).toLocaleString("es-AR")}.</p>
      <p>No conocemos aquí las ventas futuras del período estimado. La diferencia con la referencia no demuestra mayor precisión.</p>
    </section>}
    <Link className="underline" href="/training">Ver evaluación histórica, errores y comparación con referencias</Link>
  </main>;
}
