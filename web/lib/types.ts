export type Cred = {
  key: string; label: string; secret: boolean; hint?: string; default?: string;
};

export type Provider = {
  name: string; displayName: string; desc: string;
  creds: Cred[]; models: string[]; defaultModelId: string;
  available: boolean; missing: string[]; modelId: string; isDefault: boolean;
};

export const provColors: Record<string, string> = {
  anthropic: '#d97757', openai: '#10a37f', gemini: '#4285f4',
  groq: '#f55036', lightning: '#792ee5', ollama: '#000',
};
