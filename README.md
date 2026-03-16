# gemini-image — Claude Code Plugin

AI image generation for [Claude Code](https://claude.ai/code) via [Google Gemini API](https://ai.google.dev/gemini-api/docs/image-generation), powered by Gemini's native image generation.

## Installation

```bash
# Add the marketplace
/plugin marketplace add dubtor/dubtor-plugins

# Install the plugin
/plugin install gemini-image@dubtor-plugins
```

## Setup

You need a Google AI API key:

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Create an API key
3. Set the environment variable:

```bash
export GEMINI_API_KEY=your_key_here
```

## Usage

```bash
# Text-to-image — Claude enhances your prompt automatically
/gemini-image:gemini-image "A blazer on linen fabric"

# With options
/gemini-image:gemini-image "A modern office" --ratio 16:9 --size 2K --count 4

# Send prompt as-is (no enhancement)
/gemini-image:gemini-image "Your detailed prompt here..." --no-enhance

# Image-to-image editing with reference images
/gemini-image:gemini-image "Make this brighter" --reference photo.png
/gemini-image:gemini-image "Combine these" --reference style.png --reference content.png
```

## Options

| Flag | Description | Default |
|---|---|---|
| `--count N`, `-n N` | Number of images (1-4) | 2 |
| `--ratio RATIO`, `-r RATIO` | Aspect ratio (1:1, 16:9, 9:16, 3:2, etc.) | 1:1 |
| `--size SIZE`, `-s SIZE` | Image size: 512, 1K, 2K, or 4K | 1K |
| `--format FMT`, `-f FMT` | png, jpeg, or webp | png |
| `--output DIR`, `-o DIR` | Output directory | ./generated-images |
| `--name NAME` | Filename prefix | Auto from prompt |
| `--reference FILE` | Reference image (repeatable) | — |
| `--model MODEL` | Gemini model to use | gemini-3.1-flash-image-preview |
| `--seed N` | Random seed for reproducibility | — |
| `--no-enhance` | Skip prompt optimization | — |
| `--quiet`, `-q` | Minimal output | — |

## Model

Default model: `gemini-3.1-flash-image-preview`

You can switch models with `--model`:
- `gemini-3.1-flash-image-preview` — Fast, high quality (default)

Key capabilities:
- Native image generation via Gemini's multimodal capabilities
- Text rendering support
- Image-to-image editing with up to 14 reference images
- Resolutions from 512px to 4K
- Direct API — no queue, no polling, instant response

## Pricing

Gemini image generation is free during preview. Once generally available, pricing will follow Google's standard Gemini API rates. See [ai.google.dev/pricing](https://ai.google.dev/pricing) for current info.

## Prompt Enhancement

By default, Claude enhances your prompt with composition, lighting, camera/lens, and color grading details. Use `--no-enhance` to skip this.

## Requirements

- Python 3 (standard library only, no pip packages needed)
- `GEMINI_API_KEY` environment variable

## Author

Robert Clemens — [83 Ventures GmbH](https://83ventures.io) · [@dubtor](https://github.com/dubtor)

## License

MIT
