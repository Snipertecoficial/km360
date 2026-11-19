# KM 360 Assessoria Comercial · Site oficial

Site institucional da **KM 360 Assessoria Comercial**, referência no Brás (São Paulo) em assessoria para lojas de moda, atacado e varejo, que vendem em marketplaces. A página tem um objetivo só: levar o lojista ao **diagnóstico grátis**, que abre o WhatsApp com a mensagem pronta.

O diferencial visual são as **cenas 3D renderizadas no Unreal Engine 5.8**, que avançam com o scroll em cada seção, sobre a cor própria de cada serviço.

## O que o site entrega

- **Página única em português e espanhol** (`/` e `/es/`), com SEO completo: `hreflang`, Open Graph, JSON-LD `ProfessionalService`, `sitemap.xml` e `robots.txt`.
- **8 capítulos com cenas Unreal.** As cenas são quadros pré-renderizados com fundo transparente, desenhados num `<canvas>` conforme o scroll. O hero gira 360° com o arraste.
- **Seções por marketplace:** Mercado Livre, TikTok Shop, Shein e Shopee, cada uma com a sua cor, os seus pontos de atuação e "o erro que mais vemos".
- **Calculadora de margem.** Mostra o lucro real por peça, o quanto fica pelo caminho no mês e a mesma peça comparada nos quatro canais.
- **Mini-diagnóstico em 3 perguntas.** Abre o WhatsApp com as respostas e a simulação. Não tem backend e nada fica salvo no site.
- **Origem de cada contato.** As UTMs e os cliques de anúncio (Meta, Google, TikTok) vão junto na mensagem, como `ref:`.
- **Pronto para medir.** Os eventos `diagnostico_whatsapp`, `Contact` (Meta) e `generate_lead` (GA4) já disparam assim que o Pixel ou o GA4 forem instalados.
- **Mobile em primeiro lugar.**
  - No celular, as cenas usam quadros de 720 px: 11,8 MB contra 37,6 MB no desktop.
  - O menu do celular é próprio.
  - Com `prefers-reduced-motion`, as animações são desligadas.
- **Acessibilidade.** Passa na checagem WCAG 2 AA sem violações, tem foco visível e todo texto é HTML real, sem texto dentro das imagens.

## Tecnologia

| Parte | Ferramenta |
|---|---|
| Site | [Astro](https://astro.build) 7, estático, sem framework de UI e sem outras dependências |
| Cenas 3D | Unreal Engine 5.8, Movie Render Queue, Python (Geometry Script) via MCP |
| Hospedagem | Vercel (preset Astro, pasta `site`, cabeçalhos em `site/vercel.json`) |
| Domínio | Hostinger (próxima etapa) |

## Estrutura

```
.
├── site/                    # o site (Astro)
│   ├── src/data/content.ts  # TODO o texto PT/ES, números, tarifas e itens provisórios
│   ├── src/data/calc.ts     # lógica da calculadora
│   ├── src/data/mode.ts     # quando os itens EXEMPLO aparecem
│   ├── src/components/      # Page, Chapter (cena + scroll), Calculadora, Diagnostico
│   ├── src/scripts/scroll.ts# player dos quadros, cor por seção, menu, giro do hero
│   ├── vercel.json          # cache dos quadros e cabeçalhos de segurança
│   └── public/frames/<cena>/1x1 e 1x1m   # quadros WebP (desktop e celular) + crop.json
├── unreal/KM360/            # projeto Unreal Engine 5.8
│   ├── Scripts/             # build_<cena>.py (monta cada cena), render, conversão
│   └── PROGRESS.md          # pipeline de render e decisões técnicas
├── docs/superpowers/specs/  # especificação do projeto
└── plano.md                 # checklist do que foi feito e do que falta
```

## Rodar localmente

Requisito: Node.js 22.23 ou mais novo (o projeto usa o 24).

```bash
npm --prefix site ci
```

```bash
npm run dev
```

O site abre em `http://localhost:4321`. Para gerar a versão final em `site/dist/` e conferir os textos e as contas:

```bash
npm run build
```

```bash
npm run check
```

## Publicar na Vercel

1. Na Vercel, clique em **Add New → Project** e importe o repositório `Snipertecoficial/km360`.
2. Confira se a Vercel escolheu **Root Directory `site`** e o preset **Astro** (ela detecta sozinha). O `site/vercel.json` cuida do cache dos quadros e dos cabeçalhos de segurança.
3. Clique em **Deploy**. Cada push na `main` publica em produção, e cada branch ou PR ganha um link de preview.

Variáveis de ambiente opcionais (Settings → Environment Variables):

| Variável | Para que serve |
|---|---|
| `SITE_URL` | Endereço oficial, por exemplo `https://seudominio.com.br`. Usado em canonical, Open Graph e sitemap. Sem ela, o site usa o domínio de produção da Vercel. |
| `SHOW_EXAMPLES` | Use `1` para mostrar os itens EXEMPLO num build de produção. Não use em produção. |

## Domínio oficial na Hostinger

**Recomendado: o site fica na Vercel e o domínio aponta para ela.** Assim você mantém o deploy automático, o CDN e o HTTPS da Vercel.

1. Na Vercel, abra **Settings → Domains**, adicione o domínio (com e sem `www`) e anote os registros DNS que ela mostrar. Normalmente são um registro **A** para o domínio raiz e um **CNAME** para o `www`.
2. Na Hostinger, abra **Domínios → DNS / Nameservers**, crie esses registros e apague os registros A ou CNAME antigos do mesmo nome.
3. Volte à Vercel e espere o domínio ficar verificado. O certificado HTTPS sai sozinho.
4. Em **Environment Variables**, defina `SITE_URL=https://seudominio.com.br` e faça um novo deploy.

**Alternativa: hospedar na própria Hostinger.** O site é estático:

```bash
SITE_URL=https://seudominio.com.br npm run build
```

Depois envie o conteúdo de `site/dist/` para a pasta `public_html` pelo Gerenciador de Arquivos ou por FTP. Nesse caso o cache e os cabeçalhos do `site/vercel.json` não valem; eles precisariam de um `.htaccess`.

## Conteúdo provisório (EXEMPLO)

Alguns itens ainda não são reais e estão marcados com `placeholder: true` em `site/src/data/content.ts`:

- Números por plataforma
- Cases
- Depoimentos
- Logos de clientes
- Tarifas de referência da calculadora
- Respostas das perguntas frequentes

O comportamento depende de onde o site roda:

| Onde | Itens EXEMPLO |
|---|---|
| `npm run dev` e previews da Vercel | Aparecem com o selo **EXEMPLO**, para revisão |
| Produção (Vercel ou build para a Hostinger) | **Ficam de fora.** Nada inventado vai ao ar |

Para publicar um item, troque pelo dado real e apague o `placeholder: true`. Ele passa a aparecer em produção no próximo deploy.

## Cenas 3D (Unreal Engine)

Cada cena é gerada por script e pode ser refeita do zero:

1. Abra `unreal/KM360/KM360.uproject` no Unreal Engine 5.8. No Mac, precisa do Xcode e do Metal Toolchain.
2. Com o servidor MCP do editor ativo (porta 8000), rode `python3 -I unreal/KM360/Scripts/mcp.py pyfile <caminho>/build_<cena>.py`.
3. Renderize com `K.render(...)`, converta com `sheet.py webp <cena> ...` e gere a versão de celular e o recorte com `mobile_frames.py <cena>`.

O passo a passo completo, as luzes, o HDRI e os problemas já resolvidos estão em [`unreal/KM360/PROGRESS.md`](unreal/KM360/PROGRESS.md).

## Direitos

© 2026 KM 360 Assessoria Comercial · Brás, São Paulo/SP. Todos os direitos reservados. O código, os textos, a marca e as cenas 3D são de uso exclusivo da KM 360.
