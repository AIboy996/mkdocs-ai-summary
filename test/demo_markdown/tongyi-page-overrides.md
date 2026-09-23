---
include:
  - ai-summary
ai-summary-config:
  api: tongyi
  model: page-qwen-model
  ignore_code: false
  cache: false
  prompt: "Tongyi page instruction"
  provider_name: page-tongyi
  provider_title: Tongyi Test
  provider_link: https://tongyi.example/
---

# Tongyi Page Overrides

Tongyi uses the page-level prompt and model.
```python
TONGYI_CODE_SENTINEL = "must be included"
```
