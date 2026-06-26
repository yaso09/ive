# ive

AI destekli marka kimliği (brand design) dokümanı oluşturma aracı.

`ive init` çalıştırıldığında, projenizi analiz eder ve bir AI coding agent (opencode) aracılığıyla `.brand/DESIGN.md` dosyası oluşturur. Çıkan doküman; renk paleti, tipografi, spacing sistemi, komponent pattern'leri ve framework kurallarını içeren kapsamlı bir tasarım sistemidir.

## Kurulum

```bash
uv tool install .
```

## Kullanım

```bash
cd projem
ive init
```

`.brand/DESIGN.md` otomatik oluşur.

### Seçenekler

| Bayrak | Açıklama |
|--------|----------|
| `--dir` | Proje dizini (varsayılan: `.`) |
| `--agent` | Kullanılacak opencode agent |
| `--model` | Kullanılacak model (örn. `anthropic/claude-sonnet-4`) |
| `--steps` | Çalıştırılacak adımlar (örn. `0-3`, `0,2,5`) |

```bash
ive init --agent design-agent --model openai/gpt-4o
ive init --dir ../baska-proje
ive init --steps 0        # sadece DESIGN.md
ive init --steps 0-2      # ilk 3 adım
ive init --steps 0,4      # DESIGN.md + screenshot
```

## Nasıl çalışır

`ive init` 6 adımlı bir pipeline çalıştırır:

| Adım | Prompt | Çıktı |
|------|--------|-------|
| 0 | `DESIGN.md` | `.brand/DESIGN.md` — tasarım sistemi dokümanı |
| 1 | `1.md` | `.brand/assets/` — statik medya dosyaları |
| 2 | `2.md` | `.brand/elements/html/` — React komponent HTML'leri |
| 3 | `3.md` | `.brand/elements/svg/` — komponent SVG'leri |
| 4 | `4.md` | `.brand/screenshots/` — ekran görüntüleri |
| 5 | `5.md` | `.brand/map.json` — tüm çıktıların haritası |

Her adım sırayla opencode'a gönderilir. Bir önceki adımın çıktısı sonraki adımın girdisi olur.

## Prompt şablonunu özelleştirme

`prompts/DESIGN.md` dosyasını düzenleyerek AI'a vereceğiniz talimatları değiştirebilirsiniz. Mevcut şablon 4 bölümden oluşur:

- Brand & Aesthetic (renk paleti, vibe)
- Typography & Spacing (font, type scale, grid)
- Component Patterns & Rules (button, nav, card, layout)
- Code Execution & Framework (Tailwind, CSS Modules, vb.)

## Gereksinimler

- Python ≥ 3.10
- [uv](https://docs.astral.sh/uv/)
- [opencode](https://opencode.ai)
