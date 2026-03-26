import base64
import json
import urllib.request

from labeldesk.core.models.base import BaseAdapter, ModelCfg
from labeldesk.core.models.registry import register


@register("ollama")
class OllamaAdapter(BaseAdapter):
    name = "ollama"
    displayName = "Ollama (local)"
    costPer1kIn = 0.0
    costPer1kOut = 0.0

    def isAvail(self) -> bool:
        try:
            req = urllib.request.Request(f"{self._host()}/api/tags")
            urllib.request.urlopen(req, timeout=2)
            return True
        except Exception:
            return False

    def _host(self) -> str:
        return self.cfg.host or "http://localhost:11434"

    def _call(self, payload: dict) -> str:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            f"{self._host()}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=120) as r:
            body = json.loads(r.read())
        return body.get("response", "")

    def visionInfer(self, imgBytes: bytes, prompt: str, maxToks: int = 200) -> str:
        b64 = base64.b64encode(imgBytes).decode()
        return self._call({
            "model": self.cfg.modelId or "llava",
            "prompt": prompt,
            "images": [b64],
            "stream": False,
            "options": {"num_predict": maxToks},
        })

    def txtInfer(self, txt: str, prompt: str, maxToks: int = 100) -> str:
        return self._call({
            "model": self.cfg.modelId or "llava",
            "prompt": f"{prompt}\n\n{txt}",
            "stream": False,
            "options": {"num_predict": maxToks},
        })
