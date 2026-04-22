import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/Navbar";

export const metadata: Metadata = {
  title: "TrendML - Inteligencia de mercado para Mercado Libre",
  description:
    "Detecta productos tendencia, alertas de precio y predicciones de ventas para vendedores de Mercado Libre.",
  openGraph: {
    title: "TrendML",
    description: "Market Intelligence para sellers de Mercado Libre",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>
        <Navbar />
        {children}
      </body>
    </html>
  );
}
