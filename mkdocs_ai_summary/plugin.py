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
        ("api", config_options.Type(str, default="chatgpt")),
        ("ignore_code", config_options.Type(bool, default=True)),
        ("cache", config_options.Type(bool, default=True)),
        ("cache_dir", config_options.Type(str, default="./")),
        (
            "model",
            config_options.Type(str, default="gpt-3.5-turbo"),
        ),  # only used for gptapi
        (
            "prompt",
            config_options.Type(
                str, default="请帮我把下面的内容总结为200字以内的摘要："
            ),
        ),
    )

    def on_page_markdown(
        self, markdown: str, *, page: Page, config: MkDocsConfig, files: Files
    ) -> str | None:
        # add ai-summary only when meta info say it is included
        if page.meta:
            if "ai-summary" not in page.meta.get("include", {}):
                return markdown
        else:
            return markdown
        # use api to get ai summary
        if self.config["ignore_code"]:
            # delete code block
            pattern = re.compile("```.*?```", re.S)
            markdown_to_summary = re.sub(pattern, "", markdown)
        match self.config["api"]:
            case "tongyi":
                try:
                    from .tongyi_api import get_summary_tongyi, AiSummaryError
                except ImportError as e:
                    logger.warning("tongyi is not available", repr(e))
                    return markdown

                logger.info(f"Asking AI summary for page {page.title}")
                try:
                    summary = get_summary_tongyi(
                        page=str(page.title),
                        prompt=self.config["prompt"],
                        markdown=markdown_to_summary,
                        cache=self.config["cache"],
                        cache_dir=self.config["cache_dir"],
                    )
                except AiSummaryError as e:
                    logger.warning("Ask AI Error", repr(e))
                    return markdown
                except Exception as e:
                    logger.warning(repr(e))
                    return markdown
            case "chatgpt":
                try:
                    from .chatgpt_api import get_summary_chatgpt
                except ImportError as e:
                    logger.warning("chatgpt is not available", repr(e))
                    return markdown

                logger.info(f"Asking AI summary for page {page.title}")
                try:
                    summary = get_summary_chatgpt(
                        page=str(page.title),
                        prompt=self.config["prompt"],
                        markdown=markdown_to_summary,
                        cache=self.config["cache"],
                        cache_dir=self.config["cache_dir"],
                        model=self.config["model"],
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
