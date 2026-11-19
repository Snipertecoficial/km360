import type { APIRoute } from 'astro';

// PT e ES como versões da mesma página (hreflang). Sem URL pública (build local), sai vazio.
export const GET: APIRoute = ({ site }) => {
  const alt = site
    ? `<xhtml:link rel="alternate" hreflang="pt-BR" href="${new URL('/', site)}"/><xhtml:link rel="alternate" hreflang="es" href="${new URL('/es/', site)}"/>`
    : '';
  const urls = site ? ['/', '/es/'].map((p) => `<url><loc>${new URL(p, site)}</loc>${alt}</url>`).join('') : '';
  return new Response(
    `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">${urls}</urlset>\n`,
    { headers: { 'Content-Type': 'application/xml; charset=utf-8' } },
  );
};
