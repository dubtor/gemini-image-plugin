---
name: gemini-image
description: "Generate and edit images via Google Gemini API. Text-to-image and image-to-image with references. Use when the user wants to generate, create, or edit images with AI."
---

# gemini-image — Image Generation via Google Gemini API

Generate images using Google's Gemini API directly. Supports text-to-image and image-to-image editing (with reference images).

## Usage

`/gemini-image:gemini-image $ARGUMENTS`

## Instructions

### Step 1: Enhance the prompt (unless `--no-enhance` is passed)

By default, **rewrite and expand the user's prompt** before sending it to the API. Apply these principles:

**Prompt structure — always include all of these:**
- **Subject**: Who or what is in the image. Be specific about materials, colors, and details (not just "a suit jacket" but "a navy blue tweed suit jacket with satin lapels")
- **Action/State**: What the subject is doing or how it is positioned
- **Location/Context**: Where the scene takes place, what surrounds the subject
- **Composition**: Camera angle, framing, what's in focus (e.g. "medium shot, slightly off-center, shallow depth of field")
- **Style**: The visual genre (e.g. "editorial fashion photography", "fine art still life", "architectural detail photography")
- **Lighting**: Be specific about light direction, quality, and mood (e.g. "soft directional window light from the left with warm fill from above", "three-point softbox setup", "golden hour backlighting")
- **Camera/Lens**: Name specific hardware for visual DNA (e.g. "shot on Fujifilm GFX 100S with 80mm f/1.7 lens" or "Leica Q3, 28mm f/2.8"). This controls depth, distortion, and perspective
- **Color grading**: Define the emotional tone through color (e.g. "desaturated warm tones, muted contrast", "cinematic teal-and-orange grading", "near-monochromatic palette of cream and charcoal")

**Key rules:**
- Use **positive framing**: describe what you want, not what you don't want ("empty street" instead of "no cars")
- Write **narratively**, not as a keyword list
- Specify **materiality and texture** when relevant ("brushed brass", "raw concrete", "cream linen with fine weave")
- Include **film stock or grain** if it fits the mood ("analog medium-format film with fine grain")

**Show the user** the enhanced prompt before running the script, so they can see what was sent.

If `--no-enhance` is passed, use the prompt exactly as provided without modification.

### Step 2: Run the script

Run the Python script via Bash with the final prompt and all other arguments:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/gemini-image/gemini-generate.py "THE FINAL PROMPT" [other args from $ARGUMENTS]
```

Note: When enhancing the prompt, replace the user's original prompt with the enhanced version in the command. Pass all other flags through unchanged.

### Step 3: Show results

After the script completes, **display the generated images** to the user using the Read tool on each downloaded file.

If the script exits with an error about GEMINI_API_KEY, tell the user:
```
export GEMINI_API_KEY=your_key_here
```
Get a key at https://aistudio.google.com/apikey

## Arguments

- **Positional**: `"prompt text"` — the image description (required)
- `--no-enhance` — send the prompt exactly as written, skip prompt optimization
- `--count N` / `-n N` — number of images, 1-4 (default: 2)
- `--ratio RATIO` / `-r RATIO` — aspect ratio: 1:1, 16:9, 9:16, 3:2, 2:3, etc. (default: 1:1)
- `--size SIZE` / `-s SIZE` — image size: 512, 1K, 2K, or 4K (default: 1K)
- `--format FMT` / `-f FMT` — png, jpeg, or webp (default: png)
- `--output DIR` / `-o DIR` — output directory (default: ./generated-images)
- `--name NAME` — filename prefix (default: auto from prompt)
- `--reference FILE` — reference image for image-to-image mode (repeatable, local paths or URLs)
- `--model MODEL` — Gemini model to use (default: gemini-2.5-flash-preview-image-generation)
- `--seed N` — random seed for reproducible results
- `--quiet` / `-q` — minimal output

## Examples

```
# Simple prompt -> Claude enhances it automatically
/gemini-image:gemini-image "Blazer auf Leinen"

# Detailed prompt -> Claude still enhances with technical details
/gemini-image:gemini-image "Visitenkarten auf Stein" --ratio 3:2 --size 2K

# Pre-written prompt -> send exactly as-is
/gemini-image:gemini-image "A full detailed prompt here..." --no-enhance

# Image-to-image editing with reference
/gemini-image:gemini-image "Make this brighter and warmer" --reference photo.png

# Multiple references
/gemini-image:gemini-image "Combine style and content" --reference style.png --reference content.png
```
