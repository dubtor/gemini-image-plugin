# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Claude Code plugin that generates images via the **Google Gemini API** directly (no fal.ai intermediary). It's a skill-based plugin — no build system, no dependencies beyond Python 3 stdlib.

## Repository Structure

- `.claude-plugin/plugin.json` — Plugin manifest (name, version, metadata)
- `skills/gemini-image/SKILL.md` — Skill definition with prompt enhancement instructions and usage docs
- `skills/gemini-image/gemini-generate.py` — The single Python script that handles all API interaction

## How It Works

The plugin exposes one skill (`gemini-image`) invoked via `/gemini-image:gemini-image "prompt" [options]`.

**Two modes**, selected automatically by the presence of `--reference`:
- **Text-to-image**: sends prompt as text to Gemini generateContent
- **Image-to-image**: sends prompt + reference images as inline_data parts (when `--reference` is provided)

**Key architectural detail**: Unlike queue-based APIs, the Gemini API is **synchronous** — each request returns the generated image directly as base64-encoded data in the response. For multiple images (`--count N`), the script makes N separate API calls.

**Prompt enhancement**: By default, SKILL.md instructs Claude to rewrite the user's prompt with composition, lighting, camera/lens, and color grading details before passing it to the script. `--no-enhance` skips this (handled by Claude, not the Python script).

## Running the Script

```bash
# Requires GEMINI_API_KEY env var
export GEMINI_API_KEY=your_key_here

# Text-to-image
python3 skills/gemini-image/gemini-generate.py "A prompt" --ratio 16:9 --size 2K --count 2

# Image-to-image
python3 skills/gemini-image/gemini-generate.py "Edit this" --reference photo.png
```

No tests, no linter, no build step. The script uses only Python 3 standard library (urllib, json, argparse, base64).

## API Flow

1. Build request payload with prompt (+ optional reference images as base64 inline_data)
2. POST to `generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`
3. Extract base64 image data from `candidates[0].content.parts[].inlineData`
4. Decode and save images to local `./generated-images/` directory
5. Repeat for each requested image (--count N)

## Versioning

Bei jeder Änderung am Plugin immer die Patch-Version in `.claude-plugin/plugin.json` erhöhen (z.B. 1.0.0 → 1.0.1).

## Plugin-Dokumentation

Claude Code Plugin-Spezifikation: https://code.claude.com/docs/en/plugins
