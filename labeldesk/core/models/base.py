from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ModelCfg:
    apiKey: str = ""
    modelId: str = ""
    maxToks: int = 300
    temp: float = 0.2
    host: str = ""


class TxtAdapterMixin:
    """cheap txt-only path"""

    def canTxt(self) -> bool:
        return True

    @abstractmethod
    def txtInfer(self, txt: str, prompt: str, maxToks: int = 100) -> str: ...


class BaseAdapter(ABC, TxtAdapterMixin):
    name: str = "base"
    displayName: str = "Base"
    costPer1kIn: float = 0.0
    costPer1kOut: float = 0.0

    def __init__(self, cfg: ModelCfg):
        self.cfg = cfg

    @abstractmethod
    def isAvail(self) -> bool: ...

    @abstractmethod
    def visionInfer(self, imgBytes: bytes, prompt: str, maxToks: int = 200) -> str: ...

    def estimateCost(self, nImgs: int, mode: str) -> float:
        toksPerImg = {"title": 150, "description": 300, "both": 400, "tags": 100, "full": 500}
        toks = toksPerImg.get(mode, 300) * nImgs
        return (toks / 1000) * (self.costPer1kIn + self.costPer1kOut)
