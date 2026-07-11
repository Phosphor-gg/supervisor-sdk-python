"""Client-side image preprocessing for moderation requests."""

from __future__ import annotations

import base64
import io

MAX_EDGE = 1280
JPEG_QUALITY = 85


def prepare_image(image_b64: str) -> str:
    """Downscale and re-encode a base64 image before sending it to the API.

    Decodes the input, resizes it so the longest edge is at most 1280 pixels
    (aspect ratio preserved, never upscaled), flattens any alpha channel onto
    a white background, and re-encodes it as JPEG. This reduces upload size
    and request latency without affecting moderation quality.

    Args:
        image_b64: Base64-encoded image, optionally with a
            ``data:...;base64,`` prefix.

    Returns:
        The processed image as standard base64 (no data URI prefix). If the
        input cannot be decoded as an image, or if re-encoding would not
        shrink an already-small image, the original input is returned
        unchanged.
    """
    try:
        from PIL import Image
    except ImportError:
        return image_b64

    payload = image_b64
    if payload.lstrip().startswith("data:"):
        _, _, payload = payload.partition(",")

    try:
        raw = base64.b64decode("".join(payload.split()), validate=True)
        with Image.open(io.BytesIO(raw)) as img:
            # Animated images (GIF/webp): use the first frame.
            if getattr(img, "is_animated", False):
                img.seek(0)
            img.load()

            resized = False
            if max(img.width, img.height) > MAX_EDGE:
                scale = MAX_EDGE / max(img.width, img.height)
                new_size = (
                    max(1, round(img.width * scale)),
                    max(1, round(img.height * scale)),
                )
                # Ensure the longest edge lands exactly on MAX_EDGE.
                if img.width >= img.height:
                    new_size = (MAX_EDGE, new_size[1])
                else:
                    new_size = (new_size[0], MAX_EDGE)
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                resized = True

            # Flatten alpha onto a white background and convert to RGB.
            if img.mode in ("RGBA", "LA", "PA") or (
                img.mode == "P" and "transparency" in img.info
            ):
                rgba = img.convert("RGBA")
                background = Image.new("RGB", rgba.size, (255, 255, 255))
                background.paste(rgba, mask=rgba.getchannel("A"))
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True)
            encoded = buffer.getvalue()
    except Exception:
        return image_b64

    # Don't inflate images that were already small and well-compressed.
    if not resized and len(encoded) >= len(raw):
        return image_b64

    return base64.b64encode(encoded).decode("ascii")
