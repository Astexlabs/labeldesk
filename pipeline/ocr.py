from pathlib import Path

from PIL import Image


def extractTxt(imgPath: str | Path) -> str:
    """run tesseract ocr on img, returns raw txt"""
    import pytesseract

    img = Image.open(imgPath)
    txt = pytesseract.image_to_string(img)
    return txt.strip()


def summarizeTxt(raw: str, maxLen: int = 300) -> str:
    """trim ocr output to something usable as prompt ctx"""
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    out = " ".join(lines)
    if len(out) > maxLen:
        out = out[:maxLen] + "..."
    return out
