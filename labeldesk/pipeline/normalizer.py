import io
from pathlib import Path

from PIL import Image, ImageOps


def normalizeImg(imgPath: str | Path, maxSide: int = 768, quality: int = 75) -> bytes:
    """resize + convert to jpeg for cheapest ai ingestion"""
    img = Image.open(imgPath)
    img = ImageOps.exif_transpose(img)
    if img.mode != "RGB":
        img = img.convert("RGB")
    w, h = img.size
    if max(w, h) > maxSide:
        scale = maxSide / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def compressToTarget(imgBytes: bytes, targetKb: int = 150, minQ: int = 40) -> bytes:
    """progressive jpeg compression till under target"""
    if len(imgBytes) <= targetKb * 1024:
        return imgBytes
    img = Image.open(io.BytesIO(imgBytes))
    q = 75
    while q >= minQ:
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=q, optimize=True)
        out = buf.getvalue()
        if len(out) <= targetKb * 1024:
            return out
        q -= 5
    return out
