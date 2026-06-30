# ive

AI destekli marka kimliği (brand design) çıkarma aracı.

Mistral AI tool calling ile çalışır — tüm dosya okuma/yazma ve komut çalıştırma işlemleri Mistral modeli tarafından tool calling ile yapılır.

## Kurulum

```bash
pip install git+https://github.com/yaso09/ive.git
```

### GitHub Actions — Hazır Build'ler

Her commit'te GitHub Actions ile otomatik wheel build alınır:

| Platform | Runner |
|----------|--------|
| x86_64 | `ubuntu-latest` |
| ARM64 (aarch64) | `ubuntu-24.04-arm` |

Build'leri indirip kurmak:

```bash
# 1. GitHub repo sayfasında Actions sekmesine tıkla
# 2. En son workflow'u seç
# 3. "Artifacts" bölümünden platformuna uygun .zip'i indir

# 4. İndirilen zip'in içindeki .whl dosyasını kur:
pip install ive-*.whl
```

Termux'da ARM64 build kullanmak için:

```bash
# Termux'da pip ve Python hazır:
pkg update && pkg install python pip

# ARM64 wheel'i indirip kur:
pip install ive-*.whl

# API anahtarını kaydet:
ive auth login mistral

# Kullanmaya başla:
ive init
```

**Not:** ive saf bir Python paketidir, bu yüzden `ive-*.whl` tüm platformlarda (x86_64, ARM64, Windows, macOS) aynıdır. İsterseniz herhangi bir platformun build'ini kullanabilirsiniz.

**Gereksinim:** `MISTRAL_API_KEY` ortam değişkeni ya da `ive auth login mistral` ile kaydedilmiş bir API anahtarı.

## API Key Yönetimi

İki yöntemden biriyle API anahtarınızı tanımlayın:

```bash
# Yöntem 1 — env var (export ile, her shell'de tekrar gerekir):
export MISTRAL_API_KEY="your-api-key"
export MISTRAL_MODEL="mistral-large-latest"  # isteğe bağlı, varsayılan: mistral-large-latest
```

```bash
# Yöntem 2 — kalıcı kayıt (ive auth login, bir kere yeter):
ive auth login mistral
# API key sorar (girdiğiniz gösterilmez), şuraya kaydeder:
#   Linux/macOS: ~/.config/ive/auth.json
#   Windows:     %APPDATA%\ive\auth.json
# --key ile direkt de verilebilir:
ive auth login mistral --key "sk-..."
```

API anahtarı aranma sırası:
1. `MISTRAL_API_KEY` ortam değişkeni
2. `ive auth login mistral` ile kaydedilmiş dosya

## İşletim Sistemi Bilgisi

ive, her Mistral API çağrısında host işletim sistemini otomatik olarak modele bildirir:

| OS | Bildirilen |
|----|-----------|
| Windows | `Windows 10 (64-bit) on AMD64` |
| Linux | `Ubuntu 24.04 LTS kernel 6.8.0 on x86_64` |
| macOS | `macOS 24.1 on arm64` |

Böylece model, işletim sistemine uygun komutlar ve dosya yolları üretir.

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
ive init --model mistral-large-latest
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
ive version                    # 0.8.0
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
ive create script --to my-video --model mistral-large-latest
```

### `ive generate`

```bash
ive generate video my-video               # Mistral AI ile video kodu üretir
ive generate video my-video --model mistral-large-latest
```

### `ive delete`

```bash
ive delete                                 # tüm .brand/ klasörünü siler
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
| `--model` | init, create script, generate video | Mistral model adı (varsayılan: `mistral-large-latest`, `MISTRAL_MODEL` env ile değiştirilebilir) |
| `--steps` | init | Adım filtresi (örn. `0-3`, `0,2,5`, `!3`) |
| `--key` | auth login mistral | API anahtarı (atlarsanız interaktif sorar) |

## Tüm komutlar

| Komut | Açıklama |
|-------|----------|
| `ive init` | 6 adımlı brand pipeline'ı çalıştırır |
| `ive auth login mistral` | Mistral API anahtarını kalıcı kaydeder |
| `ive check` | Pipeline durumunu kontrol eder |
| `ive show script --of <video>` | Script içeriğini gösterir |
| `ive create video <name>` | Remotion video projesi oluşturur |
| `ive create script --to <video>` | Interaktif script oluşturur |
| `ive generate video <name>` | Mistral AI ile video kodu üretir |
| `ive delete` | `.brand/` klasörünü siler |
| `ive delete video <name>` | Video klasörünü siler |
| `ive delete script --to <video>` | Script dosyasını siler |
| `ive list video` | Videoları listeler |
| `ive version` | Versiyon bilgisi |

## Gereksinimler

- Python ≥ 3.10
- `MISTRAL_API_KEY` ortam değişkeni **veya** `ive auth login mistral` ile kaydedilmiş anahtar
- `mistralai` Python paketi
