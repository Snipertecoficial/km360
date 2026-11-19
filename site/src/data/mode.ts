// Itens EXEMPLO (placeholder: true) aparecem no `astro dev` e nos previews da Vercel, para revisão.
// Em build de produção (Vercel produção ou `npm run build` para a Hostinger) ficam de fora do site.
// SHOW_EXAMPLES=1 força mostrar. Só para o frontmatter dos .astro (roda no build, não no navegador).
export const SHOW_EXAMPLES =
  import.meta.env.DEV || process.env.VERCEL_ENV === 'preview' || process.env.SHOW_EXAMPLES === '1';
