import base64
import json
import urllib.request

from labeldesk.core.models.base import BaseAdapter, ModelCfg
from labeldesk.core.models.registry import register


@register("lightning")
class LightningAdapter(BaseAdapter):
    name = "lightning"
    displayName = "Lightning AI"
    costPer1kIn = 0.0001
    costPer1kOut = 0.0003

    def isAvail(self) -> bool:
        return bool(self.cfg.apiKey and self.cfg.host)

    def _host(self) -> str:
        return self.cfg.host.rstrip("/")

    def _call(self, payload: dict) -> str:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            f"{self._host()}/v1/chat/completions",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.cfg.apiKey}",
            },
        )
        with urllib.request.urlopen(req, timeout=120) as r:
            body = json.loads(r.read())
        return body["choices"][0]["message"]["content"]

    def visionInfer(self, imgBytes: bytes, prompt: str, maxToks: int = 200) -> str:
        b64 = base64.b64encode(imgBytes).decode()
        return self._call({
            "model": self.cfg.modelId or "lightning-vision",
            "max_tokens": maxToks,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                ],
            }],
        })

    def txtInfer(self, txt: str, prompt: str, maxToks: int = 100) -> str:
        return self._call({
            "model": self.cfg.modelId or "lightning-vision",
            "max_tokens": maxToks,
            "messages": [{"role": "user", "content": f"{prompt}\n\n{txt}"}],
        })
