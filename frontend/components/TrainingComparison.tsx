"use client";
import { useEffect, useState } from "react";

type Metrics = Record<string, number>;
type Case = {product_id:string;title:string;origin:string;target_end:string;actual:number;predictions:Metrics};
type Comparison = {version:string;worst_cases?:Case[];labels:Record<string,string>;validation_mae:Metrics;selected_model:string;selected_method:string;validation:{cutoff:string;mae:Metrics}[];comparison:{training_pairs:number;cases:Case[];mae:Metrics};per_product:{product_id:string;title:string;mae:Metrics}[]};
const number = (value:number) => value.toLocaleString('es-AR',{maximumFractionDigits:1});

export default function TrainingComparison({version=2}:{version?:2|3}) {
  const [data,setData] = useState<Comparison|null>(null);
  const [failed,setFailed] = useState(false);
  const [product,setProduct] = useState('');
  const expectedVersion=version===3?'weekly-residual-v3':'weekly-lags-v2';
  useEffect(()=>{
    const controller=new AbortController();
    setData(null); setFailed(false); setProduct('');
    fetch(`/training-results-v${version}.json`,{cache:'no-store',signal:controller.signal})
      .then(r=>{if(!r.ok)throw Error();return r.json();})
      .then((result:Comparison)=>{
        if(result.version!==expectedVersion)throw Error('Unexpected experiment version');
        if(!controller.signal.aborted)setData(result);
      }).catch(()=>{if(!controller.signal.aborted)setFailed(true);});
    return ()=>controller.abort();
  },[version,expectedVersion]);
  if(failed)return <section className="card p-6">No se pudo cargar la comparación v{version}. Ejecuta scripts/train_uci_v{version}.py y recarga la página.</section>;
  if(!data||data.version!==expectedVersion)return <section className="card p-6">Cargando comparación v{version}…</section>;
  const keys=Object.keys(data.labels);
  const rows=data.comparison.cases.filter(c=>!product||c.product_id===product);
  const modelError=data.comparison.mae[data.selected_model];
  const reference=Math.min(data.comparison.mae.last_week,data.comparison.mae.mean_4_weeks);
  return <section className="card p-6 space-y-5">
    <div><h2 className="text-2xl font-semibold">Versión {version}: {version===3?"corregir el promedio de ventas":"ventas recientes y comparación temporal"}</h2><p className="mt-2">{version===3?"La v3 aprende una corrección sobre el promedio de cuatro semanas. Incorpora historial de 56 días, frecuencia de días sin ventas y variabilidad por producto.":"Ventas de 7, 14 y 28 días, variación semanal, precio y calendario."} Los cinco métodos se comparan sobre los mismos productos, fechas y ejemplos disponibles.</p></div>
    <div className="rounded-lg bg-slate-50 p-4"><p><strong>Modelo v{version} elegido en validación:</strong> {data.labels[data.selected_model]}.</p><p><strong>Mejor método en validación, incluidas referencias:</strong> {data.labels[data.selected_method]}.</p><p className="mt-2">{modelError < reference ? 'En noviembre, el modelo seleccionado también supera a ambas referencias.' : 'En noviembre, el modelo seleccionado no supera a la mejor referencia.'} Esta comparación es exploratoria: los períodos ya se habían consultado. Las mejoras orientan el desarrollo y requieren una evaluación independiente. No acredita rendimiento futuro ni habilita el uso para decisiones de stock.</p></div>
    <div className="overflow-x-auto"><table className="w-full text-sm"><caption className="text-left pb-2 font-semibold">Error absoluto medio en unidades por producto y semana · menor es mejor</caption><thead><tr className="border-b text-left"><th className="p-2">Método</th>{data.validation.map(f=><th className="p-2" key={f.cutoff}>{f.cutoff}</th>)}<th className="p-2">Promedio validación</th><th className="p-2">Noviembre*</th></tr></thead><tbody>{keys.map(k=><tr className="border-b" key={k}><th className="p-2 text-left font-normal">{data.labels[k]}{k===data.selected_model?' · elegido':''}</th>{data.validation.map(f=><td className="p-2" key={f.cutoff}>{number(f.mae[k])}</td>)}<td className="p-2">{number(data.validation_mae[k])}</td><td className="p-2">{number(data.comparison.mae[k])}</td></tr>)}</tbody></table></div>
    <p className="text-sm text-slate-600">Cada corte evalúa cuatro semanas posteriores y entrena solo con objetivos ya conocidos. Productos seleccionados al 1 de agosto de 2011. Se descartaron los primeros {version===3?55:27} días de cada serie por falta de historial para las variables nuevas. El modelo {version===3?"v2":"v1"} se volvió a ajustar sobre esas mismas filas; sus cifras pueden diferir del experimento original.</p>
    <div className="overflow-x-auto"><table className="w-full text-sm"><caption className="text-left font-semibold pb-2">Errores por producto en noviembre*</caption><thead><tr className="text-left border-b"><th className="p-2">Producto</th>{keys.map(k=><th className="p-2" key={k}>{data.labels[k]}</th>)}</tr></thead><tbody>{data.per_product.map(p=><tr className="border-b" key={p.product_id}><th className="p-2 text-left font-normal">{p.title}</th>{keys.map(k=><td className="p-2" key={k}>{number(p.mae[k])}</td>)}</tr>)}</tbody></table></div>
    {data.worst_cases && <details className="border rounded-lg p-4"><summary className="cursor-pointer font-semibold">Cinco mayores errores del modelo elegido en noviembre</summary><p className="my-3 text-sm">Son casos para investigar; no se eliminaron ni se usaron para volver a ajustar esta versión.</p><ul className="space-y-2">{data.worst_cases.map(c=><li key={c.product_id+c.origin}><strong>{c.title}</strong> · {c.origin}: observado {number(c.actual)}, estimado {number(c.predictions[data.selected_model])}, error {number(Math.abs(c.actual-c.predictions[data.selected_model]))} unidades.</li>)}</ul></details>}
    <label className="block font-semibold">Detalle semanal v{version} <select className="border rounded px-2 py-1 max-w-full font-normal" value={product} onChange={e=>setProduct(e.target.value)}><option value="">Todos los productos</option>{data.per_product.map(p=><option key={p.product_id} value={p.product_id}>{p.title}</option>)}</select></label>
    <div className="overflow-x-auto"><table className="w-full text-sm"><thead><tr className="text-left border-b"><th className="p-2">Producto</th><th className="p-2">Desde / hasta</th><th className="p-2">Real</th>{keys.map(k=><th className="p-2" key={k}>{data.labels[k]}</th>)}</tr></thead><tbody>{rows.map(c=><tr key={c.product_id+c.origin} className="border-b"><td className="p-2">{c.title}</td><td className="p-2 whitespace-nowrap">{c.origin}<br/>{c.target_end}</td><td className="p-2">{number(c.actual)}</td>{keys.map(k=><td className="p-2" key={k}>{number(c.predictions[k])}</td>)}</tr>)}</tbody></table></div>
    <p className="text-sm text-slate-600">*Noviembre: {data.comparison.cases.length} casos; {data.comparison.training_pairs} pares para entrenar cada modelo. El artefacto v{version} final se reentrena posteriormente con todo el historial y se guarda por separado. El flujo operativo conserva su modelo actual.</p>
  </section>;
}
