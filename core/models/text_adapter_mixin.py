from abc import abstractmethod


class TxtAdapterMixin:
    """mixin so adapters can expose a cheap txt-only path"""

    @abstractmethod
    def txtInfer(self, txt: str, prompt: str, maxToks: int = 100) -> str:
        ...

    @abstractmethod
    def visionInfer(self, imgBytes: bytes, prompt: str, maxToks: int = 200) -> str:
        ...

    def canTxt(self) -> bool:
        return True
