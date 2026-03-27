import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'labeldesk',
  description: 'Smart image labeling pipeline with cascading cost optimization',
  base: '/labeldesk/',
  cleanUrls: true,
  themeConfig: {
    nav: [
      { text: 'Guide', link: '/guide/getting-started' },
      { text: 'CLI Reference', link: '/reference/cli' },
      { text: 'Providers', link: '/providers/' },
      { text: 'GitHub', link: 'https://github.com/Astexlabs/labeldesk' },
    ],
    sidebar: {
      '/guide/': [
        {
          text: 'Guide',
          items: [
            { text: 'Getting Started', link: '/guide/getting-started' },
            { text: 'Installation', link: '/guide/installation' },
            { text: 'Architecture', link: '/guide/architecture' },
            { text: 'Label Schema', link: '/guide/schema' },
            { text: 'Web Dashboard', link: '/guide/web' },
            { text: 'Deployment', link: '/guide/deployment' },
          ],
        },
      ],
      '/reference/': [
        {
          text: 'Reference',
          items: [
            { text: 'CLI Commands', link: '/reference/cli' },
            { text: 'Configuration', link: '/reference/config' },
            { text: 'Output Formats', link: '/reference/output' },
            { text: 'HTTP API', link: '/reference/api' },
          ],
        },
      ],
      '/providers/': [
        {
          text: 'Providers',
          items: [
            { text: 'Overview', link: '/providers/' },
            { text: 'Anthropic', link: '/providers/anthropic' },
            { text: 'OpenAI', link: '/providers/openai' },
            { text: 'Google Gemini', link: '/providers/gemini' },
            { text: 'Groq', link: '/providers/groq' },
            { text: 'Lightning AI', link: '/providers/lightning' },
            { text: 'Ollama (local)', link: '/providers/ollama' },
          ],
        },
      ],
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/Astexlabs/labeldesk' },
    ],
    footer: {
      message: 'Released under the MIT License.',
    },
    search: { provider: 'local' },
  },
})
