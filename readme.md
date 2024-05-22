# mkdocs-ai-summary

[![PyPI - Version](https://img.shields.io/pypi/v/mkdocs-ai-summary)](https://pypi.org/project/mkdocs-ai-summary/)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/mkdocs-ai-summary)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mkdocs-ai-summary)

Generage an **ai-summary** for the page:
![](assets/2024-05-23-04-11-20.png)

Minimal demo: [aiboy996.github.io/mkdocs-ai-summary](https://aiboy996.github.io/mkdocs-ai-summary)

Live demo(my homepage): [yangzhang.site](https://yangzhang.site)

## Installation

You should install the package with pip:
```
pip install mkdocs-ai-summary[chatgpt]
```
or
```
pip install mkdocs-ai-summary[tongyi]
```
> ⚠️⚠️⚠️⚠️
> 
> Only support [tongyi ai](https://tongyi.aliyun.com/) and [ChatGPT](https://chat.openai.com/) for now.
>  
>  To use **ChatGPT(default)**, you should set a Environmental Variable for **api key**:
>  ```bash
>  export OPENAI_API_KEY='sk-xxxxxxx'
>  ```
>
>  To use **tongyi ai**, you should set a Environmental Variable for **api key**:
>  ```bash
>  export DASHSCOPE_API_KEY='sk-xxxxxxx'
>  ```

[optional] Then you can include the [ai-summary.css](./docs/ai-summary.css)(optional, this is for the **custom  ai summary admonition style**) in the config file as below:

## Configuration

A demo for `mkdocs.yml`:

```yml
site_name: mkdocs-ai-summary
theme:
  name: material

plugins:
  - ai-summary:
      # these are all default value
      api: "chatgpt"
      model: "gpt-3.5-turbo"
      # we ignore ``` code block when do summary
      ignore_code: true 
      cache: true
      cache_dir: "./"
      prompt: "请帮我把下面的内容总结为200字以内的摘要："
  - tags

markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences
  - pymdownx.tabbed:
      alternate_style: true 
extra_css:
  - ai-summary.css
```

Then for each page you can add the ai-summary with a meta tag:
```markdown
---
include:
- ai-summary
---

# h1

....
```

or you can use **tongyi ai** by setting:
```yml
plugins:
  - ai-summary:
      api: "tongyi"
      ignore_code: true
      cache: true
      cache_dir: "./"
      prompt: "请帮我把下面的内容总结为200字以内的摘要："
```

## About Cache

Don't worry about duplicate api calls, we've made the cache function so that if you've done an ai-summary before and the content hasn't changed it will use the cache.

Enjoy it.