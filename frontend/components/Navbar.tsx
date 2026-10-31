import Link from "next/link";

export function Navbar() {
  return (
    <header className="border-b border-slate-200 bg-white/95 backdrop-blur sticky top-0 z-50">
      <nav className="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between">
        <Link href="/" className="text-xl font-semibold text-brand-700">TrendML</Link>
        <div className="flex items-center gap-5 text-sm">
          <Link href="/forecast" className="hover:text-brand-700">Predecir</Link>
          <Link href="/dashboard" className="hover:text-brand-700">Dashboard</Link>
          <a href="/training" className="hover:text-brand-700">Entrenamiento</a>
          <Link href="/pricing" className="hover:text-brand-700">Permisos</Link>
          <Link href="/login" className="hover:text-brand-700">Login</Link>
          <Link href="/register" className="rounded-xl bg-brand-500 text-white px-4 py-2 hover:bg-brand-700">Comenzar gratis</Link>
        </div>
      </nav>
    </header>
  );
}
