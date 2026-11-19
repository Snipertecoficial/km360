// Checagem rápida: node src/data/content.check.ts
import assert from 'node:assert/strict';
import { copy, split, fees, hasPlaceholders, whatsappUrl, parseOrigin, compareChannels } from './content.ts';
import { calc, CALC_FIELDS, type CalcRaw } from './calc.ts';

// Provisórios detectados (trava de produção depende disso).
assert.equal(hasPlaceholders([copy.pt, split]), true);
assert.equal(hasPlaceholders({ a: [{ b: { placeholder: false } }] }), false);
assert.equal(hasPlaceholders({ a: [{ b: { placeholder: true } }] }), true);

// Diagnóstico exige segmento, faturamento e ao menos um canal.
assert.equal(whatsappUrl('pt', { seg: 'Jeans', fat: 'Até R$ 50 mil', mkt: [] }), null);
assert.equal(whatsappUrl('pt', { seg: 'Jeans', mkt: ['Shopee'] }), null);

const url = whatsappUrl('pt', { name: '  Ana ', seg: 'Jeans', fat: 'Até R$ 50 mil', mkt: ['Shopee', 'Shein'] })!;
assert.ok(url.startsWith('https://wa.me/5511988179980?text='));
const text = decodeURIComponent(url.split('text=')[1]);
assert.match(text, /^Olá, KM 360! Sou Ana e/);
assert.match(text, /Onde vendo: Shopee, Shein/);

// Sem nome usa o tratamento padrão; ES usa o texto em espanhol.
assert.match(decodeURIComponent(whatsappUrl('es', { seg: 'Jeans', fat: 'x', mkt: ['Shein'] })!), /Soy comerciante/);

// PT e ES têm as mesmas chaves de marketplace.
assert.deepEqual(Object.keys(copy.es.mk), Object.keys(copy.pt.mk));

// PT e ES têm os mesmos campos na calculadora.
assert.deepEqual(Object.keys(copy.es.calc.fields), Object.keys(copy.pt.calc.fields));

// Calculadora: valores-padrão dão lucro positivo.
const base = Object.fromEntries(CALC_FIELDS.map((f) => [f.key, f.value])) as CalcRaw;
const ok = calc(base);
assert.ok(ok.ok);
const near = (a: number, b: number) => assert.ok(Math.abs(a - b) < 1e-6, `${a} != ${b}`);
near(ok.head, 54.9);
near(ok.real, 89.9 - 35 - 89.9 * 0.27 - 8); // 22,627
near(ok.margin, ok.real / 89.9);
near(ok.leak, (54.9 - ok.real) * 500); // 16.136,50
near(ok.month, ok.real * 500);
assert.equal(ok.loss, false);

// Prejuízo: taxas maiores que a margem.
const bad = calc({ ...base, price: 50, commission: 20, ads: 10 });
assert.ok(bad.ok && bad.loss && bad.real < 0);
near(bad.ok ? bad.real : 0, 50 - 35 - 50 * 0.36 - 8); // -11

// Entradas inválidas: vazio, negativo, preço zero, pedidos quebrados.
const inv = calc({ ...base, price: null, cost: -1, orders: 2.5 });
assert.ok(!inv.ok);
assert.deepEqual(inv.errors, { price: 'empty', cost: 'negative', orders: 'integer' });
const zero = calc({ ...base, price: 0, freight: NaN });
assert.ok(!zero.ok && zero.errors.price === 'zero' && zero.errors.freight === 'empty');

// Simulação vai anexada ao WhatsApp, formatada em BRL.
const sim = { price: 89.9, cost: 35, real: ok.real, margin: ok.margin };
const withSim = decodeURIComponent(whatsappUrl('pt', { seg: 'Jeans', fat: 'x', mkt: ['Shein'], sim })!.split('text=')[1]);
assert.match(withSim, /Preço da peça: R\$\s89,90/);
assert.match(withSim, /Lucro real por peça: R\$\s22,63/);
assert.match(withSim, /Margem real: 25,2\s?%/);
const esSim = decodeURIComponent(whatsappUrl('es', { seg: 'Jeans', fat: 'x', mkt: ['Shein'], sim })!);
assert.match(esSim, /Ganancia real por prenda: 22,63\sR\$/);
assert.doesNotMatch(decodeURIComponent(url), /simulação/);

// Tarifas e respostas do FAQ são provisórias (travam produção).
assert.equal(hasPlaceholders(fees), true);
assert.equal(hasPlaceholders(copy.pt.faq), true);
assert.equal(copy.es.faq.items.length, copy.pt.faq.items.length);
assert.deepEqual(Object.keys(copy.es.traps), Object.keys(copy.pt.traps));

// Comparativo: mesma peça, só comissão e frete mudam por canal.
const cmp = compareChannels(base);
assert.deepEqual(cmp.map((c) => c.id), ['mercadolivre', 'tiktokshop', 'shein', 'shopee']);
const ml = cmp[0].res;
assert.ok(ml.ok);
near(ml.ok ? ml.real : 0, 89.9 - 35 - 89.9 * (fees.byMk.mercadolivre.commission + 6 + 5) / 100 - fees.byMk.mercadolivre.freight);
assert.ok(!compareChannels({ ...base, price: null })[0].res.ok);

// Origem do contato: UTMs em ordem; sem UTM, o clique do anúncio; nada vira ''.
assert.equal(parseOrigin('?utm_source=meta&utm_medium=cpc&utm_campaign=bras-nov'), 'meta · cpc · bras-nov');
assert.equal(parseOrigin('?fbclid=abc'), 'meta');
assert.equal(parseOrigin('?gclid=x&foo=1'), 'google');
assert.equal(parseOrigin(''), '');
assert.equal(parseOrigin('?utm_source=a%0Ab').includes('\n'), false);
assert.equal(parseOrigin(`?utm_campaign=${'x'.repeat(300)}`).length, 120);
const withRef = decodeURIComponent(whatsappUrl('pt', { seg: 'Jeans', fat: 'x', mkt: ['Shein'], origin: 'meta · cpc' })!);
assert.match(withRef, /\n\nref: meta · cpc$/);
assert.doesNotMatch(decodeURIComponent(url), /ref:/);

console.log('content.check: ok');
