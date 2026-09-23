# mkdocs-ai-summary

[![PyPI - Version](https://img.shields.io/pypi/v/mkdocs-ai-summary)](https://pypi.org/project/mkdocs-ai-summary/)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/mkdocs-ai-summary)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mkdocs-ai-summary)

`mkdocs-ai-summary` is a MkDocs plugin that generates an AI summary for selected Markdown pages and inserts it into the rendered page.

![AI summary example](assets/2024-05-23-04-35-01.png)

## Demos

- Minimal MkDocs example: [mkdocs-ai-summary-minimal-example](https://aiboy996.github.io/mkdocs-ai-summary-minimal-example/)
- MkDocs Material example: [project demo](https://aiboy996.github.io/mkdocs-ai-summary)
- In use on [yangzhang.site](https://yangzhang.site)

## Installation

Install the extra for the provider you plan to use. ChatGPT and DeepSeek use the OpenAI Python SDK; Tongyi uses DashScope.

```bash
pip install 'mkdocs-ai-summary[chatgpt]'
# or
pip install 'mkdocs-ai-summary[deepseek]'
# or
pip install 'mkdocs-ai-summary[tongyi]'
```

Set the provider's API key in the environment where you run `mkdocs build` or `mkdocs serve`:

```bash
export OPENAI_API_KEY="..."       # ChatGPT
export DEEPSEEK_API_KEY="..."     # DeepSeek
export DASHSCOPE_API_KEY="..."    # Tongyi
```

## Configuration

Add the plugin to `mkdocs.yml`. The plugin is enabled site-wide, but it only requests a summary for pages that opt in with `include: [ai-summary]`.

```yaml
plugins:
  - search
  - ai-summary:
      api: chatgpt
      ignore_code: true
      cache: true
      cache_dir: .
      prompt: "Summarize the following page in its original language, in no more than 200 words:"

extra_css:
  - ai-summary.css
```

Then add this front matter to each page that should receive a summary:

```yaml
---
include:
  - ai-summary
---

# Page title

Page content goes here.
```

### Options

All options can be set under `plugins: - ai-summary:` and overridden per page using `ai-summary-config` front matter. Page values take precedence over site-level values.

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `api` | string | `chatgpt` | Provider: `chatgpt`, `deepseek`, or `tongyi`. |
| `api_key` | string | Empty string | For `chatgpt` and `deepseek`, this is an **environment variable name**, not the secret itself (for example, `OPENROUTER_API_KEY`). When omitted, the client uses the environment variable listed below. Tongyi uses `DASHSCOPE_API_KEY` through DashScope. |
| `base_url` | string | See provider defaults below | OpenAI-compatible endpoint; used by `chatgpt` and `deepseek`. Tongyi does not use this option. |
| `provider_name` | string | See provider defaults below | Prefix for the admonition CSS class. The plugin appends `-summary`; for example, `openrouter` produces `openrouter-summary`. |
| `provider_title` | string | See provider defaults below | Display name in the “AI Summary powered by …” attribution. |
| `provider_link` | string | See provider defaults below | Destination linked from the attribution. |
| `model` | string | See provider defaults below | Model identifier accepted by the selected provider. |
| `ignore_code` | boolean | `true` | Exclude triple-backtick code blocks from the text sent for summarization. |
| `cache` | boolean | `true` | Reuse a cached summary when the page content has not changed. |
| `cache_dir` | string | `./` | Directory where the cache JSON file is stored. |
| `prompt` | string | See below | Text prepended to the page content in the request. |

The default prompt is `Please help me summarize the following content into an abstract within 200 words:`. If a prompt does not end with a colon, the plugin adds one before the page text.

The table below combines each provider's default model, API key environment variable, endpoint, and attribution. Model availability can change; set `model` to one supported by your provider account.

| `api` | Default `model` | Environment variable when `api_key` is empty | Default/effective `base_url` | Default attribution (`provider_name`; `provider_title`; `provider_link`) |
| --- | --- | --- | --- | --- |
| `chatgpt` | `gpt-3.5-turbo` | `OPENAI_API_KEY` | OpenAI SDK default endpoint | `chatgpt`; `ChatGPT`; `https://chat.openai.com/` |
| `chatgpt` with custom `base_url` | `gpt-3.5-turbo` | `OPENAI_API_KEY`, or the variable named by `api_key` | Configured `base_url` | `custom-provider`; `Custom Provider`; configured `base_url` |
| `deepseek` | `deepseek-flash` | `DEEPSEEK_API_KEY` | `https://api.deepseek.com` | `deepseek`; `DeepSeek`; `https://www.deepseek.com/` |
| `deepseek` with non-default `base_url` | `deepseek-flash` | `DEEPSEEK_API_KEY`, or the variable named by `api_key` | Configured `base_url` | `custom-provider`; `Custom Provider`; configured `base_url` |
| `tongyi` | `qwen-turbo` | `DASHSCOPE_API_KEY` | Not used | `tongyiai`; `通义千问`; `https://tongyi.aliyun.com/` |

Each `provider_*` option can override its corresponding default independently, at either site or page level. For example, changing only `provider_title` leaves the automatically selected class name and link unchanged. `base_url` does not select a provider or infer a brand; custom endpoints receive the generic attribution above unless you set explicit `provider_*` values.

### Choose a provider

For Tongyi, set `api: tongyi`. Model and key defaults are listed above:

```yaml
plugins:
  - ai-summary:
      api: tongyi
```

For DeepSeek, set `api: deepseek`. Its default model, endpoint, and API key environment variable are listed above:

```yaml
plugins:
  - ai-summary:
      api: deepseek
```

You can also use an OpenAI-compatible endpoint such as OpenRouter with `api: chatgpt`. Set `api_key` to the name of an environment variable and provide the endpoint and a model identifier supported by that service. The example sets all three attribution options so the summary identifies OpenRouter instead of using the generic custom endpoint defaults:

```yaml
---
include:
  - ai-summary
ai-summary-config:
  api: chatgpt
  api_key: OPENROUTER_API_KEY
  base_url: https://openrouter.ai/api/v1
  model: YOUR_PROVIDER_MODEL_ID
  provider_name: openrouter
  provider_title: OpenRouter
  provider_link: https://openrouter.ai/
  prompt: "Summarize this page in no more than 200 words:"
---
```

`api_key` must contain the environment variable's name; never put the secret directly in Markdown or `mkdocs.yml`.

### Styling

The plugin emits a MkDocs admonition. To use the included [ai-summary.css](docs/ai-summary.css), copy it into your documentation directory and list it under `extra_css`, for example `extra_css: [ai-summary.css]`. This is optional and is most useful with the Material theme.

## Cache

With caching enabled, summaries are stored as provider-specific JSON files in `cache_dir` (the current working directory by default; the directory is created if needed). Cache entries are keyed by page title and compare only the MD5 hash of the Markdown body after `ignore_code` processing, before adding the prompt or applying provider-specific length truncation. Changes to the prompt, model, endpoint, or other configuration do not invalidate the cache; delete the provider's cache file to force regeneration with new settings. When `ignore_code` is true, triple-backtick code blocks are excluded from the content being hashed. Cache files may contain generated summaries; do not commit them if your page content is private.

## Thanks

- [MkDocs](https://www.mkdocs.org/)
- [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)
