# ive

AI destekli marka kimliği (brand design) çıkarma aracı.

## Kurulum

```bash
pip install git+https://github.com/yaso09/ive.git
```

## Komutlar

### `ive init`

6 adımlı pipeline ile `.brand/` klasörü altında tasarım sistemi dokümanı, varlık dosyaları, komponent çizimleri, ekran görüntüleri ve harita JSON'ı üretir.

| Adım | Prompt | Çıktı |
|------|--------|-------|
| 0 | `DESIGN.md` | `.brand/DESIGN.md` — tasarım sistemi dokümanı |
| 1 | `1.md` | `.brand/assets/` — statik medya dosyaları |
| 2 | `2.md` | `.brand/elements/html/` — React komponent HTML'leri |
| 3 | `3.md` | `.brand/elements/svg/` — komponent SVG'leri |
| 4 | `4.md` | `.brand/screenshots/` — ekran görüntüleri |
| 5 | `5.md` | `.brand/map.json` — tüm çıktıların haritası |

```bash
ive init
ive init --steps 0          # sadece DESIGN.md
ive init --steps 0-2        # ilk 3 adım
ive init --steps "!3"       # SVG adımı hariç
ive init --agent my-agent   # opencode agent belirtme
ive init --model anthropic/claude-sonnet-4
```

### `ive create`

```bash
ive create video "my-video"               # Remotion video projesi oluşturur (.brand/videos/my-video/)
ive create script --to my-video            # boş script.md oluşturur
```

### `ive delete`

```bash
ive delete video my-video                  # video klasörünü siler
ive delete script --to my-video            # script.md dosyasını siler
```

### `ive list`

```bash
ive list video                            # videoları listeler
```

Çıktı:
```
my-video      script.md
other-video   
```

## Promptları özelleştirme

`src/ive/prompts/` altındaki 6 prompt dosyasını düzenleyerek her adımın davranışını değiştirebilirsiniz.

## Gereksinimler

- Python ≥ 3.10
- [opencode](https://opencode.ai) (`opencode` PATH'te olmalı)
