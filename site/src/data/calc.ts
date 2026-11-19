// Calculadora de margem por peça. Lógica pura (sem DOM), usada no site e em content.check.ts.

export type CalcKey = 'price' | 'cost' | 'commission' | 'freight' | 'tax' | 'ads' | 'orders';

/** Campos na ordem da tela. kind: money (R$), pct (range 0..max), int (inteiro). */
export const CALC_FIELDS: { key: CalcKey; kind: 'money' | 'pct' | 'int'; value: number; max?: number }[] = [
  { key: 'price', kind: 'money', value: 89.9 },
  { key: 'cost', kind: 'money', value: 35 },
  { key: 'commission', kind: 'pct', value: 16, max: 40 },
  { key: 'freight', kind: 'money', value: 8 },
  { key: 'tax', kind: 'pct', value: 6, max: 30 },
  { key: 'ads', kind: 'pct', value: 5, max: 30 },
  { key: 'orders', kind: 'int', value: 500 },
];

export type CalcError = 'empty' | 'negative' | 'zero' | 'integer';
export type CalcRaw = Record<CalcKey, number | null>;
export type CalcResult =
  | { ok: false; errors: Partial<Record<CalcKey, CalcError>> }
  | {
      ok: true;
      head: number; // lucro "na cabeça" por peça
      real: number; // lucro real por peça
      margin: number; // margem real (fração)
      leak: number; // quanto fica pelo caminho no mês
      month: number; // lucro real no mês (negativo = prejuízo)
      loss: boolean;
    };

export function calc(r: CalcRaw): CalcResult {
  const errors: Partial<Record<CalcKey, CalcError>> = {};
  for (const { key } of CALC_FIELDS) {
    const v = r[key];
    if (v === null || !Number.isFinite(v)) errors[key] = 'empty';
    else if (v < 0) errors[key] = 'negative';
    else if (key === 'price' && v === 0) errors[key] = 'zero';
    else if (key === 'orders' && !Number.isInteger(v)) errors[key] = 'integer';
  }
  if (Object.keys(errors).length) return { ok: false, errors };

  const { price, cost, commission, freight, tax, ads, orders } = r as Record<CalcKey, number>;
  const head = price - cost;
  const real = price - cost - (price * (commission + tax + ads)) / 100 - freight;
  return { ok: true, head, real, margin: real / price, leak: (head - real) * orders, month: real * orders, loss: real <= 0 };
}

export const money = (locale: string, n: number) =>
  new Intl.NumberFormat(locale, { style: 'currency', currency: 'BRL', currencyDisplay: 'narrowSymbol' }).format(n);
export const pct = (locale: string, n: number) =>
  new Intl.NumberFormat(locale, { style: 'percent', minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(n);
