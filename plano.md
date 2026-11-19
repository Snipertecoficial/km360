# Plano: site KM 360 com Unreal

Spec: [docs/superpowers/specs/2026-11-18-site-km360-design.md](docs/superpowers/specs/2026-11-18-site-km360-design.md)

## Fase 1: Ambiente
- [x] Epic Games Launcher instalado (Homebrew)
- [x] Unreal Engine 5.8.4 instalado (plugins MCP, AllToolsets, ToolsetRegistry, Terminal presentes)
- [x] Projeto `unreal/KM360/KM360.uproject` + plugins + `bAutoStartServer=True`
- [x] Python Bridge escrito em `unreal/KM360/Plugins/PythonBridge` (padrão do demo_toolset.py da Epic)
- [x] Cliente MCP HTTP em `unreal/KM360/Scripts/mcp.py`
- [x] Xcode 27.2 + Metal Toolchain + `xcode-select` apontando para o Xcode (o Unreal abre normalmente, inclusive pelo Launcher)
- [x] MCP na porta 8000 + `.mcp.json` oficial gerado (raiz e `unreal/KM360`)
- [x] Python Bridge: 4 testes do tutorial ok (versão, 5 cubos, persistência, traceback)
- [x] Render com alpha ligado (`r.PostProcessing.PropagateAlpha=True`)
- [x] 8 clipes renderizados no Unreal, 1200×1200 com alpha, em `site/public/frames/<clip>/1x1/` (816 quadros, 37 MB; detalhes em `unreal/KM360/PROGRESS.md`)
- [x] Versão mobile em `1x1m/` (720 px, só os quadros pares no celular): 11,8 MB medidos no celular contra 37,6 MB no desktop. Para regenerar após um re-render: `python3 unreal/KM360/Scripts/mobile_frames.py <clip>`
- [x] Melhorias (2026-11-19): calculadora com tarifa por canal + comparativo da peça nos 4 canais; origem do contato (UTM/fbclid/gclid/ttclid) vai como `ref:` na mensagem do WhatsApp; eventos `diagnostico_whatsapp`/`Contact`/`generate_lead` prontos para quando Pixel, GA4 ou GTM forem instalados; "o erro que mais vemos aqui" em cada marketplace; perguntas frequentes. **Para o cliente revisar:** tarifas (`fees` em content.ts, EXEMPLO), respostas do FAQ (EXEMPLO), textos dos erros por marketplace
- [x] Espaçamento apertado (blocos 2,75–5rem, capítulos 130–160vh; página ~16% mais curta) + menu do celular (botão Menu, lista com as 5 seções e troca de idioma)
- [x] Cenas Shein e Shopee refeitas no Unreal (v2): coleção entrando na arara; cupons e moedas virando venda na sacola (v1 guardada fora do projeto)
- [x] Celular sem vãos: abaixo de 900px só o hero fica preso; os outros capítulos têm a altura do conteúdo e a animação avança enquanto passam pela tela (página no celular 21.536 → 16.542px)
- [ ] Instalar Pixel do Meta / GA4 (aguardando IDs do cliente)
- [x] Capítulo Problema voltou às etiquetas de texto HTML, sem Unreal (pedido em 2026-11-19; `noFrames` no `Chapter`, 2 colunas no celular)
- [x] Redesign do site: 10 seções com cor própria, cor despejada pelo anel 360, header escuro com logo vetorial que se adapta a cada seção, calculadora de perda, copy PT/ES com gatilhos e hero girável. Validado: check, tsc, build, trava de produção, 0 erros e 0 violações a11y em desktop e 375px

## Fase 2: Site
- [x] Astro + conteúdo PT/ES + capítulos com fallback CSS (`site/`, rodar: `npm --prefix site run dev`)
- [x] Mini-diagnóstico que abre o WhatsApp (testado: validação, exclusão "ainda não vendo", mensagem)
- [x] Trava de provisórios em produção (testado: `VERCEL_ENV=production` falha)
- [x] Validação no browser (desktop 800px, mobile 375px, PT e ES, sem erros no console)
- [ ] Deploy de preview na Vercel (aguardando sua autorização)

## Fase 3: Cinemática
- [ ] Cena premium: K/M metálicos, anel 360, 4 estações e gráfico
- [ ] Sequencer: 8 clipes × 2 câmeras (16:9 e 9:16)
- [ ] Render (Movie Render Queue), conversão para WebP e entrada em `site/public/frames`

## Fase 4: Conteúdo real e lançamento
- [ ] Números por plataforma, cases, depoimentos e logos dos clientes (cliente envia)
- [ ] Domínio + deploy de produção
