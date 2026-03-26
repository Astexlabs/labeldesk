from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image
from PIL.ExifTags import TAGS
import numpy as np


@dataclass
class FreeSignals:
    width: int = 0
    height: int = 0
    aspect: str = "unknown"
    brightness: str = "mid"
    dominant: tuple[int, int, int] = (128, 128, 128)
    isMono: bool = False
    isSolid: bool = False
    edgeDensity: float = 0.0
    exif: dict = field(default_factory=dict)
    gps: dict = field(default_factory=dict)
    camModel: str = ""
    focalLen: str = ""
    software: str = ""
    fnameHints: list[str] = field(default_factory=list)
    folderHints: list[str] = field(default_factory=list)
    timeHint: str = ""


def _classifyAspect(w, h):
    r = w / h if h else 1
    if r > 2.5:
        return "panoramic"
    if r > 1.2:
        return "landscape"
    if r < 0.5:
        return "banner"
    if r < 0.85:
        return "portrait"
    return "square"


def _classifyBrightness(img):
    grey = img.convert("L")
    hist = grey.histogram()
    total = sum(hist)
    if total == 0:
        return "mid"
    weightedSum = sum(i * v for i, v in enumerate(hist))
    avg = weightedSum / total
    if avg > 190:
        return "high-key"
    if avg < 60:
        return "dark"
    if avg < 30:
        return "silhouette"
    return "mid"


def _dominantColor(img):
    small = img.resize((16, 16)).convert("RGB")
    px = np.array(small).reshape(-1, 3)
    avg = tuple(int(c) for c in px.mean(axis=0))
    return avg


def _checkMono(img):
    small = img.resize((32, 32)).convert("RGB")
    px = np.array(small).reshape(-1, 3)
    stds = px.std(axis=0)
    return bool(stds.max() < 30)


def _checkSolid(img):
    small = img.resize((8, 8)).convert("RGB")
    px = np.array(small).reshape(-1, 3)
    perChannel = px.std(axis=0)
    return bool(perChannel.max() < 10)


def _edgeDensity(img):
    grey = np.array(img.convert("L").resize((64, 64)), dtype=np.float32)
    kx = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float32)
    ky = kx.T
    from scipy.signal import convolve2d

    gx = convolve2d(grey, kx, mode="valid")
    gy = convolve2d(grey, ky, mode="valid")
    mag = np.sqrt(gx**2 + gy**2)
    return float(mag.mean() / 255.0)


def _parseExif(img):
    raw = img.getexif()
    if not raw:
        return {}, {}, "", "", ""
    parsed = {}
    for k, v in raw.items():
        tag = TAGS.get(k, k)
        parsed[str(tag)] = str(v)
    cam = parsed.get("Model", "")
    focal = parsed.get("FocalLength", "")
    sw = parsed.get("Software", "")
    gps = {}
    if 34853 in raw:
        gps = {str(k): str(v) for k, v in raw.get_ifd(34853).items()}
    return parsed, gps, cam, focal, sw


def _fnameHints(p: Path):
    stem = p.stem.lower()
    hints = []
    if stem.startswith("img_") or stem.startswith("dsc"):
        hints.append("camera-photo")
    if "screenshot" in stem:
        hints.append("screenshot")
    if "photo" in stem:
        hints.append("photo")
    if "scan" in stem:
        hints.append("scanned")
    return hints


def _folderHints(p: Path):
    parts = [part.lower() for part in p.parent.parts[-3:]]
    return parts


def extractSignals(imgPath: str | Path) -> FreeSignals:
    """pull all free info from an img w/o any ai"""
    p = Path(imgPath)
    img = Image.open(p)
    w, h = img.size
    exif, gps, cam, focal, sw = _parseExif(img)
    return FreeSignals(
        width=w,
        height=h,
        aspect=_classifyAspect(w, h),
        brightness=_classifyBrightness(img),
        dominant=_dominantColor(img),
        isMono=_checkMono(img),
        isSolid=_checkSolid(img),
        edgeDensity=_edgeDensity(img),
        exif=exif,
        gps=gps,
        camModel=cam,
        focalLen=focal,
        software=sw,
        fnameHints=_fnameHints(p),
        folderHints=_folderHints(p),
    )
