import base64

from labeldesk.core.models.base import BaseAdapter, ModelCfg
from labeldesk.core.models.registry import register


@register("groq")
class GroqAdapter(BaseAdapter):
    name = "groq"
    displayName = "Groq"
    costPer1kIn = 0.00005
    costPer1kOut = 0.00008

    def __init__(self, cfg: ModelCfg):
        super().__init__(cfg)
        self._client = None

    def _cli(self):
        if self._client is None:
            from groq import Groq
            self._client = Groq(api_key=self.cfg.apiKey)
        return self._client

    def isAvail(self) -> bool:
        return bool(self.cfg.apiKey)

    def visionInfer(self, imgBytes: bytes, prompt: str, maxToks: int = 200) -> str:
        b64 = base64.b64encode(imgBytes).decode()
        resp = self._cli().chat.completions.create(
            model=self.cfg.modelId or "llama-3.2-11b-vision-preview",
            max_tokens=maxToks,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                ],
            }],
        )
        return resp.choices[0].message.content

    def txtInfer(self, txt: str, prompt: str, maxToks: int = 100) -> str:
        resp = self._cli().chat.completions.create(
            model=self.cfg.modelId or "llama-3.2-11b-vision-preview",
            max_tokens=maxToks,
            messages=[{"role": "user", "content": f"{prompt}\n\n{txt}"}],
        )
        return resp.choices[0].message.content
