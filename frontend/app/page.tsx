import Link from "next/link";
export default function HomePage(){return <main className="mx-auto max-w-5xl px-4 py-16 space-y-8">
  <p className="text-brand-700 font-semibold">TrendML · Proyecto integrador · Grupo 14</p>
  <h1 className="text-5xl font-bold">Análisis de productos y estimación semanal de ventas</h1>
  <p className="text-lg text-slate-600">Consulta tendencias, compara precios y ejecuta un modelo de aprendizaje automático. Esta entrega combina un catálogo sintético de demostración con un laboratorio de ventas históricas reales.</p>
  <div className="flex gap-4"><Link href="/login" className="rounded-xl bg-brand-500 text-white px-5 py-3">Entrar a la demo</Link><Link href="/training" className="rounded-xl border px-5 py-3">Ver evaluación del modelo</Link></div>
  <section className="grid md:grid-cols-3 gap-5">{[
    ["Tendencias", "Crecimiento observado y bajas de precio mediante cálculos convencionales."],
    ["Predicción con IA", "Modelo entrenado que estima unidades para siete días desde un corte histórico."],
    ["Evaluación transparente", "Comparación temporal contra referencias simples, errores por producto y limitaciones."],
  ].map(([title,text])=><article key={title} className="card p-6"><h2 className="text-xl font-semibold">{title}</h2><p className="mt-3">{text}</p></article>)}</section>
  <p className="rounded-xl bg-amber-50 p-5">UCI Online Retail contiene transacciones británicas de 2010–2011. No hay una cuenta vendedora de Mercado Libre conectada ni una validación comercial actual. La aplicación apoya la revisión humana.</p>
</main>;}
