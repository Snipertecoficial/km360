// Progresso de scroll por capítulo (--p de 0 a 1), desenho dos quadros Unreal no canvas,
// turntable do hero, anel 360 fixo (--page-p) e a cor de cada seção despejada a partir do anel.
// Sem dependências.

type Ratio = '1x1' | '1x1m' | '16x9' | '9x16';
type Clip = {
  el: HTMLElement;
  canvas: HTMLCanvasElement | null;
  ratio: Ratio;
  n: number;
  imgs: (HTMLImageElement | undefined)[];
  loading: boolean;
  want: number; // quadro pedido
  last: number; // quadro desenhado
  tt: boolean; // turntable: o quadro vem do arraste, não do scroll
  crop: number[]; // caixa do objeto no quadro (0..1): x, y, w, h
  ay: number; // alinhamento vertical do objeto na área (0 topo, .5 centro, 1 base), de --obj-y
  pin: boolean; // palco preso na tela (sticky); no celular só o hero
};

const pinned = (el: HTMLElement) => getComputedStyle(el.querySelector('.chapter-stage')!).position === 'sticky';

const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const portrait = matchMedia('(max-aspect-ratio: 1/1)');
const root = document.documentElement;
// Celular ou economia de dados: quadros de 720 px (1x1m) e só os pares; o desenho usa o vizinho mais próximo.
const lite =
  matchMedia('(max-width: 700px)').matches ||
  (navigator as Navigator & { connection?: { saveData?: boolean } }).connection?.saveData === true;

const clips: Clip[] = [...document.querySelectorAll<HTMLElement>('.chapter')].map((el) => {
  const d = el.dataset;
  const f11 = Number(d.f11), f169 = Number(d.f169), f916 = Number(d.f916);
  // 1x1 preferido (1x1m no modo leve, se existir completo); senão o enquadramento da tela, senão o outro.
  const [ratio, n]: [Ratio, number] = f11
    ? [lite && Number(d.f11m) === f11 ? '1x1m' : '1x1', f11]
    : portrait.matches
      ? f916 ? ['9x16', f916] : ['16x9', f169]
      : f169 ? ['16x9', f169] : ['9x16', f916];
  const tt = !!el.querySelector('[data-turntable]');
  const crop = d.crop ? d.crop.split(',').map(Number) : [0, 0, 1, 1];
  return { el, canvas: el.querySelector('canvas'), ratio, n, imgs: new Array(n), loading: false, want: 0, last: -1, tt, crop, ay: 0.5, pin: pinned(el) };
});

// Carrega a cada 8 quadros primeiro (scrub funciona cedo) e depois preenche o resto.
function load(c: Clip) {
  if (c.loading || !c.n) return;
  c.loading = true;
  const order = [...Array(c.n).keys()]
    .filter((i) => !lite || i % 2 === 0)
    .sort((a, b) => Number(a % 8 !== 0) - Number(b % 8 !== 0));
  let next = 0;
  const pump = () => {
    if (next >= order.length) return;
    const i = order[next++];
    const img = new Image();
    img.decoding = 'async';
    img.src = `/frames/${c.el.dataset.clip}/${c.ratio}/${String(i + 1).padStart(4, '0')}.webp`;
    img.onload = () => {
      c.imgs[i] = img;
      if (c.last === -1 || Math.abs(i - c.want) < 8) draw(c, c.want, true);
      pump();
    };
    img.onerror = pump;
  };
  for (let k = 0; k < 4; k++) pump(); // 4 downloads em paralelo
}

function nearest(c: Clip, i: number) {
  for (let d = 0; d < c.n; d++) {
    if (c.imgs[i - d]) return c.imgs[i - d];
    if (c.imgs[i + d]) return c.imgs[i + d];
  }
}

function draw(c: Clip, i: number, force = false) {
  if (!c.canvas || !c.n) return;
  c.want = i;
  if (i === c.last && !force) return;
  const img = nearest(c, i);
  if (!img) return;
  c.last = i;
  const cv = c.canvas;
  const dpr = Math.min(devicePixelRatio || 1, 2);
  const w = Math.round(cv.clientWidth * dpr), h = Math.round(cv.clientHeight * dpr);
  if (cv.width !== w || cv.height !== h) {
    cv.width = w; cv.height = h;
    const ay = getComputedStyle(cv).getPropertyValue('--obj-y').trim();
    c.ay = ay === '' ? 0.5 : Number(ay);
  }
  const ctx = cv.getContext('2d')!;
  ctx.clearRect(0, 0, w, h);
  if (c.ratio.startsWith('1x1')) {
    // Fundo transparente: só a caixa do objeto, em "contain", alinhada por --obj-y.
    const [x, y, cw, ch] = c.crop, sw = img.naturalWidth * cw, sh = img.naturalHeight * ch;
    const s = Math.min(w / sw, h / sh), dw = sw * s, dh = sh * s;
    ctx.drawImage(img, img.naturalWidth * x, img.naturalHeight * y, sw, sh, (w - dw) / 2, (h - dh) * c.ay, dw, dh);
  } else {
    const iw = img.naturalWidth, ih = img.naturalHeight, s = Math.max(w / iw, h / ih), dw = iw * s, dh = ih * s;
    ctx.drawImage(img, (w - dw) / 2, (h - dh) / 2, dw, dh);
  }
}

// Começa a baixar quando o capítulo está a uma tela de distância.
const io = new IntersectionObserver(
  (entries) => entries.forEach((e) => e.isIntersecting && load(clips.find((c) => c.el === e.target)!)),
  { rootMargin: '100% 0px' },
);
clips.forEach((c) => c.n && io.observe(c.el));

/* ---------- cor da seção: despeja a partir do anel ---------- */
const tones = [...document.querySelectorAll<HTMLElement>('.tone')];
const pour = document.querySelector<HTMLElement>('.pour')!;
const ring = document.querySelector<HTMLElement>('.ring360')!;
const themeMeta = document.querySelector('meta[name="theme-color"]');
let active: HTMLElement | undefined;
let anim: Animation | undefined;
let animBg = '';
let toneTimer = 0;

function setTone(t: HTMLElement, instant: boolean) {
  const bg = t.dataset.bg!, ink = t.dataset.ink!;
  root.dataset.head = t.dataset.head ?? 'tone'; // topo: escuro com logo oficial no azul, tinta da seção no resto
  root.style.setProperty('--I', ink);
  root.style.setProperty('--F', bg); // anel e topo já seguram a cor nova
  themeMeta?.setAttribute('content', t.dataset.head ? '#030A16' : bg);
  if (anim) { anim.cancel(); anim = undefined; root.style.setProperty('--B', animBg); }
  if (instant || reduced || getComputedStyle(root).getPropertyValue('--B').trim().toUpperCase() === bg.toUpperCase()) {
    root.style.setProperty('--B', bg);
    return;
  }
  const r = ring.getBoundingClientRect();
  const x = r.left + r.width / 2, y = r.top + r.height / 2;
  const R = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));
  pour.style.background = bg;
  const a = pour.animate(
    { clipPath: [`circle(0px at ${x}px ${y}px)`, `circle(${R}px at ${x}px ${y}px)`] },
    { duration: 650, easing: 'cubic-bezier(.2,.75,.25,1)', fill: 'forwards' },
  );
  anim = a;
  animBg = bg;
  a.onfinish = () => {
    if (anim !== a) return;
    root.style.setProperty('--B', bg);
    a.cancel();
    anim = undefined;
  };
}

function pickTone() {
  const mid = innerHeight / 2;
  const t = tones.find((el) => { const r = el.getBoundingClientRect(); return r.top <= mid && r.bottom > mid; });
  if (!t || t === active) return;
  const first = !active;
  active = t;
  clearTimeout(toneTimer);
  // Pequena espera: num salto longo (âncora) só a última seção despeja, sem piscar cores.
  if (first) setTone(t, true);
  else toneTimer = window.setTimeout(() => setTone(t, false), 90);
}

/* ---------- scroll ---------- */
let ticking = false;
function update() {
  ticking = false;
  const vh = innerHeight;
  for (const c of clips) {
    const r = c.el.getBoundingClientRect();
    if (r.bottom < -vh || r.top > 2 * vh) continue;
    // Preso: 0..1 enquanto o palco está fixo. Solto: de quando entra por baixo até a base passar de 35% da tela.
    const raw = c.pin ? -r.top / Math.max(1, r.height - vh) : (vh - r.top) / (0.65 * vh + r.height);
    const p = reduced ? 1 : Math.min(1, Math.max(0, raw));
    c.el.style.setProperty('--p', p.toFixed(4));
    if (!c.tt) draw(c, Math.round(p * (c.n - 1)));
  }
  const max = root.scrollHeight - vh;
  root.style.setProperty('--page-p', (max > 0 ? scrollY / max : 0).toFixed(4));
  pickTone();
}
const schedule = () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } };

// Pontos coloridos no anel fixo = onde cada marketplace começa na página (0..1 da volta).
const dots = [...document.querySelectorAll<HTMLElement>('.ring360-dots i')];
const mks = [...document.querySelectorAll<HTMLElement>('.mk-chapter')];
function placeDots() {
  const max = root.scrollHeight - innerHeight;
  mks.forEach((m, i) => dots[i]?.style.setProperty('--at', (m.offsetTop / max).toFixed(3)));
}

/* ---------- turntable do hero: arraste gira 360°, ocioso gira devagar ---------- */
const tt = document.querySelector<HTMLElement>('[data-turntable]');
const ttClip = clips.find((c) => c.tt);
if (tt && ttClip) {
  let turn = 0; // em voltas
  let vel = 0; // voltas/ms (inércia do arraste)
  let spin = 0; // auto-rotação atual
  let drag = false, lastX = 0, lastT = 0, idleAt = 0, prev = 0, running = false;

  tt.addEventListener('pointerdown', (e) => {
    drag = true; lastX = e.clientX; lastT = e.timeStamp; vel = 0;
    tt.setPointerCapture(e.pointerId);
    tt.classList.add('is-drag');
  });
  tt.addEventListener('pointermove', (e) => {
    if (!drag) return;
    const d = ((e.clientX - lastX) / Math.max(200, tt.clientWidth)) * 0.9;
    turn += d;
    vel = d / Math.max(8, e.timeStamp - lastT);
    lastX = e.clientX; lastT = e.timeStamp;
  });
  const end = () => { drag = false; idleAt = performance.now(); tt.classList.remove('is-drag'); };
  tt.addEventListener('pointerup', end);
  tt.addEventListener('pointercancel', end);

  const frame = (now: number) => {
    const dt = Math.min(64, now - (prev || now));
    prev = now;
    if (!drag) {
      turn += vel * dt;
      vel *= Math.pow(0.94, dt / 16);
      const target = !reduced && now - idleAt > 1400 ? 1 / 26000 : 0; // ~26 s por volta
      spin += (target - spin) * 0.03;
      turn += spin * dt;
    } else spin = 0;
    const p = Number(ttClip.el.style.getPropertyValue('--p')) || 0;
    const shown = turn + p * 0.3; // o scroll também avança um pouco
    tt.style.setProperty('--turn', shown.toFixed(4));
    if (ttClip.n) draw(ttClip, ((Math.floor(shown * ttClip.n) % ttClip.n) + ttClip.n) % ttClip.n);
    if (running) requestAnimationFrame(frame);
  };
  new IntersectionObserver(([e]) => {
    const was = running;
    running = e.isIntersecting;
    if (running && !was) { prev = 0; requestAnimationFrame(frame); }
  }).observe(ttClip.el);
}

/* ---------- inclinação 3D leve nos cards (só mouse) ---------- */
if (!reduced && matchMedia('(hover: hover) and (pointer: fine)').matches) {
  document.querySelectorAll<HTMLElement>('[data-tilt]').forEach((el) => {
    el.addEventListener('pointermove', (e) => {
      const r = el.getBoundingClientRect();
      el.style.setProperty('--rx', `${(((e.clientY - r.top) / r.height) - 0.5) * -6}deg`);
      el.style.setProperty('--ry', `${(((e.clientX - r.left) / r.width) - 0.5) * 6}deg`);
    });
    el.addEventListener('pointerleave', () => { el.style.removeProperty('--rx'); el.style.removeProperty('--ry'); });
  });
}

/* ---------- menu do celular: abre/fecha, fecha no link, no Esc e no toque fora ---------- */
const head = document.querySelector<HTMLElement>('.top')!;
const menuBtn = head.querySelector<HTMLButtonElement>('.menu-btn');
if (menuBtn) {
  const setMenu = (open: boolean) => { head.classList.toggle('menu-open', open); menuBtn.setAttribute('aria-expanded', String(open)); };
  menuBtn.addEventListener('click', () => setMenu(!head.classList.contains('menu-open')));
  head.querySelectorAll('.top-nav a').forEach((a) => a.addEventListener('click', () => setMenu(false)));
  addEventListener('keydown', (e) => { if (e.key === 'Escape' && head.classList.contains('menu-open')) { setMenu(false); menuBtn.focus(); } });
  document.addEventListener('click', (e) => { if (!head.contains(e.target as Node)) setMenu(false); });
}

addEventListener('scroll', schedule, { passive: true });
addEventListener('resize', () => { clips.forEach((c) => { c.last = -1; c.pin = pinned(c.el); }); placeDots(); schedule(); });
placeDots();
update();
