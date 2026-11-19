// URL pública do site (canonical, hreflang, Open Graph e sitemap):
// SITE_URL (domínio oficial, ex.: https://km360.com.br) > domínio de produção da Vercel > nenhuma (local).
import { defineConfig } from 'astro/config';

const vercel = process.env.VERCEL_PROJECT_PRODUCTION_URL;

export default defineConfig({
  site: process.env.SITE_URL || (vercel ? `https://${vercel}` : undefined),
});
