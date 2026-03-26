from labeldesk.core.models.base import BaseAdapter, ModelCfg
from labeldesk.core.models.registry import register


@register("gemini")
class GeminiAdapter(BaseAdapter):
    name = "gemini"
    displayName = "Gemini (Google)"
    costPer1kIn = 0.000075
    costPer1kOut = 0.0003

    def __init__(self, cfg: ModelCfg):
        super().__init__(cfg)
        self._model = None

    def _mdl(self):
        if self._model is None:
            import google.generativeai as genai
            genai.configure(api_key=self.cfg.apiKey)
            self._model = genai.GenerativeModel(self.cfg.modelId or "gemini-1.5-flash")
        return self._model

    def isAvail(self) -> bool:
        return bool(self.cfg.apiKey)

    def visionInfer(self, imgBytes: bytes, prompt: str, maxToks: int = 200) -> str:
        resp = self._mdl().generate_content(
            [{"mime_type": "image/jpeg", "data": imgBytes}, prompt],
            generation_config={"max_output_tokens": maxToks},
        )
        return resp.text

    def txtInfer(self, txt: str, prompt: str, maxToks: int = 100) -> str:
        resp = self._mdl().generate_content(
            f"{prompt}\n\n{txt}",
            generation_config={"max_output_tokens": maxToks},
        )
        return resp.text
