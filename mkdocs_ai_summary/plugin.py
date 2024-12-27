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
        ("api", config_options.Choice(["chatgpt", "tongyi"], default="chatgpt")),
        ("ignore_code", config_options.Type(bool, default=True)),
        ("cache", config_options.Type(bool, default=True)),
        ("cache_dir", config_options.Type(str, default="./")),
        (
            "model",
            config_options.Type(str, default="gpt-3.5-turbo"),
        ),
        (
            "prompt",
            config_options.Type(
                str,
                default="Please help me summarize the following content into an"
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
            model = page_config.get("model", self.config["model"])
        else:
            return markdown
        # use api to get ai summary
        if ignore_code:
            # delete code block
            pattern = re.compile("```.*?```", re.S)
            markdown_to_summary = re.sub(pattern, "", markdown)
        match api:
            case "tongyi":
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
                        model=model,
                        logger=logger,
                    )
                except AiSummaryRequestError as e:
                    logger.warning("Request Tongyi AI Error", repr(e))
                    return markdown
                except Exception as e:
                    logger.warning(repr(e))
                    return markdown
            case "chatgpt":
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
                        model=model,
                        logger=logger,
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
