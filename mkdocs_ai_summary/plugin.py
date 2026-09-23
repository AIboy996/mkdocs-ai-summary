from mkdocs import plugins
from mkdocs.config import config_options
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.exceptions import ConfigurationError
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page

import re
import logging


logger = logging.getLogger("mkdocs.plugins.ai-summary")


class AiSummaryPlugin(BasePlugin):
    config_scheme = (
        (
            "api",
            config_options.Choice(["chatgpt", "tongyi", "deepseek"], default="chatgpt"),
        ),
        ("ignore_code", config_options.Type(bool, default=True)),
        ("cache", config_options.Type(bool, default=True)),
        ("cache_dir", config_options.Type(str, default="./")),
        ("api_key", config_options.Type(str, default="")),
        ("base_url", config_options.Type(str, default="")),
        ("provider_name", config_options.Type(str, default="")),
        ("provider_title", config_options.Type(str, default="")),
        ("provider_link", config_options.Type(str, default="")),
        ("model", config_options.Type(str, default="")),
        (
            "prompt",
            config_options.Type(
                str,
                default="Please help me summarize the following content into an "
                "abstract within 200 words: ",
            ),
        ),
    )

    @plugins.event_priority(50)
    def on_page_markdown(
        self, markdown: str, *, page: Page, config: MkDocsConfig, files: Files
    ) -> str | None:
        # add ai-summary only when meta info say it is included
        if page.meta:
            if "ai-summary" not in page.meta.get("include", {}):
                return markdown
            page_config = page.meta.get("ai-summary-config", {})
            api = page_config.get("api", self.config["api"])
            ignore_code = page_config.get("ignore_code", self.config["ignore_code"])
            prompt = page_config.get("prompt", self.config["prompt"])
            cache = page_config.get("cache", self.config["cache"])
            cache_dir = page_config.get("cache_dir", self.config["cache_dir"])
            api_key = page_config.get("api_key", self.config["api_key"])
            base_url = page_config.get("base_url", self.config["base_url"])
            provider_name = page_config.get("provider_name", self.config["provider_name"])
            provider_title = page_config.get("provider_title", self.config["provider_title"])
            provider_link = page_config.get("provider_link", self.config["provider_link"])
            model = page_config.get("model", self.config["model"])
        else:
            return markdown
        # use api to get ai summary
        markdown_to_summary = markdown
        if ignore_code:
            # delete code block
            pattern = re.compile("```.*?```", re.S)
            markdown_to_summary = re.sub(pattern, "", markdown)
        match api:
            case "tongyi":
                effective_provider_name = provider_name or "tongyiai"
                effective_provider_title = provider_title or "通义千问"
                effective_provider_link = provider_link or "https://tongyi.aliyun.com/"
                try:
                    from .tongyi_api import get_summary, AiSummaryRequestError
                except ImportError as e:
                    logger.warning("tongyi is not available", repr(e))
                    return markdown

                logger.info(f"Asking AI summary for page [{page.title}]({page.url})")
                try:
                    summary = get_summary(
                        page=str(page.title),
                        prompt=prompt,
                        markdown=markdown_to_summary,
                        cache=cache,
                        cache_dir=cache_dir,
                        model=model or "qwen-turbo",
                        logger=logger,
                        provider_name=effective_provider_name,
                        provider_title=effective_provider_title,
                        provider_link=effective_provider_link,
                    )
                except AiSummaryRequestError as e:
                    logger.warning("Request Tongyi AI Error", repr(e))
                    return markdown
                except Exception as e:
                    logger.warning(repr(e))
                    return markdown
            case "chatgpt":
                custom_endpoint = bool(base_url)
                effective_provider_name = provider_name or (
                    "custom-provider" if custom_endpoint else "chatgpt"
                )
                effective_provider_title = provider_title or (
                    "Custom Provider" if custom_endpoint else "ChatGPT"
                )
                effective_provider_link = provider_link or (
                    base_url if custom_endpoint else "https://chat.openai.com/"
                )
                try:
                    from .chatgpt_api import get_summary
                except ImportError as e:
                    logger.warning("chatgpt is not available", repr(e))
                    return markdown

                logger.info(f"Asking AI summary for page [{page.title}]({page.url})")
                try:
                    summary = get_summary(
                        page=str(page.title),
                        prompt=prompt,
                        markdown=markdown_to_summary,
                        cache=cache,
                        cache_dir=cache_dir,
                        model=model or "gpt-3.5-turbo",
                        logger=logger,
                        api_key=api_key,
                        base_url=base_url,
                        provider_name=effective_provider_name,
                        provider_title=effective_provider_title,
                        provider_link=effective_provider_link,
                    )
                except Exception as e:
                    logger.warning(repr(e))
                    return markdown
            case "deepseek":
                custom_endpoint = bool(
                    base_url and base_url.rstrip("/") != "https://api.deepseek.com"
                )
                effective_provider_name = provider_name or (
                    "custom-provider" if custom_endpoint else "deepseek"
                )
                effective_provider_title = provider_title or (
                    "Custom Provider" if custom_endpoint else "DeepSeek"
                )
                effective_provider_link = provider_link or (
                    base_url if custom_endpoint else "https://www.deepseek.com/"
                )
                # deepseek is OpenAI-compatible, reuse the openai sdk via chatgpt_api
                try:
                    from .chatgpt_api import get_summary
                except ImportError as e:
                    logger.warning("deepseek is not available", repr(e))
                    return markdown

                logger.info(f"Asking AI summary for page [{page.title}]({page.url})")
                try:
                    summary = get_summary(
                        page=str(page.title),
                        prompt=prompt,
                        markdown=markdown_to_summary,
                        cache=cache,
                        cache_dir=cache_dir,
                        model=model or "deepseek-flash",
                        logger=logger,
                        api_key=api_key or "DEEPSEEK_API_KEY",
                        base_url=base_url or "https://api.deepseek.com",
                        cache_suffix="_ai_summary_cache_deepseek.json",
                        provider_name=effective_provider_name,
                        provider_title=effective_provider_title,
                        provider_link=effective_provider_link,
                    )
                except Exception as e:
                    logger.warning(repr(e))
                    return markdown
            case _:
                e = repr(ConfigurationError("unrecongnized api config."))
                logger.warning(repr(e))
                return markdown
        h1 = re.match(r"^# .*?\n", markdown)
        # if h1 exists, then insert summary after h1
        if h1:
            markdown = markdown[: h1.end()] + summary + markdown[h1.end() :]
        # else insert summary at the first beginning
        else:
            markdown = summary + markdown
        return markdown
