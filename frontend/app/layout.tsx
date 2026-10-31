import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/Navbar";

export const metadata: Metadata = {
  title: "TrendML · Análisis y predicción de ventas",
  description:
    "Demostración académica de análisis de productos y predicción histórica de ventas.",
  openGraph: {
    title: "TrendML",
    description: "Análisis de productos y laboratorio histórico con IA",
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
