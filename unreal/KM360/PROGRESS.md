# KM 360 — renders Unreal (progresso)

Estado em 2026-11-18: **8/8 clipes renderizados e entregues** em `site/public/frames/<clip>/1x1/0001.webp…`.

## Pipeline (validado)
- Editor UE 5.8.4 aberto com MCP; scripts em `Scripts/` rodados com `python3 -I mcp.py pyfile <script>`.
  Cada `build_<clip>.py` é idempotente: abre/cria `/Game/KM360/Maps/<clip>`, apaga atores com tag "KM",
  recria estúdio + malhas + câmera + `/Game/KM360/Seq/<clip>` e salva.
- Render: `K.render(clip, MAP, SEQ, out_dir, temporal=16, warmup=48)` (MoviePipelinePIEExecutor, assíncrono);
  `./poll.sh` espera terminar. ~1 min por clipe de 96–120 quadros (≈0,6 s/quadro).
- Pós: `python3 sheet.py webp <clip> Saved/Renders/<clip> 82` e `sheet.py contact <clip> <hex> Saved/Renders/<clip>`.
- Alpha: `r.PostProcessing.PropagateAlpha=True` + Deferred `accumulator_includes_alpha` + PNG `write_alpha`.
  Cena sem céu/atmosfera/chão => alpha 0 no fundo; bordas AA pelo TSR com 16 amostras temporais.
- Reflexo na cor da seção: `make_hdri.py` gera HDRI de estúdio (.hdr lat-long 2048x1024): cor da seção com
  gradiente (horizonte claro, chão escuro), softboxes brancos, anel de horizonte 360° e bandas escuras.
  Importado como TextureCube e usado no SkyLight (SLS_SPECIFIED_CUBEMAP, 1024). SkyLight não desenha fundo.
  Calibração: lon_hdri = yaw_mundo + 90 (câmera em -X olhando +X). Shein (branco) usa chão quase preto.
- Luzes: `DEFAULT_LIGHTS` (key + rim) + `RIM_LIGHTS` (painéis frios grandes lado/trás/topo/base — recorte
  pedido pelo coordenador; aparece nos chanfros). Exposição manual, sem bloom/vinheta/motion blur.

## Pegadinhas resolvidas (não repetir)
- Chanfro (`bevel`) em recorte côncavo muito fino (ex.: axila entre manga e corpo) dispara o vértice para longe: virava "orelha" no casaco. Evite ângulos côncavos agudos.
- Tecido/laca clara: não use os RIM_LIGHTS (`lights=K.DEFAULT_LIGHTS`), eles lavam a cor.
- SkyLight `lower_hemisphere_is_black` (padrão True) deixava faces frontais pretas -> False.
- Recapturar SkyLight depois do import (textura compila assíncrona) — `K.render()` já recaptura.
- `append_simple_extrude_polygon` só triangula polígono côncavo certo no sentido horário (u,v); no outro sentido
  dobra triângulos (o K virava cunha). `extrude_poly` triangula horário e inverte normais (`flip_normals`).
- Tubos precisam de UV (tangente degenerada -> NaN/riscos). Render com `step>1` mostra ghosting do TSR
  (só em teste; render contínuo é limpo).
- Objetos pequenos refletidos em cromo grande: desligar `affect_distance_field_lighting` evita borrões do Lumen.
- Clear coat não é conectável pelo Python (MP_CUSTOM_DATA não exposto) — recorte feito com luz.

## Assets
- Mapas `/Game/KM360/Maps/<clip>`, sequências `/Game/KM360/Seq/<clip>` (30 fps, CineCamera 50 mm, filmback 24x24).
- Materiais `/Game/KM360/Materials/M_Metal` + MIs (MI_K_Blue #1444A6 r.25, MI_Chrome #D7D5D6 r.08,
  MI_Arc_Blue #2180F4 r.18, MI_ML_*, MI_TT_*, MI_Shopee_*, MI_Coin_Gold, MI_Tag_RoseGold, MI_Shein_DarkChrome...).
- HDRI `/Game/KM360/HDRI/HDR_<clip>` (fontes em `Saved/HDRI/`).
- Malhas `/Game/KM360/Meshes/`: SM_KM_Letters (K azul slot0; perna+M cromo slot1), SM_KM_Arc (235°),
  SM_Final_Arc_000..095 (uma por quadro do clipe final), SM_Res_*, SM_ML_*, SM_TT_*, SM_Shein_*, SM_Shopee_*,
  SM_Problema_Tag.
- Sobras de teste: mapa/seq `calib` e `HDR_calib` (calibração do HDRI) — podem ser apagados.

## Clipes
| clip | quadros | KB médio | notas |
|---|---|---|---|
| hero | 120 | 37 | turntable 3°/quadro (0..357°), loop ok; re-render com K corrigido + recorte |
| final | 96 | 61 | arco 235° -> anel 360° (recentra e abre raio), giro -10..+10°, recorte frio |
| resultados | 96 | 76 | 14 colunas em arco de 300°, sobem em sequência; maior em verde metálico |
| mercadolivre | 96 | 61 | esteira circular + 6 caixas (cromo/ouro) + barra 5 LEDs vermelho->verde |
| tiktokshop | 96 | 38 | 5 celulares 9:16 orbitando + 12 corações rosa-cromo subindo |
| shein | 96 | 42 | v2 (2026-11-19): arara preta + 5 cabides de frente; peças nas cores do site entram uma a uma com pulo e balanço; sem os painéis de recorte (lavavam o tecido) |
| shopee | 96 | 28 | v2 (2026-11-19): sacola laca branca com selo laranja + anel de moedas e cupons picotados; com o scroll voam para a sacola, que quica; cupons ficam espetados na boca no fim |
| problema | 96 | 41 | 20 etiquetas em caos -> grade 5x4 (girada 22°) |
