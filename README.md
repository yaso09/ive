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
ive init --dir ../other-project   # farklı proje dizini
```

### `ive check`

Pipeline durumunu kontrol eder — her adımın çıktısını `.brand/` altında denetler.

```bash
ive check                      # mevcut dizin
ive check --dir ../other-project
```

Çıktı:
```
  [0] brand design document: ok
  [1] asset extraction: missing
  [2] UI element extraction: ok
  [3] SVG rendering: ok
  [4] screenshots: ok
  [5] map generation: ok
ive: init incomplete — some steps are missing
```

### `ive version`

```bash
ive version                    # 0.6.0
```

### `ive show`

```bash
ive show script --of my-video              # script.md içeriğini terminale yazdırır
ive show script --of my-video --dir ../other-project
```

### `ive create`

```bash
ive create video "my-video"               # Remotion video projesi oluşturur (.brand/videos/my-video/)
ive create script --to my-video            # interaktif prompt ile script.md oluşturur
ive create script --to my-video --agent uzman
ive create script --to my-video --model anthropic/claude-sonnet-4
```

### `ive generate`

```bash
ive generate video my-video               # opencode TUI açar, script.md'yi referans alır
ive generate video my-video --agent uzman
ive generate video my-video --model anthropic/claude-sonnet-4
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

## Tüm flag'ler

| Flag | Komutlar | Açıklama |
|------|----------|----------|
| `--dir` | init, check, show, create, delete, list, generate | Proje dizini (varsayılan: `.`) |
| `--of` | show script | Video adı (örn. my-video) |
| `--agent` | init, create script, generate video | Opencode agent adı |
| `--model` | init, create script, generate video | Model adı (örn. `anthropic/claude-sonnet-4`) |
| `--steps` | init | Adım filtresi (örn. `0-3`, `0,2,5`, `!3`) |

## Gereksinimler

- Python ≥ 3.10
- [opencode](https://opencode.ai) (`opencode` PATH'te olmalı)
