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

```bash
ive init --agent design-agent --model openai/gpt-4o
ive init --dir ../baska-proje
```

## Nasıl çalışır

1. `prompts/DESIGN.md` şablonunu okur
2. Proje bağlamını toplar (README, package.json, dosya ağacı)
3. Şablon + bağlam birleştirilmiş promptu opencode'a gönderir
4. Opencode `.brand/DESIGN.md`'yi oluşturur

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
