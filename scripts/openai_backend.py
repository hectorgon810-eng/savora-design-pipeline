#!/usr/bin/env python3
"""
OpenAI image backend — gpt-image-2 adapter for the restaurant-design-pipeline.

Mirrors the interface of the Gemini call in nano_banana_runner.py so the
runner can swap backends with `--backend gemini|openai|both`.

Released Apr 21, 2026. Native thinking, 2K res, multi-image consistency.
Docs: https://developers.openai.com/api/docs/models/gpt-image-2
"""

from __future__ import annotations

import base64
import io
import pathlib
import sys
from typing import Optional

try:
    from openai import OpenAI
except ImportError:
    sys.exit("Install: pip3 install openai")


# Aspect ratio → OpenAI size mapping.
# gpt-image-2 supports: 1024x1024, 1024x1536, 1536x1024, 2048x2048, 2048x3072,
# 3072x2048, plus "auto". Use "auto" when aspect isn't a direct match and
# let the model pick the closest.
SIZE_MAP = {
    # 1024-tier sizes — native IG-spec, ~5x cheaper than 2K tier.
    # Instagram max is 1080x1350 for 4:5, so 2K is overkill for social output.
    "1:1":  "1024x1024",
    "4:5":  "1024x1280",   # NATIVE 4:5 (confirmed via API probe 2026-04-22, cost-optimized tier)
    "2:3":  "1024x1536",
    "9:16": "1024x1536",
    "3:2":  "1536x1024",
    "16:9": "1536x1024",
}


def _size_for(aspect_ratio: str) -> str:
    return SIZE_MAP.get(aspect_ratio, "auto")


_SAFE_ZONE_NOTE = {
    # gpt-image-2 now outputs native 4:5 at 2048x2560 — no crop needed.
    # Still include a tiny safe-margin nudge so models don't bleed type to canvas edge.
    "4:5": (
        "\n\n--- OUTPUT NOTE ---\n"
        "The output canvas is 4:5 portrait (2048x2560, final resize 1080x1350 IG spec). "
        "Leave at least 4% margin from every canvas edge for all critical type and logos. "
        "Bleeds on photo backgrounds are fine; type and logos must have breathing room.\n"
    ),
    "1:1": "",
    "9:16": "",
    "2:3": "",
    "3:2": "",
    "16:9": "",
}


def generate_one_openai(
    client: OpenAI,
    model: str,
    prompt_text: str,
    aspect_ratio: str,
    ref_image_bytes: Optional[bytes],
    logo_bytes: Optional[bytes] = None,
) -> Optional[bytes]:
    """Generate a single PNG via gpt-image-2.

    If ref_image_bytes is supplied, uses images.edit() (multi-image composite
    mode). Otherwise uses images.generate(). Returns raw PNG bytes or None.
    """
    size = _size_for(aspect_ratio)
    # Append safe-zone note so model composes inside the final-crop region
    prompt_text = prompt_text + _SAFE_ZONE_NOTE.get(aspect_ratio, "")

    # No reference → pure generation
    if ref_image_bytes is None and logo_bytes is None:
        resp = client.images.generate(
            model=model,
            prompt=prompt_text,
            size=size,
            n=1,
        )
        b64 = resp.data[0].b64_json
        return base64.b64decode(b64) if b64 else None

    # With reference → edit mode (supports multi-image input)
    image_files: list = []
    if ref_image_bytes is not None:
        bio = io.BytesIO(ref_image_bytes)
        bio.name = "reference.jpg"
        image_files.append(bio)
    if logo_bytes is not None:
        bio = io.BytesIO(logo_bytes)
        bio.name = "logo.png"
        image_files.append(bio)

    # SDK accepts single file or list. Pass single if only one.
    image_arg = image_files if len(image_files) > 1 else image_files[0]

    resp = client.images.edit(
        model=model,
        image=image_arg,
        prompt=prompt_text,
        size=size,
        n=1,
    )
    b64 = resp.data[0].b64_json
    return base64.b64decode(b64) if b64 else None


def generate_with_retry_openai(
    client: OpenAI,
    prompt_text: str,
    aspect_ratio: str,
    ref_image_bytes: Optional[bytes],
    logo_bytes: Optional[bytes] = None,
    primary_model: str = "gpt-image-2",
    fallback_model: str = "",
) -> tuple[Optional[bytes], str]:
    """Call gpt-image-2. Fallback only if explicitly set (default: none)."""
    models = [primary_model] + ([fallback_model] if fallback_model else [])
    for model in models:
        try:
            png = generate_one_openai(
                client, model, prompt_text, aspect_ratio,
                ref_image_bytes, logo_bytes=logo_bytes,
            )
            if png:
                return png, model
        except Exception as exc:  # noqa: BLE001
            print(f"    ! {model} errored: {type(exc).__name__}: {exc}")
            continue
    return None, ""


def build_client(api_key: str) -> OpenAI:
    return OpenAI(api_key=api_key)
