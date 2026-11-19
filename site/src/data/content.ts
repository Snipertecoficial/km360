// Todo texto e dado do site. Itens com `placeholder: true` aparecem com selo EXEMPLO
// e bloqueiam o build de produção (VERCEL_ENV=production) até serem trocados pelos reais.
import { calc, money, pct, type CalcRaw } from './calc.ts';

export type Lang = 'pt' | 'es';

export const WHATSAPP = '5511988179980';
export const INSTAGRAM = 'klebermarques.assessor';
export const TOTAL_MI = 50; // real: +R$ 50 milhões faturados em marketplaces para clientes

// Cor sólida de cada seção (fundo, tinta). Todas as duplas passam AA.
export const tones = {
  hero: ['#1F4FE0', '#FFFFFF'],
  problema: ['#D62246', '#FFFFFF'],
  resultados: ['#19D27A', '#04331C'],
  metodo: ['#E3E6EB', '#0B1A3A'],
  provas: ['#6A3DF0', '#FFFFFF'],
  final: ['#1F4FE0', '#FFFFFF'],
} as const;

export const marketplaces = [
  { id: 'mercadolivre', name: 'Mercado Livre', accent: '#FFE600', ink: '#2D3277' },
  { id: 'tiktokshop', name: 'TikTok Shop', accent: '#25F4EE', accent2: '#FE2C55', ink: '#0B0B0B' },
  { id: 'shein', name: 'Shein', accent: '#FFFFFF', ink: '#000000' },
  { id: 'shopee', name: 'Shopee', accent: '#EE4D2D', ink: '#2B0A03' },
] as const;

export type MarketplaceId = (typeof marketplaces)[number]['id'];

// Tarifa de referência por canal para a calculadora: comissão (%) e taxa fixa por pedido (R$).
// Provisório: as tarifas mudam e variam por categoria. A KM 360 confere antes de publicar.
export const fees = {
  placeholder: true,
  byMk: {
    mercadolivre: { commission: 14, freight: 6.25 },
    tiktokshop: { commission: 12, freight: 4 },
    shein: { commission: 16, freight: 5 },
    shopee: { commission: 20, freight: 4 },
  } as Record<MarketplaceId, { commission: number; freight: number }>,
};

// Divisão do faturamento por plataforma (%). Provisório até o cliente enviar os números.
export const split = {
  placeholder: true,
  shares: { mercadolivre: 45, shopee: 25, shein: 15, tiktokshop: 15 } as Record<MarketplaceId, number>,
};

const pt = {
  htmlLang: 'pt-BR',
  meta: {
    title: 'KM 360 Assessoria Comercial | Referência no Brás em marketplaces de moda',
    description:
      'Assessoria comercial para lojas de moda do Brás. Custo, preço e equipe no lugar e a loja crescendo no Mercado Livre, TikTok Shop, Shein e Shopee. +R$ 50 milhões faturados em marketplaces para nossos clientes.',
  },
  badge: 'EXEMPLO',
  nav: { label: 'Seções', calc: 'Margem', marketplaces: 'Marketplaces', resultados: 'Resultados', metodo: 'Método', faq: 'Dúvidas', cta: 'Diagnóstico', other: 'ES', otherLabel: 'Ver em espanhol', otherHref: '/es/', menu: 'Menu' },
  ring: { label: 'Ir para o diagnóstico' },
  hero: {
    kicker: 'Assessoria comercial para lojas de moda',
    line1: 'Sua loja vende.',
    line2a: 'Mas está dando ',
    line2b: 'lucro?',
    text: 'A KM 360 coloca custo, preço e equipe no lugar e faz sua loja crescer no Mercado Livre, TikTok Shop, Shein e Shopee. Com margem, não só com volume.',
    cta: 'Fazer diagnóstico grátis',
    cta2: 'Calcular minha margem',
    authority: [
      { big: '+R$ 50 mi', label: 'faturados em marketplaces para nossos clientes' },
      { big: 'Referência no Brás', label: 'em assessoria para atacado e varejo de moda' },
    ],
    drag: 'Arraste para girar 360°',
    objLabel: 'Logo da KM 360 em 3D, girando 360 graus',
  },
  problema: {
    kicker: 'O problema',
    title: 'Vender muito não é o mesmo que lucrar.',
    text: 'No marketplace, cada pedido paga comissão, frete, imposto e anúncio antes de virar lucro. Quem não faz a conta peça por peça descobre o prejuízo no fim do mês.',
    tags: ['tarifa', 'frete', 'devolução', 'anúncio', 'custo', 'margem', 'estoque', 'equipe', 'preço', 'imposto', 'atraso', 'cupom'],
    items: [
      { t: 'Custo que ninguém vê', d: 'Comissão, frete, devolução e anúncio comem a margem pedido por pedido. Na conta de cabeça, nada disso aparece.' },
      { t: 'Preço no chute', d: 'Copiar o preço do vizinho não paga o seu custo. Sem a conta da peça, o prejuízo só aparece quando o dinheiro já saiu.' },
      { t: 'Operação no improviso', d: 'Estoque, equipe e atendimento sem processo travam a loja justo quando as vendas sobem.' },
    ],
  },
  calc: {
    kicker: 'Calculadora de margem',
    title: 'Faça a conta da sua peça.',
    text: 'Coloque os números de uma peça que você vende e veja quanto fica, de verdade, no seu bolso.',
    note: 'Valores de referência. Ajuste para a sua realidade e confira a tarifa da sua categoria.',
    fields: {
      price: 'Preço de venda da peça (R$)',
      cost: 'Custo da peça (R$)',
      commission: 'Comissão do marketplace (%)',
      freight: 'Frete/tarifa fixa por pedido (R$)',
      tax: 'Imposto (%)',
      ads: 'Anúncios (% da venda)',
      orders: 'Pedidos por mês',
    },
    receipt: 'Sua simulação',
    head: 'Lucro na cabeça, por peça',
    real: 'Lucro real, por peça',
    margin: 'Margem real',
    leakA: 'Todo mês,',
    leakB: 'ficam pelo caminho.',
    month: 'Lucro real no mês',
    alert: 'Você está pagando para vender.',
    loss: 'Prejuízo no mês',
    invalid: 'Corrija os campos marcados para ver a conta.',
    errors: {
      empty: 'Digite um número.',
      negative: 'Use um valor igual ou maior que zero.',
      zero: 'O preço precisa ser maior que zero.',
      integer: 'Use um número inteiro de pedidos.',
    },
    cta: 'Quero recuperar essa margem',
    ctaNote: 'A simulação vai junto no seu diagnóstico.',
    channel: 'Onde essa peça é vendida?',
    manual: 'Outro / manual',
    feesNote: 'Escolha o canal e a comissão e o frete entram com a tarifa de referência dele. Confira a da sua categoria.',
    compareTitle: 'A mesma peça nos 4 canais',
    compareText: 'Mesmo preço, custo, imposto e anúncio. Só muda a tarifa de cada marketplace.',
    best: 'Mais lucro',
    perPiece: 'por peça',
  },
  mkIntro: {
    kicker: 'Onde a gente faz acontecer',
    title: 'Quatro marketplaces. Uma estratégia.',
    text: 'Cada canal tem regra, tarifa e público diferentes. A KM 360 trabalha os quatro com a mesma conta: margem primeiro, escala depois.',
  },
  mkKicker: 'Marketplace',
  mk: {
    mercadolivre: {
      lead: 'Reputação verde, anúncio no topo e frete que não come a margem.',
      points: [
        'Título, ficha técnica e fotos pensados para a busca do Mercado Livre',
        'Reputação e termômetro no verde, sem atraso e sem reclamação acumulada',
        'Full e Mercado Ads só onde a margem da peça aguenta',
      ],
    },
    tiktokshop: {
      lead: 'Moda vende quando aparece. A gente transforma vídeo e live em pedido.',
      points: [
        'Vitrine e catálogo prontos para vender sem sair do app',
        'Rotina de lives, vídeos curtos e afiliados que gira o estoque parado',
        'Campanha medida por custo por pedido, não por visualização',
      ],
    },
    shein: {
      lead: 'Sua coleção na vitrine de moda que o cliente já abre todo dia.',
      points: [
        'Cadastro, grade e fotos no padrão que a Shein aprova',
        'Preço e prazo de postagem alinhados à capacidade da sua produção',
        'Fluxo de pedidos sem atraso, sem multa e sem cancelamento',
      ],
    },
    shopee: {
      lead: 'Campanha, cupom e frete grátis no ritmo das datas que mais vendem.',
      points: [
        'Calendário 9.9, 11.11 e 12.12 planejado com estoque e preço antes da data',
        'Cupom, Shopee Ads e frete grátis calculados para não queimar a margem',
        'Envio e atendimento que mantêm a nota da loja lá em cima',
      ],
    },
  },
  mkStat: 'faturados por clientes nesta plataforma',
  traps: {
    title: 'O erro que mais vemos aqui',
    mercadolivre: 'Anúncio bom com envio atrasado. Poucos atrasos deixam a reputação amarela e o anúncio cai na busca, mesmo com o preço certo.',
    tiktokshop: 'Fazer live sem estoque separado. O vídeo bomba, o pedido entra e a loja cancela por falta de peça, e a conta perde alcance.',
    shein: 'Postar fora do prazo. Cada atraso vira multa ou cancelamento, e o lucro da coleção vai embora na penalidade.',
    shopee: 'Entrar em toda campanha com cupom e frete grátis sem fazer a conta. A loja vende muito na data e fecha o mês no prejuízo.',
  },
  resultados: {
    kicker: 'Resultado é o nosso foco',
    prefix: '+R$',
    unit: 'milhões',
    title: 'faturados em marketplaces para as lojas atendidas pela KM 360.',
    splitTitle: 'Onde esse faturamento aconteceu',
  },
  metodo: {
    kicker: 'Método 360',
    title: 'Visão, organização e resultado. Nessa ordem.',
    steps: [
      { t: 'Visão', d: 'Diagnóstico de vendas, custos e margem por canal. Você enxerga onde ganha e onde perde.' },
      { t: 'Organização', d: 'Processo, equipe e preço no lugar. A loja para de depender de improviso.' },
      { t: 'Resultado', d: 'Escala nos marketplaces com meta, acompanhamento e números na mesa todo mês.' },
    ],
    servicesTitle: 'O que entra na volta completa',
    services: [
      { t: 'Organização comercial', d: 'Processo de venda, metas e rotina da loja no papel e na prática.' },
      { t: 'Equipe e vendas', d: 'Quem faz o quê, como atende e como é cobrado. Treino junto com a equipe.' },
      { t: 'Custos e margem', d: 'Custo real de cada peça, preço por canal e margem mínima definida.' },
      { t: 'Marketplace & E-commerce', d: 'Mercado Livre, TikTok Shop, Shein e Shopee operando com a mesma conta.' },
      { t: 'Atacado & Varejo', d: 'Preço e atendimento certos para quem compra uma peça ou cem.' },
    ],
  },
  provas: {
    kicker: 'Provas',
    casesTitle: 'Antes e depois',
    before: 'Antes',
    after: 'Depois',
    cases: [
      { placeholder: true, seg: 'Moda feminina · Atacado', where: 'Mercado Livre + Shopee', before: 'R$ 80 mil/mês', after: 'R$ 310 mil/mês' },
      { placeholder: true, seg: 'Jeans · Varejo', where: 'Shein', before: 'R$ 0', after: 'R$ 120 mil/mês' },
      { placeholder: true, seg: 'Moda infantil · Atacado', where: 'TikTok Shop', before: 'R$ 25 mil/mês', after: 'R$ 140 mil/mês' },
    ],
    testimonialsTitle: 'Quem já deu a volta',
    testimonials: [
      { placeholder: true, quote: 'A gente vendia bem e não sobrava nada. Depois do diagnóstico, refiz o preço de tudo e o lucro apareceu no primeiro mês.', who: 'Lojista de moda feminina, Brás' },
      { placeholder: true, quote: 'Entrar na Shopee sem saber a margem era loteria. Hoje cada campanha tem meta e eu sei quanto ganho por pedido.', who: 'Atacadista de moda praia, Brás' },
      { placeholder: true, quote: 'A equipe passou a ter processo. Parou o retrabalho e o atendimento ficou no padrão que o marketplace cobra.', who: 'Loja de moda masculina, Brás' },
    ],
    logosTitle: 'Lojas que confiam na KM 360',
    logos: Array.from({ length: 6 }, () => ({ placeholder: true, label: 'Logo do cliente' })),
  },
  // Respostas são afirmações sobre a KM 360: provisórias até o cliente confirmar.
  faq: {
    kicker: 'Antes de chamar',
    title: 'O que todo lojista pergunta.',
    items: [
      { placeholder: true, q: 'Vocês atendem lojas fora do Brás?', a: 'Sim. A KM 360 nasceu no Brás, e o acompanhamento é feito por reunião online e WhatsApp com lojas de todo o Brasil.' },
      { placeholder: true, q: 'Vocês operam minha conta ou ensinam minha equipe?', a: 'Depende da loja. A KM 360 organiza o processo e treina a equipe e, quando faz sentido, opera junto até a rotina andar sozinha.' },
      { placeholder: true, q: 'Em quanto tempo aparece resultado?', a: 'A margem costuma melhorar já no primeiro mês, porque preço e custo são ajustados logo no começo. A escala de vendas leva de 3 a 6 meses, conforme o canal e o estoque.' },
      { placeholder: true, q: 'Preciso já vender em marketplace?', a: 'Não. Se a loja ainda não vende, o diagnóstico mostra por qual canal começar e com qual preço.' },
      { placeholder: true, q: 'Quanto custa a assessoria?', a: 'Depende do tamanho da loja e dos canais. O diagnóstico é grátis, e é nele que você recebe a proposta com o valor.' },
    ],
  },
  final: {
    kicker: 'Volta completa',
    title: 'Agora é a sua loja.',
    text: 'Responda 3 perguntas e receba o diagnóstico direto no WhatsApp. É grátis e você fala com a KM 360, não com robô.',
  },
  diag: {
    title: 'Diagnóstico grátis em 30 segundos',
    scarcity: 'Atendemos poucas lojas novas por mês para acompanhar cada uma de perto.',
    q1: { label: 'Qual o segmento da sua loja?', options: ['Moda feminina', 'Moda masculina', 'Moda infantil', 'Plus size', 'Jeans', 'Moda praia/fitness', 'Outro'] },
    q2: { label: 'Quanto a loja fatura por mês?', options: ['Até R$ 50 mil', 'R$ 50 mil a 200 mil', 'R$ 200 mil a 1 milhão', 'Acima de R$ 1 milhão'] },
    q3: { label: 'Onde você já vende?', none: 'Ainda não vendo em marketplace' },
    name: { label: 'Seu nome', placeholder: 'Como podemos te chamar?' },
    sim: 'Enviar minha simulação junto',
    submit: 'Enviar no WhatsApp',
    note: 'Abre o WhatsApp com suas respostas. Nada fica salvo neste site.',
    error: 'Responda o segmento, o faturamento e onde vende para continuar.',
    msg: 'Olá, KM 360! Sou {name} e quero meu diagnóstico.\n• Segmento: {seg}\n• Faturamento mensal: {fat}\n• Onde vendo: {mkt}',
    simMsg: '\n\nMinha simulação de margem:\n• Preço da peça: {price}\n• Custo da peça: {cost}\n• Lucro real por peça: {real}\n• Margem real: {margin}',
    anon: 'lojista',
  },
  footer: {
    tagline: 'Do Brás para o Brasil.',
    place: 'Brás · São Paulo/SP',
    whatsapp: 'WhatsApp (11) 98817-9980',
    rights: '© 2026 KM 360 Assessoria Comercial',
    unreal: 'Objetos 3D renderizados em Unreal Engine.',
  },
};

export type Copy = typeof pt;

const es: Copy = {
  htmlLang: 'es',
  meta: {
    title: 'KM 360 Asesoría Comercial | Referencia en el Brás en marketplaces de moda',
    description:
      'Asesoría comercial para tiendas de moda del Brás. Costos, precios y equipo en orden y la tienda creciendo en Mercado Livre, TikTok Shop, Shein y Shopee. +R$ 50 millones facturados en marketplaces para nuestros clientes.',
  },
  badge: 'EJEMPLO',
  nav: { label: 'Secciones', calc: 'Margen', marketplaces: 'Marketplaces', resultados: 'Resultados', metodo: 'Método', faq: 'Dudas', cta: 'Diagnóstico', other: 'PT', otherLabel: 'Ver en portugués', otherHref: '/', menu: 'Menú' },
  ring: { label: 'Ir al diagnóstico' },
  hero: {
    kicker: 'Asesoría comercial para tiendas de moda',
    line1: 'Tu tienda vende.',
    line2a: '¿Pero te está dando ',
    line2b: 'ganancia?',
    text: 'KM 360 pone en orden costos, precios y equipo y hace crecer tu tienda en Mercado Livre, TikTok Shop, Shein y Shopee. Con margen, no solo con volumen.',
    cta: 'Hacer diagnóstico gratis',
    cta2: 'Calcular mi margen',
    authority: [
      { big: '+R$ 50 mi', label: 'facturados en marketplaces para nuestros clientes' },
      { big: 'Referencia en el Brás', label: 'en asesoría para moda mayorista y minorista' },
    ],
    drag: 'Arrastra para girar 360°',
    objLabel: 'Logo de KM 360 en 3D, girando 360 grados',
  },
  problema: {
    kicker: 'El problema',
    title: 'Vender mucho no es lo mismo que ganar.',
    text: 'En el marketplace, cada pedido paga comisión, envío, impuesto y anuncio antes de volverse ganancia. Quien no hace la cuenta prenda por prenda descubre la pérdida a fin de mes.',
    tags: ['comisión', 'envío', 'devolución', 'anuncio', 'costo', 'margen', 'stock', 'equipo', 'precio', 'impuesto', 'atraso', 'cupón'],
    items: [
      { t: 'Costos que nadie ve', d: 'Comisión, envío, devoluciones y anuncios se comen el margen pedido a pedido. En la cuenta de memoria, nada de eso aparece.' },
      { t: 'Precio a ojo', d: 'Copiar el precio del vecino no paga tu costo. Sin la cuenta de la prenda, la pérdida aparece cuando el dinero ya salió.' },
      { t: 'Operación improvisada', d: 'Stock, equipo y atención sin procesos frenan la tienda justo cuando las ventas suben.' },
    ],
  },
  calc: {
    kicker: 'Calculadora de margen',
    title: 'Haz la cuenta de tu prenda.',
    text: 'Pon los números de una prenda que vendes y mira cuánto te queda, de verdad, en el bolsillo.',
    note: 'Valores de referencia. Ajústalos a tu realidad y revisa la tarifa de tu categoría.',
    fields: {
      price: 'Precio de venta de la prenda (R$)',
      cost: 'Costo de la prenda (R$)',
      commission: 'Comisión del marketplace (%)',
      freight: 'Envío/tarifa fija por pedido (R$)',
      tax: 'Impuesto (%)',
      ads: 'Anuncios (% de la venta)',
      orders: 'Pedidos por mes',
    },
    receipt: 'Tu simulación',
    head: 'Ganancia de memoria, por prenda',
    real: 'Ganancia real, por prenda',
    margin: 'Margen real',
    leakA: 'Cada mes,',
    leakB: 'se quedan en el camino.',
    month: 'Ganancia real del mes',
    alert: 'Estás pagando para vender.',
    loss: 'Pérdida del mes',
    invalid: 'Corrige los campos marcados para ver la cuenta.',
    errors: {
      empty: 'Escribe un número.',
      negative: 'Usa un valor igual o mayor que cero.',
      zero: 'El precio tiene que ser mayor que cero.',
      integer: 'Usa un número entero de pedidos.',
    },
    cta: 'Quiero recuperar ese margen',
    ctaNote: 'La simulación va junto con tu diagnóstico.',
    channel: '¿Dónde se vende esta prenda?',
    manual: 'Otro / manual',
    feesNote: 'Elige el canal y la comisión y el envío se cargan con su tarifa de referencia. Revisa la de tu categoría.',
    compareTitle: 'La misma prenda en los 4 canales',
    compareText: 'Mismo precio, costo, impuesto y anuncio. Solo cambia la tarifa de cada marketplace.',
    best: 'Más ganancia',
    perPiece: 'por prenda',
  },
  mkIntro: {
    kicker: 'Donde lo hacemos realidad',
    title: 'Cuatro marketplaces. Una estrategia.',
    text: 'Cada canal tiene reglas, tarifas y público distintos. KM 360 trabaja los cuatro con la misma cuenta: primero el margen, después la escala.',
  },
  mkKicker: 'Marketplace',
  mk: {
    mercadolivre: {
      lead: 'Reputación verde, anuncio arriba y envío que no se come el margen.',
      points: [
        'Título, ficha técnica y fotos pensados para el buscador de Mercado Livre',
        'Reputación y termómetro en verde, sin atrasos ni reclamos acumulados',
        'Full y Mercado Ads solo donde el margen de la prenda lo aguanta',
      ],
    },
    tiktokshop: {
      lead: 'La moda vende cuando se ve. Convertimos videos y lives en pedidos.',
      points: [
        'Vitrina y catálogo listos para vender sin salir de la app',
        'Rutina de lives, videos cortos y afiliados que mueve el stock parado',
        'Campañas medidas por costo por pedido, no por visualizaciones',
      ],
    },
    shein: {
      lead: 'Tu colección en la vitrina de moda que el cliente abre todos los días.',
      points: [
        'Alta de productos, tallas y fotos con el estándar que Shein aprueba',
        'Precio y plazo de despacho alineados con la capacidad de tu producción',
        'Flujo de pedidos sin atrasos, sin multas y sin cancelaciones',
      ],
    },
    shopee: {
      lead: 'Campañas, cupones y envío gratis al ritmo de las fechas que más venden.',
      points: [
        'Calendario 9.9, 11.11 y 12.12 planificado con stock y precio antes de la fecha',
        'Cupones, Shopee Ads y envío gratis calculados para no quemar el margen',
        'Envíos y atención que mantienen la calificación de la tienda arriba',
      ],
    },
  },
  mkStat: 'facturados por clientes en esta plataforma',
  traps: {
    title: 'El error que más vemos aquí',
    mercadolivre: 'Buen anuncio con envío atrasado. Pocos atrasos ponen la reputación en amarillo y el anuncio cae en el buscador, aunque el precio sea correcto.',
    tiktokshop: 'Hacer lives sin stock separado. El video explota, entra el pedido y la tienda cancela por falta de prenda, y la cuenta pierde alcance.',
    shein: 'Despachar fuera de plazo. Cada atraso se vuelve multa o cancelación, y la ganancia de la colección se va en penalidades.',
    shopee: 'Entrar a todas las campañas con cupón y envío gratis sin hacer la cuenta. La tienda vende mucho en la fecha y cierra el mes con pérdida.',
  },
  resultados: {
    kicker: 'El resultado es nuestro foco',
    prefix: '+R$',
    unit: 'millones',
    title: 'facturados en marketplaces por las tiendas asesoradas por KM 360.',
    splitTitle: 'Dónde ocurrió esa facturación',
  },
  metodo: {
    kicker: 'Método 360',
    title: 'Visión, organización y resultado. En ese orden.',
    steps: [
      { t: 'Visión', d: 'Diagnóstico de ventas, costos y margen por canal. Ves dónde ganas y dónde pierdes.' },
      { t: 'Organización', d: 'Procesos, equipo y precios en su lugar. La tienda deja de depender de la improvisación.' },
      { t: 'Resultado', d: 'Escala en los marketplaces con metas, seguimiento y números sobre la mesa cada mes.' },
    ],
    servicesTitle: 'Qué incluye la vuelta completa',
    services: [
      { t: 'Organización comercial', d: 'Proceso de venta, metas y rutina de la tienda en el papel y en la práctica.' },
      { t: 'Equipo y ventas', d: 'Quién hace qué, cómo atiende y cómo se mide. Capacitación junto al equipo.' },
      { t: 'Costos y margen', d: 'Costo real de cada prenda, precio por canal y margen mínimo definido.' },
      { t: 'Marketplace & E-commerce', d: 'Mercado Livre, TikTok Shop, Shein y Shopee operando con la misma cuenta.' },
      { t: 'Mayorista & Minorista', d: 'Precio y atención correctos para quien compra una prenda o cien.' },
    ],
  },
  provas: {
    kicker: 'Pruebas',
    casesTitle: 'Antes y después',
    before: 'Antes',
    after: 'Después',
    cases: [
      { placeholder: true, seg: 'Moda femenina · Mayorista', where: 'Mercado Livre + Shopee', before: 'R$ 80 mil/mes', after: 'R$ 310 mil/mes' },
      { placeholder: true, seg: 'Jeans · Minorista', where: 'Shein', before: 'R$ 0', after: 'R$ 120 mil/mes' },
      { placeholder: true, seg: 'Moda infantil · Mayorista', where: 'TikTok Shop', before: 'R$ 25 mil/mes', after: 'R$ 140 mil/mes' },
    ],
    testimonialsTitle: 'Quienes ya dieron la vuelta',
    testimonials: [
      { placeholder: true, quote: 'Vendíamos bien y no quedaba nada. Después del diagnóstico rehice los precios y la ganancia apareció en el primer mes.', who: 'Tienda de moda femenina, Brás' },
      { placeholder: true, quote: 'Entrar a Shopee sin conocer el margen era lotería. Hoy cada campaña tiene meta y sé cuánto gano por pedido.', who: 'Mayorista de moda de playa, Brás' },
      { placeholder: true, quote: 'El equipo empezó a tener procesos. Se acabó el retrabajo y la atención quedó al nivel que exige el marketplace.', who: 'Tienda de moda masculina, Brás' },
    ],
    logosTitle: 'Tiendas que confían en KM 360',
    logos: Array.from({ length: 6 }, () => ({ placeholder: true, label: 'Logo del cliente' })),
  },
  faq: {
    kicker: 'Antes de escribir',
    title: 'Lo que todo comerciante pregunta.',
    items: [
      { placeholder: true, q: '¿Atienden tiendas fuera del Brás?', a: 'Sí. KM 360 nació en el Brás, y el seguimiento se hace por reunión online y WhatsApp con tiendas de todo Brasil.' },
      { placeholder: true, q: '¿Ustedes operan mi cuenta o capacitan a mi equipo?', a: 'Depende de la tienda. KM 360 organiza el proceso y capacita al equipo y, cuando tiene sentido, opera en conjunto hasta que la rutina funcione sola.' },
      { placeholder: true, q: '¿En cuánto tiempo se ven resultados?', a: 'El margen suele mejorar ya en el primer mes, porque precio y costo se ajustan desde el inicio. Escalar las ventas lleva de 3 a 6 meses, según el canal y el stock.' },
      { placeholder: true, q: '¿Necesito vender ya en marketplaces?', a: 'No. Si la tienda todavía no vende, el diagnóstico muestra por qué canal empezar y con qué precio.' },
      { placeholder: true, q: '¿Cuánto cuesta la asesoría?', a: 'Depende del tamaño de la tienda y de los canales. El diagnóstico es gratis y ahí recibes la propuesta con el valor.' },
    ],
  },
  final: {
    kicker: 'Vuelta completa',
    title: 'Ahora es tu tienda.',
    text: 'Responde 3 preguntas y recibe el diagnóstico directo por WhatsApp. Es gratis y hablas con KM 360, no con un robot.',
  },
  diag: {
    title: 'Diagnóstico gratis en 30 segundos',
    scarcity: 'Atendemos pocas tiendas nuevas por mes para acompañar cada una de cerca.',
    q1: { label: '¿Cuál es el segmento de tu tienda?', options: ['Moda femenina', 'Moda masculina', 'Moda infantil', 'Talles grandes', 'Jeans', 'Moda de playa/fitness', 'Otro'] },
    q2: { label: '¿Cuánto factura la tienda por mes?', options: ['Hasta R$ 50 mil', 'R$ 50 mil a 200 mil', 'R$ 200 mil a 1 millón', 'Más de R$ 1 millón'] },
    q3: { label: '¿Dónde ya vendes?', none: 'Todavía no vendo en marketplaces' },
    name: { label: 'Tu nombre', placeholder: '¿Cómo te llamamos?' },
    sim: 'Enviar mi simulación junto',
    submit: 'Enviar por WhatsApp',
    note: 'Abre WhatsApp con tus respuestas. Nada queda guardado en este sitio.',
    error: 'Responde el segmento, la facturación y dónde vendes para continuar.',
    msg: '¡Hola, KM 360! Soy {name} y quiero mi diagnóstico.\n• Segmento: {seg}\n• Facturación mensual: {fat}\n• Dónde vendo: {mkt}',
    simMsg: '\n\nMi simulación de margen:\n• Precio de la prenda: {price}\n• Costo de la prenda: {cost}\n• Ganancia real por prenda: {real}\n• Margen real: {margin}',
    anon: 'comerciante',
  },
  footer: {
    tagline: 'Del Brás para todo Brasil.',
    place: 'Brás · São Paulo/SP',
    whatsapp: 'WhatsApp +55 11 98817-9980',
    rights: '© 2026 KM 360 Asesoría Comercial',
    unreal: 'Objetos 3D renderizados en Unreal Engine.',
  },
};

export const copy: Record<Lang, Copy> = { pt, es };

/** true se existir qualquer `placeholder: true` em `value` (busca profunda). */
export function hasPlaceholders(value: unknown): boolean {
  if (!value || typeof value !== 'object') return false;
  if ((value as { placeholder?: unknown }).placeholder === true) return true;
  return Object.values(value).some(hasPlaceholders);
}

/** Resumo da calculadora anexado ao diagnóstico (margin em fração: 0.25 = 25%). */
export type Sim = { price: number; cost: number; real: number; margin: number };
export type Answers = { name?: string; seg?: string; fat?: string; mkt: string[]; sim?: Sim; origin?: string };

/** Monta o link wa.me com as respostas do diagnóstico, ou null se faltar resposta obrigatória. */
export function whatsappUrl(lang: Lang, a: Answers): string | null {
  if (!a.seg || !a.fat || a.mkt.length === 0) return null;
  const { diag: d, htmlLang: loc } = copy[lang];
  let text = d.msg
    .replace('{name}', a.name?.trim() || d.anon)
    .replace('{seg}', a.seg)
    .replace('{fat}', a.fat)
    .replace('{mkt}', a.mkt.join(', '));
  if (a.sim) {
    text += d.simMsg
      .replace('{price}', money(loc, a.sim.price))
      .replace('{cost}', money(loc, a.sim.cost))
      .replace('{real}', money(loc, a.sim.real))
      .replace('{margin}', pct(loc, a.sim.margin));
  }
  if (a.origin) text += `\n\nref: ${a.origin}`; // de qual campanha/anúncio veio o contato
  return `https://wa.me/${WHATSAPP}?text=${encodeURIComponent(text)}`;
}

/** Origem do contato pela URL de entrada: UTMs; sem UTM, o clique de anúncio vira meta/google/tiktok. '' se não houver. */
export function parseOrigin(search: string): string {
  const q = new URLSearchParams(search);
  const utm = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content'].map((k) => q.get(k)?.trim()).filter(Boolean);
  const click = q.has('fbclid') ? 'meta' : q.has('gclid') ? 'google' : q.has('ttclid') ? 'tiktok' : '';
  return (utm.length ? utm.join(' · ') : click).replace(/\s+/g, ' ').slice(0, 120);
}

/** A mesma peça em cada canal: troca só comissão e frete pela tarifa de referência do marketplace. */
export function compareChannels(r: CalcRaw) {
  return marketplaces.map((m) => ({ ...m, res: calc({ ...r, ...fees.byMk[m.id] }) }));
}
