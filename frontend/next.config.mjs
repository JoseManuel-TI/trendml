/** @type {import('next').NextConfig} */
const nextConfig = {
  distDir: process.env.TRENDML_BUILD_DIR || ".next",
  experimental: {
    typedRoutes: true
  }
};

export default nextConfig;
