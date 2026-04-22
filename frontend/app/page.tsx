import Link from "next/link";

const features = [
  { title: "Productos tendencia", text: "Detecta categorías y productos en crecimiento antes que la competencia." },
  { title: "Alertas de precio", text: "Monitorea caídas de precio y reacciona rápido con mejores márgenes." },
  { title: "Predicción de demanda", text: "Usa modelos de ML para estimar ventas futuras por producto." },
];

export default function HomePage() {
  return (
    <main>
      <section className="bg-gradient-to-r from-emerald-100 via-white to-cyan-100">
        <div className="mx-auto max-w-6xl px-4 py-20 grid md:grid-cols-2 gap-10 items-center">
          <div>
            <p className="inline-flex rounded-full bg-white/80 px-3 py-1 text-xs font-semibold text-brand-700 border border-brand-100">
              AI Market Intelligence para LATAM
            </p>
            <h1 className="mt-4 text-5xl font-bold tracking-tight text-slate-900">
              Vende mejor en Mercado Libre con datos, no con intuición.
            </h1>
            <p className="mt-5 text-lg text-slate-600">
              TrendML analiza el mercado y te muestra oportunidades accionables: tendencias, precios y predicciones.
            </p>
            <div className="mt-8 flex gap-3">
              <Link href="/register" className="rounded-xl bg-brand-500 px-5 py-3 text-white font-medium hover:bg-brand-700">
                Comenzar gratis
              </Link>
              <Link href="/dashboard" className="rounded-xl border border-slate-300 bg-white px-5 py-3 font-medium hover:bg-slate-100">
                Ver demo
              </Link>
            </div>
          </div>
          <div className="card p-6 bg-white/90">
            <p className="text-sm text-slate-500">Snapshot del mercado</p>
            <div className="mt-4 space-y-4">
              <div>
                <p className="text-xs text-slate-500">Productos tendencia</p>
                <p className="text-3xl font-semibold text-brand-700">+37 hoy</p>
              </div>
              <div>
                <p className="text-xs text-slate-500">Alertas de precio</p>
                <p className="text-3xl font-semibold text-orange-600">112 detectadas</p>
              </div>
              <div>
                <p className="text-xs text-slate-500">Categorías monitoreadas</p>
                <p className="text-3xl font-semibold text-cyan-700">64</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-16">
        <h2 className="text-3xl font-semibold">Cómo funciona</h2>
        <div className="mt-8 grid md:grid-cols-3 gap-5">
          {features.map((feature) => (
            <article key={feature.title} className="card p-6">
              <h3 className="text-xl font-semibold">{feature.title}</h3>
              <p className="mt-3 text-slate-600">{feature.text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 pb-20">
        <h2 className="text-3xl font-semibold">Planes</h2>
        <div className="mt-8 grid md:grid-cols-3 gap-5">
          {[
            ["Starter", "$9.000 ARS/mes", "1 mercado, alertas básicas"],
            ["Pro", "$29.000 ARS/mes", "Predicciones y top sellers"],
            ["Premium", "$59.000 ARS/mes", "Análisis avanzado + exportación"],
          ].map((plan) => (
            <article key={plan[0]} className="card p-6">
              <h3 className="text-xl font-semibold">{plan[0]}</h3>
              <p className="mt-2 text-3xl font-bold text-brand-700">{plan[1]}</p>
              <p className="mt-2 text-slate-600">{plan[2]}</p>
              <Link href="/pricing" className="mt-6 inline-block rounded-xl bg-slate-900 text-white px-4 py-2 hover:bg-slate-700">
                Elegir plan
              </Link>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
