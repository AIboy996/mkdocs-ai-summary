---
include:
  - ai-summary
ai-summary-config:
  api: chatgpt
  api_key: PAGE_OPENAI_KEY
  base_url: https://chat-proxy.example/v1
  model: page-chat-model
  ignore_code: false
  cache: false
  cache_dir: .test-cache/page
  prompt: "Page-specific instruction:"
  provider_name: test-gateway
  provider_title: Test Gateway
  provider_link: https://chat-proxy.example/
---

# ChatGPT Page Overrides

Page-level options override the site-level values.

```python
PAGE_CODE_SENTINEL = "must be included"
```
