from pathlib import Path

import numpy as np
from PIL import Image

from labeldesk.core.models.categories import ImgCat

_CAT_MAP = {
    "screenshot": ImgCat.screenshot, "document": ImgCat.document,
    "face": ImgCat.face, "outdoor": ImgCat.outdoor, "indoor": ImgCat.indoor,
    "food": ImgCat.food, "product": ImgCat.product, "abstract": ImgCat.abstract,
    "diagram": ImgCat.diagram, "icon": ImgCat.icon,
}
_LABELS = list(_CAT_MAP.keys()) + ["generic"]


class LocalClassifier:
    """wraps onnx mobilenet for quick local img classification"""

    def __init__(self, modelPath: str | None = None):
        self._session = None
        self._modelPath = modelPath

    def _loadModel(self):
        if self._session is not None or self._modelPath is None:
            return
        import onnxruntime as ort
        self._session = ort.InferenceSession(self._modelPath)

    def _preprocess(self, imgPath: str | Path) -> np.ndarray:
        img = Image.open(imgPath).convert("RGB").resize((224, 224))
        arr = np.array(img, dtype=np.float32) / 255.0
        arr = (arr - np.array([0.485, 0.456, 0.406])) / np.array([0.229, 0.224, 0.225])
        arr = arr.transpose(2, 0, 1)
        return np.expand_dims(arr, 0).astype(np.float32)

    def classify(self, imgPath: str | Path) -> ImgCat:
        self._loadModel()
        if self._session is None:
            return ImgCat.generic
        inp = self._preprocess(imgPath)
        inName = self._session.get_inputs()[0].name
        out = self._session.run(None, {inName: inp})
        topIdx = int(np.argmax(out[0][0]))
        if topIdx < len(_LABELS):
            return _CAT_MAP.get(_LABELS[topIdx], ImgCat.generic)
        return ImgCat.generic

    def classifyFromSignals(self, signals) -> ImgCat:
        """fallback classifier using free signals when no onnx model"""
        if "screenshot" in signals.fnameHints:
            return ImgCat.screenshot
        if "scanned" in signals.fnameHints:
            return ImgCat.document
        if signals.isSolid:
            return ImgCat.icon
        if signals.software and any(
            s in signals.software.lower()
            for s in ["screenshot", "snip", "grab", "flameshot"]
        ):
            return ImgCat.screenshot
        if signals.edgeDensity < 0.05 and signals.isMono:
            return ImgCat.document
        if signals.aspect == "panoramic":
            return ImgCat.outdoor
        return ImgCat.generic
