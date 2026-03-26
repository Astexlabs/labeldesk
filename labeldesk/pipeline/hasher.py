from dataclasses import dataclass
from pathlib import Path

import imagehash
from PIL import Image


@dataclass
class HashResult:
    phash: str
    exactDupes: list[str]
    nearDupes: list[str]


class ImgHasher:
    def __init__(self, threshold: int = 8):
        self._store: dict[str, str] = {}
        self._thresh = threshold

    def computeHash(self, imgPath: str | Path) -> str:
        img = Image.open(imgPath)
        return str(imagehash.phash(img))

    def findDupes(self, imgPath: str | Path) -> HashResult:
        h = self.computeHash(imgPath)
        exact, near = [], []
        hObj = imagehash.hex_to_hash(h)
        for storedHash, storedPath in self._store.items():
            dist = hObj - imagehash.hex_to_hash(storedHash)
            if dist == 0:
                exact.append(storedPath)
            elif dist < self._thresh:
                near.append(storedPath)
        self._store[h] = str(imgPath)
        return HashResult(phash=h, exactDupes=exact, nearDupes=near)

    def register(self, phash: str, imgPath: str):
        self._store[phash] = imgPath

    def clear(self):
        self._store.clear()
