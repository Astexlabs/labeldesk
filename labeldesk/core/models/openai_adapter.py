import base64

from labeldesk.core.models.base import BaseAdapter, ModelCfg
from labeldesk.core.models.registry import register


@register("openai")
class OpenAIAdapter(BaseAdapter):
    name = "openai"
    displayName = "GPT (OpenAI)"
    costPer1kIn = 0.00015
    costPer1kOut = 0.0006

    def __init__(self, cfg: ModelCfg):
        super().__init__(cfg)
        self._client = None

    def _cli(self):
        if self._client is None:
            import openai
            self._client = openai.OpenAI(api_key=self.cfg.apiKey)
        return self._client

    def isAvail(self) -> bool:
        return bool(self.cfg.apiKey)

    def visionInfer(self, imgBytes: bytes, prompt: str, maxToks: int = 200) -> str:
        b64 = base64.b64encode(imgBytes).decode()
        resp = self._cli().chat.completions.create(
            model=self.cfg.modelId or "gpt-4o-mini",
            max_tokens=maxToks,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}", "detail": "low"}},
                ],
            }],
        )
        return resp.choices[0].message.content

    def txtInfer(self, txt: str, prompt: str, maxToks: int = 100) -> str:
        resp = self._cli().chat.completions.create(
            model=self.cfg.modelId or "gpt-4o-mini",
            max_tokens=maxToks,
            messages=[{"role": "user", "content": f"{prompt}\n\n{txt}"}],
        )
        return resp.choices[0].message.content
