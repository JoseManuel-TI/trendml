const posts = [
  {
    slug: "como-detectar-productos-tendencia",
    title: "Cómo detectar productos tendencia en Mercado Libre",
    excerpt: "Framework práctico para elegir productos con demanda creciente.",
  },
  {
    slug: "pricing-dinamico-latam",
    title: "Pricing dinámico para ecommerce en LATAM",
    excerpt: "Cuándo bajar o subir precios según señales del mercado.",
  },
];

export default function BlogPage() {
  return (
    <main className="mx-auto max-w-4xl px-4 py-14">
      <h1 className="text-4xl font-semibold">Blog</h1>
      <div className="mt-8 space-y-4">
        {posts.map((post) => (
          <article key={post.slug} className="card p-5">
            <h2 className="text-xl font-semibold">{post.title}</h2>
            <p className="mt-2 text-slate-600">{post.excerpt}</p>
          </article>
        ))}
      </div>
    </main>
  );
}
