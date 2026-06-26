# ive

AI destekli marka kimliği (brand design) çıkarma aracı.

`ive init` projenizi analiz eder ve 6 adımlı bir pipeline ile `.brand/` klasörü altında tasarım sistemi dokümanı, varlık dosyaları, komponent çizimleri, ekran görüntüleri ve bir harita JSON'ı üretir.

## Kurulum

```bash
uv tool install .
```

## Kullanım

```bash
cd projem
ive init
```

Tüm pipeline çalışır ve `.brand/` klasörü oluşur.

### Seçenekler

| Bayrak | Açıklama |
|--------|----------|
| `--dir` | Proje dizini (varsayılan: `.`) |
| `--agent` | Kullanılacak opencode agent |
| `--model` | Kullanılacak model (örn. `anthropic/claude-sonnet-4`) |
| `--steps` | Çalıştırılacak adımlar |

```bash
ive init --agent design-agent --model openai/gpt-4o
ive init --dir ../baska-proje
ive init --steps 0          # sadece DESIGN.md
ive init --steps 0-2        # ilk 3 adım
ive init --steps 0,4        # DESIGN.md + screenshot
ive init --steps "!3"       # SVG adımı hariç
ive init --steps "!2,!4"    # element ve screenshot hariç
```

## Pipeline

`ive init` 6 adımı sırayla opencode'a gönderir:

| Adım | Prompt | Çıktı |
|------|--------|-------|
| 0 | `DESIGN.md` | `.brand/DESIGN.md` — tasarım sistemi dokümanı |
| 1 | `1.md` | `.brand/assets/` — statik medya dosyaları |
| 2 | `2.md` | `.brand/elements/html/` — React komponent HTML'leri |
| 3 | `3.md` | `.brand/elements/svg/` — komponent SVG'leri |
| 4 | `4.md` | `.brand/screenshots/` — ekran görüntüleri |
| 5 | `5.md` | `.brand/map.json` — tüm çıktıların haritası |

Her adım bir öncekinin çıktısı üzerine kurulur. Adım 0 hariç tüm adımlar kendi promptlarında yeterli bağlamı içerir (opencode projeyi doğrudan analiz eder). Adım 0'a ayrıca proje bağlamı (README, package.json, dosya ağacı) eklenir.

## Promptları özelleştirme

`src/ive/prompts/` altındaki 6 prompt dosyasını düzenleyerek her adımın davranışını değiştirebilirsiniz:

| Dosya | Kapsam |
|-------|--------|
| `DESIGN.md` | Renk paleti, tipografi, spacing, komponent pattern'leri, framework kuralları |
| `1.md` | Statik varlık taraması ve kopyalama (görsel, ses) |
| `2.md` | React komponent tespiti ve HTML'e dönüştürme |
| `3.md` | HTML komponentlerinden SVG oluşturma |
| `4.md` | Uygulamayı başlatıp ekran görüntüsü alma (Playwright) |
| `5.md` | Tüm çıktıları `.brand/map.json` altında birleştirme |

## Gereksinimler

- Python ≥ 3.10
- [uv](https://docs.astral.sh/uv/)
- [opencode](https://opencode.ai) (`opencode` PATH'te olmalı)
