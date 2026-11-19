# Site KM 360: design

Data: 2026-11-18. Status: aprovado pelo cliente (Seção 1). O restante foi decidido em conversa e ele pediu para avançar.

## Objetivo
Site da **KM 360 Assessoria Comercial** (Brás/SP, moda atacado e varejo) para o desafio "melhor site usando Unreal".
- **Público:** donos de loja de moda do Brás que vendem, ou querem vender, em marketplaces.
- **Função única da página:** levar o lojista a fazer o **mini-diagnóstico**, que abre o WhatsApp com a mensagem pronta.
- **Prova central (real):** +R$ 50 milhões faturados em marketplaces para clientes.

## Decisões
| Tema | Decisão |
|---|---|
| Entrega do Unreal | Cinemática pré-renderizada (Movie Render Queue) em sequência de quadros, avançada pelo scroll |
| Estrutura | **Capítulos**: um clipe por seção, com conteúdo HTML real entre eles e transições casadas |
| Estilo 3D | Premium abstrato: azul-marinho, metais do logo (K azul, M prata), anel 360 de luz |
| Idiomas | PT (`/`) e ES (`/es/`) |
| Conversão | 3 perguntas (segmento, faturamento, marketplaces) + nome, que abrem `wa.me` com o texto montado. Sem backend |
| Provas | Números por plataforma, cases, depoimentos, logos, tarifas da calculadora e respostas do FAQ ficam **provisórios** (`placeholder: true`, selo "EXEMPLO") até o cliente enviar os reais. Aparecem no dev e nos previews; no build de produção **ficam de fora** (decisão de 2026-11-19, antes o build falhava) |
| Marcas de marketplace | Nos renders entram só a cor de destaque e um motivo abstrato, nunca o logo oficial. O nome aparece em texto HTML |
| Texto | Nunca vai assado no render. Todo texto e número é HTML (permite traduzir e editar sem re-renderizar) |

## Roteiro
| Clipe (`clip`) | Cena Unreal | Conteúdo |
|---|---|---|
| `hero` | Partículas metálicas formam o K e o M; o anel 360 gira e acende | "Sua loja vende. Mas está dando lucro?" + CTA |
| `problema` | **Sem Unreal** (pedido do cliente em 2026-11-19): etiquetas de texto HTML (tarifa, frete, devolução…) saem do caos e se alinham com o scroll. Os quadros renderizados ficam guardados, sem uso (`noFrames`) | Vender ≠ lucrar |
| `mercadolivre` | Estação amarela: caixas em esteira, termômetro | O que fazemos no ML |
| `tiktokshop` | Estação ciano/rosa: telas verticais de live, corações | O que fazemos no TikTok Shop |
| `shein` | Estação P&B: passarela minimalista, cabides | O que fazemos na Shein |
| `shopee` | Estação laranja: sacolas, moedas/cupons em órbita | O que fazemos na Shopee |
| `resultados` | Colunas metálicas sobem e formam um gráfico | +R$ 50 mi, com o anel dividido por plataforma |
| `final` | A câmera recua e o anel 360 se fecha | Mini-diagnóstico |

Sem clipe: Serviços/Método 360, Cases + Depoimentos + Logos, Rodapé.

**Assinatura visual:** o **anel 360** aparece no logo, nos renders, no indicador fixo de progresso (que se fecha ao chegar no diagnóstico) e no gráfico de rosca dos resultados.

## Contrato Unreal → site (atualizado em 2026-11-18 com o redesign colorido)
- O Movie Render Queue exporta PNG com **fundo transparente**, 1200×1200, 30 fps (hero 120 quadros em turntable com loop, demais 96). O site compõe o objeto sobre a cor CSS da seção, para a cor bater exata. O reflexo usa um HDRI na cor da seção, que só aparece no cromado.
- Arquivos: `site/public/frames/<clip>/1x1/0001.webp` (cwebp q82, alpha_q90) e `.../1x1m/` (720 px para celular ou economia de dados; o player carrega só os pares). Gere com `unreal/KM360/Scripts/mobile_frames.py`, que também grava `frames/<clip>/crop.json` (caixa do objeto somando todos os quadros). O player desenha só essa caixa, sem a margem transparente do render; `--obj-y` no CSS alinha o objeto (no desktop os marketplaces ficam no topo).
- (Histórico: o plano inicial previa 16x9/9x16 com fundo renderizado; o player ainda aceita esses formatos.)
- O site conta os quadros no build. Um clipe sem quadros usa o **fallback CSS** (anel + brilho), e esse fallback também serve para `prefers-reduced-motion`.
- O primeiro quadro de cada clipe deve casar com o último do anterior.

## Arquitetura do site
Astro (estático), sem framework de UI e sem dependências além do próprio Astro.
- `src/data/content.ts`: todo o texto PT/ES e os dados, com `placeholder: true` nos itens provisórios.
- `src/components/Page.astro`: a página, recebe `lang`.
- `src/components/Chapter.astro`: bloco sticky com canvas e fallback, conta os quadros em `public/frames`.
- `src/scripts/scroll.ts`: progresso por capítulo (`--p`), desenho dos quadros e anel de progresso.
- Diagnóstico: `<form>` nativo, e um JS monta a URL do `wa.me`.
- Deploy: Vercel (`vercel.json` na raiz, sem configuração no painel). Em produção os itens EXEMPLO são escondidos (`src/data/mode.ts`). Domínio oficial depois, na Hostinger (ver README).

## Qualidade
- Mobile primeiro, com `svh` no sticky e enquadramento 9:16 próprio.
- Foco visível, labels no formulário, canvas com `aria-hidden` e texto sempre no DOM.
- `prefers-reduced-motion`: sem pin, com imagem estática.
- SEO: `hreflang` PT/ES, Open Graph e JSON-LD `ProfessionalService`.
- Verificação: build limpo e checagem no browser em desktop e mobile (scroll, troca de idioma, link do WhatsApp).

## Fora de escopo (por agora)
CRM/banco de leads, blog, Pixel Streaming, cena 3D em tempo real no navegador.
