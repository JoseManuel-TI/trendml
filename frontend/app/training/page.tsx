"use client";
import { useEffect, useState } from "react";
import TrainingComparison from "../../components/TrainingComparison";

type Case = {product_id:string;title:string;origin:string;target_end:string;actual:number;prediction:number;baseline:number;absolute_error:number};
type Result = {source:{url:string;author:string;license:string};evaluation:{training_pairs:number;test_cases:number;products:number;mae:number;baseline_mae:number;beats_baseline:boolean;cutoff:string};cases:Case[];forecasts:{product_id:string;title:string;as_of:string;target_end:string;prediction:number}[]};
export default function Training() {
  const [result,setResult]=useState<Result|null>(null);
  const [error,setError]=useState(false);
  const [product,setProduct]=useState("");
  useEffect(()=>{fetch('/training-results.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error();return r.json();}).then(setResult).catch(()=>setError(true));},[]);
  if(error)return <main className="max-w-6xl mx-auto p-8">Todavía no hay una evaluación disponible. Ejecuta el entrenamiento local para generar los resultados.</main>;
  if(!result)return <main className="max-w-6xl mx-auto p-8">Cargando evaluación…</main>;
  const e=result.evaluation;
  const products=Array.from(new Map(result.cases.map(c=>[c.product_id,c.title])).entries());
  const cases=result.cases.filter(c=>!product||c.product_id===product);
  return <main className="max-w-6xl mx-auto px-4 py-10 space-y-6">
    <div><p className="text-sm font-semibold text-brand-700">Laboratorio de aprendizaje • Grupo 14</p><h1 className="text-3xl font-semibold mt-2">Entrenamiento con ventas reales históricas</h1><p className="mt-3 text-slate-600">Comercio británico, 2010–2011. Estimamos unidades vendidas en los siete días siguientes. Son ventas brutas: se excluyen cancelaciones y devoluciones. Estos resultados no representan demanda actual de Mercado Libre.</p></div>
    <TrainingComparison version={3} />
    <details className="space-y-4"><summary className="cursor-pointer font-semibold">Consultar experimento anterior · versión 2</summary><TrainingComparison /></details>
    <h2 className="text-2xl font-semibold">Experimento original · versión 1</h2>
    <section className="grid sm:grid-cols-3 gap-4">
      <div className="card p-5"><p>Error medio del modelo</p><strong className="text-3xl">{e.mae.toFixed(1)}</strong><p>unidades por producto y semana</p></div>
      <div className="card p-5"><p>Error de la referencia</p><strong className="text-3xl">{e.baseline_mae.toFixed(1)}</strong><p>repetir las ventas de la semana anterior</p></div>
      <div className="card p-5"><p>Evaluación</p><strong className="text-3xl">{e.test_cases} casos</strong><p>{e.products} productos · {e.training_pairs} ejemplos de entrenamiento</p></div>
    </section>
    <section className="card p-6"><h2 className="text-xl font-semibold">¿Qué aprendimos?</h2><p className="mt-2">{e.beats_baseline?'El modelo logró un error menor que la referencia en este período.':'El modelo tuvo más error que repetir la semana anterior. Todavía necesita mejoras antes de orientar decisiones de stock.'}</p><p className="mt-2 text-slate-600">Se entrenó con resultados conocidos hasta {e.cutoff}. Después se evaluaron cuatro semanas, sin ajustar el modelo con sus resultados. Un error menor es mejor; esta medida no es un porcentaje de aciertos.</p></section>
    <section className="card p-6"><div className="flex flex-wrap justify-between items-center gap-3"><h2 className="text-xl font-semibold">Predicción frente a ventas observadas</h2><label>Producto <select className="border rounded px-2 py-1" value={product} onChange={ev=>setProduct(ev.target.value)}><option value="">Todos</option>{products.map(([id,title])=><option key={id} value={id}>{title}</option>)}</select></label></div>
      <div className="overflow-x-auto mt-4"><table className="w-full text-sm"><thead><tr className="text-left border-b"><th className="py-2">Producto</th><th>Desde / hasta</th><th>Real</th><th>Modelo</th><th>Semana anterior</th><th>Error absoluto</th></tr></thead><tbody>{cases.map(c=><tr key={c.product_id+c.origin} className="border-b"><td className="py-3 pr-3">{c.title}</td><td className="whitespace-nowrap pr-3">{c.origin}<br/>{c.target_end}</td><td>{c.actual.toFixed(0)}</td><td>{c.prediction.toFixed(1)}</td><td>{c.baseline.toFixed(0)}</td><td>{c.absolute_error.toFixed(1)}</td></tr>)}</tbody></table></div>
    </section>
    <details className="card p-6"><summary className="cursor-pointer font-semibold">Estimaciones posteriores al final del historial</summary><p className="my-3">Modelo reentrenado hasta el 8 de diciembre de 2011. Las estimaciones al 15 de diciembre no tienen ventas posteriores disponibles para comprobarlas.</p><ul>{result.forecasts.map(f=><li className="py-1" key={f.product_id}>{f.title}: {f.prediction.toFixed(1)} unidades</li>)}</ul></details>
    <footer className="text-sm text-slate-600"><a className="underline" href={result.source.url} target="_blank" rel="noreferrer">Fuente: UCI Online Retail</a> · {result.source.author} · {result.source.license}. Precios originales en GBP. La evaluación usa unidades, no dinero.</footer>
  </main>;
}
