import Link from "next/link";
export default function PermissionsPage(){return <main className="mx-auto max-w-4xl px-4 py-12 space-y-6">
<h1 className="text-3xl font-semibold">Permisos de la demostración</h1>
<p>La entrega académica no requiere pagos. Los permisos se verifican en la API.</p>
<ul className="list-disc pl-6 space-y-3"><li>Starter: registro, acceso, tendencias y catálogo histórico.</li><li>Pro: además, alertas de precio y cálculo de predicciones.</li><li>Premium: además, consulta de vendedores. No concede acceso administrativo.</li></ul>
<p>Las cuentas nuevas empiezan en Starter. Usa la cuenta demo local para recorrer las funciones Pro.</p>
<Link href="/login" className="inline-block rounded-xl bg-brand-500 px-5 py-3 text-white">Ir al acceso</Link>
</main>;}
