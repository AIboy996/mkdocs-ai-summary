---
include:
  - ai-summary
ai-summary-config:
  api: deepseek
  api_key: PAGE_DEEPSEEK_KEY
  base_url: https://deepseek-proxy.example/v1
  model: page-deepseek-model
  ignore_code: false
  cache: false
  prompt: "DeepSeek page instruction"
  provider_name: page-deepseek
  provider_title: DeepSeek Proxy
  provider_link: https://deepseek-proxy.example/
---

# DeepSeek Page Overrides

This page overrides the DeepSeek model and endpoint.
```python
DEEPSEEK_PAGE_CODE_SENTINEL = "must be included"
```
