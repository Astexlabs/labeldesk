import base64

from labeldesk.core.models.base import BaseAdapter, ModelCfg
from labeldesk.core.models.registry import register


@register("anthropic")
class AnthropicAdapter(BaseAdapter):
    name = "anthropic"
    displayName = "Claude (Anthropic)"
    costPer1kIn = 0.0008
    costPer1kOut = 0.004

    def __init__(self, cfg: ModelCfg):
        super().__init__(cfg)
        self._client = None

    def _cli(self):
        if self._client is None:
            import anthropic
            self._client = anthropic.Anthropic(api_key=self.cfg.apiKey)
        return self._client

    def isAvail(self) -> bool:
        return bool(self.cfg.apiKey)

    def visionInfer(self, imgBytes: bytes, prompt: str, maxToks: int = 200) -> str:
        b64 = base64.standard_b64encode(imgBytes).decode()
        msg = self._cli().messages.create(
            model=self.cfg.modelId or "claude-haiku-4-5-20251001",
            max_tokens=maxToks,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
                    {"type": "text", "text": prompt},
                ],
            }],
        )
        return msg.content[0].text

    def txtInfer(self, txt: str, prompt: str, maxToks: int = 100) -> str:
        msg = self._cli().messages.create(
            model=self.cfg.modelId or "claude-haiku-4-5-20251001",
            max_tokens=maxToks,
            messages=[{"role": "user", "content": f"{prompt}\n\n{txt}"}],
        )
        return msg.content[0].text
