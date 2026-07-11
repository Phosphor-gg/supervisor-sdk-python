"""Tests for client-side image preprocessing."""

import base64
import io

from PIL import Image

from supervisor import prepare_image


def _encode(img: Image.Image, format: str) -> str:
    buffer = io.BytesIO()
    img.save(buffer, format=format)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def _decode(image_b64: str) -> Image.Image:
    return Image.open(io.BytesIO(base64.b64decode(image_b64)))


def test_large_rgb_png_downscaled_to_jpeg():
    original = _encode(Image.new("RGB", (3000, 2000), (200, 30, 30)), "PNG")

    result = prepare_image(original)

    output = _decode(result)
    assert output.format == "JPEG"
    assert max(output.size) == 1280
    assert output.size == (1280, 853)  # 2000 * 1280/3000 = 853.33 -> 853


def test_large_rgba_png_flattened_and_downscaled():
    original = _encode(Image.new("RGBA", (4000, 1000), (0, 100, 200, 128)), "PNG")

    result = prepare_image(original)

    output = _decode(result)
    assert output.format == "JPEG"
    assert output.mode == "RGB"
    assert max(output.size) == 1280
    assert output.size == (1280, 320)  # 1000 * 1280/4000 = 320


def test_small_jpeg_dims_unchanged():
    original = _encode(Image.new("RGB", (64, 64), (10, 200, 10)), "JPEG")

    result = prepare_image(original)

    output = _decode(result)
    assert output.size == (64, 64)


def test_garbage_input_returned_unchanged():
    assert prepare_image("not base64!!!") == "not base64!!!"

    text_b64 = base64.b64encode(b"just some text, not an image").decode("ascii")
    assert prepare_image(text_b64) == text_b64


def test_data_uri_prefix_stripped():
    original = _encode(Image.new("RGB", (3000, 2000), (50, 50, 50)), "PNG")

    result = prepare_image(f"data:image/png;base64,{original}")

    assert not result.startswith("data:")
    output = _decode(result)
    assert output.format == "JPEG"
    assert max(output.size) == 1280
