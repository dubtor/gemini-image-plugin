#!/usr/bin/env python3
"""
gemini-generate — Image generation via Google Gemini API

Modes:
  Text-to-Image:   gemini-generate.py "prompt text" [options]
  Image-to-Image:  gemini-generate.py "prompt text" --reference img1.png [options]

Requires: GEMINI_API_KEY environment variable set with your Google AI API key.
"""

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

# ── Model & Endpoint ──────────────────────────────────────────────────────
API_BASE = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_MODEL = "gemini-3.1-flash-image-preview"

VALID_RATIOS = [
    "1:1", "3:2", "2:3", "3:4", "4:3",
    "4:5", "5:4", "9:16", "16:9", "21:9",
    "1:4", "4:1", "1:8", "8:1",
]
VALID_SIZES = ["512", "1K", "2K", "4K"]
VALID_FORMATS = ["png", "jpeg", "webp"]


# ── API helper ─────────────────────────────────────────────────────────────

def api_request(url, api_key, data):
    """Make an authenticated request to the Gemini API."""
    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json",
    }
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw, strict=False)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(f"ERROR: HTTP {e.code} — {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Connection failed — {e.reason}", file=sys.stderr)
        sys.exit(1)


def generate_image(api_key, model, prompt, parts, aspect_ratio, image_size):
    """Send a generateContent request and return image data from the response."""
    url = f"{API_BASE}/models/{model}:generateContent"

    # Build content parts: text prompt first, then any reference images
    content_parts = [{"text": prompt}]
    content_parts.extend(parts)

    payload = {
        "contents": [{
            "parts": content_parts,
        }],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
        },
    }

    # Add image config if aspect ratio or size specified
    image_config = {}
    if aspect_ratio:
        image_config["aspectRatio"] = aspect_ratio
    if image_size:
        image_config["imageSize"] = image_size
    if image_config:
        payload["generationConfig"]["imageConfig"] = image_config

    result = api_request(url, api_key, payload)

    # Extract images from response
    images = []
    candidates = result.get("candidates", [])
    if not candidates:
        # Check for prompt feedback / blocking
        block_reason = result.get("promptFeedback", {}).get("blockReason")
        if block_reason:
            print(f"ERROR: Request blocked — {block_reason}", file=sys.stderr)
        else:
            print(f"ERROR: No candidates in response: {json.dumps(result)[:500]}", file=sys.stderr)
        return images

    parts_resp = candidates[0].get("content", {}).get("parts", [])
    for part in parts_resp:
        if "inlineData" in part:
            images.append({
                "data": part["inlineData"]["data"],
                "mimeType": part["inlineData"]["mimeType"],
            })

    return images


# ── Image reference handling ──────────────────────────────────────────────

def resolve_image_refs(refs):
    """Convert local file paths and URLs to Gemini inline_data parts."""
    parts = []
    for ref in refs:
        if ref.startswith("http://") or ref.startswith("https://"):
            # Download the image and convert to base64
            try:
                with urllib.request.urlopen(ref, timeout=30) as resp:
                    img_data = resp.read()
                    content_type = resp.headers.get("Content-Type", "image/png")
                    # Extract just the mime type (strip parameters like charset)
                    mime = content_type.split(";")[0].strip()
                    b64 = base64.b64encode(img_data).decode("utf-8")
                    parts.append({
                        "inline_data": {
                            "mime_type": mime,
                            "data": b64,
                        }
                    })
            except Exception as e:
                print(f"ERROR: Failed to download reference URL {ref}: {e}", file=sys.stderr)
                sys.exit(1)
        elif os.path.isfile(ref):
            mime = mimetypes.guess_type(ref)[0] or "image/png"
            with open(ref, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            parts.append({
                "inline_data": {
                    "mime_type": mime,
                    "data": b64,
                }
            })
        else:
            print(f"ERROR: Reference file not found: {ref}", file=sys.stderr)
            sys.exit(1)
    return parts


def save_image(image_data, mime_type, output_path, target_format):
    """Decode base64 image data and save to file."""
    raw = base64.b64decode(image_data)

    # Determine source format from mime type
    source_ext = mime_type.split("/")[-1] if mime_type else "png"
    # Map common mime subtypes
    ext_map = {"jpeg": "jpeg", "jpg": "jpeg", "png": "png", "webp": "webp"}
    source_ext = ext_map.get(source_ext, source_ext)

    # If target format matches source, just write directly
    # (No conversion needed — Gemini returns the format it chooses)
    with open(output_path, "wb") as f:
        f.write(raw)

    size_kb = len(raw) / 1024
    return size_kb


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generate images via Google Gemini API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Text-to-Image:
    %(prog)s "A black blazer collar on beige linen"
    %(prog)s "A modern office" --ratio 16:9 --size 2K --count 4

  Image-to-Image (edit/transform with reference):
    %(prog)s "Make this photo look like a watercolor" --reference photo.png
    %(prog)s "Combine these into one scene" --reference bg.png --reference object.png

  Advanced:
    %(prog)s "A detailed scene" --size 4K
    %(prog)s "Quick draft" --size 512 --count 4
        """,
    )

    parser.add_argument("prompt", help="The image generation prompt")
    parser.add_argument("--count", "-n", type=int, default=2,
                        help="Number of images to generate (1-4, default: 2)")
    parser.add_argument("--ratio", "-r", default="1:1", choices=VALID_RATIOS,
                        help="Aspect ratio (default: 1:1)")
    parser.add_argument("--size", "-s", default="1K", choices=VALID_SIZES,
                        help="Image size: 512, 1K, 2K, or 4K (default: 1K)")
    parser.add_argument("--format", "-f", default="png", choices=VALID_FORMATS,
                        help="Output format (default: png)")
    parser.add_argument("--output", "-o", default="./generated-images",
                        help="Output directory (default: ./generated-images)")
    parser.add_argument("--name", help="File name prefix (default: auto-generated from prompt)")
    parser.add_argument("--reference", action="append", default=[],
                        help="Reference image path or URL (repeatable). Enables image-to-image mode")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help=f"Gemini model (default: {DEFAULT_MODEL})")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducible results")
    parser.add_argument("--timeout", type=int, default=120,
                        help="Max seconds per request (default: 120)")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Minimal output (only print final file paths)")

    args = parser.parse_args()

    # ── Validate ──
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        print("  Get your key at https://aistudio.google.com/apikey", file=sys.stderr)
        print("  Then: export GEMINI_API_KEY=your_key_here", file=sys.stderr)
        sys.exit(1)

    if args.count < 1 or args.count > 4:
        print("ERROR: --count must be between 1 and 4", file=sys.stderr)
        sys.exit(1)

    # ── Determine mode ──
    is_img2img = len(args.reference) > 0
    mode = "image-to-image" if is_img2img else "text-to-image"

    # ── Build name prefix ──
    if args.name:
        name_prefix = args.name
    else:
        words = args.prompt.lower().split()[:4]
        slug = "-".join(
            "".join(c for c in w if c.isalnum() or c == "-")
            for w in words
        )
        name_prefix = slug[:50] or "image"

    # ── Prepare output dir ──
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Resolve reference images ──
    ref_parts = []
    if is_img2img:
        ref_parts = resolve_image_refs(args.reference)

    # ── Generate images ──
    if not args.quiet:
        print(f"Mode: {mode}")
        print(f"Model: {args.model}")
        print(f"Images: {args.count} x {args.ratio} @ {args.size}")
        if is_img2img:
            print(f"References: {len(args.reference)} image(s)")

    downloaded = []
    for i in range(1, args.count + 1):
        if not args.quiet:
            print(f"Generating image {i}/{args.count}...")

        images = generate_image(
            api_key=api_key,
            model=args.model,
            prompt=args.prompt,
            parts=ref_parts,
            aspect_ratio=args.ratio,
            image_size=args.size,
        )

        if not images:
            print(f"  WARNING: No image returned for request {i}/{args.count}", file=sys.stderr)
            continue

        # Save the first image from this response
        img = images[0]
        # Determine file extension from mime type
        mime_ext = img["mimeType"].split("/")[-1]
        ext_map = {"jpeg": "jpeg", "jpg": "jpeg", "png": "png", "webp": "webp"}
        file_ext = ext_map.get(mime_ext, args.format)

        filename = f"{name_prefix}_{i}.{file_ext}"
        filepath = output_dir / filename

        size_kb = save_image(img["data"], img["mimeType"], str(filepath), args.format)

        if size_kb is not None:
            downloaded.append(str(filepath))
            if not args.quiet:
                print(f"  [{i}/{args.count}] {filepath} ({size_kb:.0f} KB)")

    # ── Summary ──
    if not args.quiet:
        print(f"\nDone! {len(downloaded)} image(s) saved to {output_dir}/")
    else:
        for p in downloaded:
            print(p)

    if not args.quiet:
        print(f"\n{json.dumps({'files': downloaded, 'count': len(downloaded)})}")


if __name__ == "__main__":
    main()
