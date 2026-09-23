"""Integration tests for plugin configuration without external API calls."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from mkdocs.commands.build import build
from mkdocs.config import load_config

from mkdocs_ai_summary import chatgpt_api, tongyi_api


MKDOCS_CONFIG = Path(__file__).parent / "mkdocs-ai-summary-test.yml"


class PluginConfigurationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory(prefix="mkdocs-ai-summary-test-")
        work_dir = Path(cls.temp_dir.name)
        cls.site_dir = work_dir / "site"
        config = load_config(config_file=str(MKDOCS_CONFIG))
        config["site_dir"] = str(cls.site_dir)

        cls.openai_calls = []
        cls.tongyi_calls = []

        def fake_openai_ask(prompt, model=None, api_key=None, base_url=None):
            cls.openai_calls.append(
                {
                    "prompt": prompt,
                    "model": model,
                    "api_key": api_key,
                    "base_url": base_url,
                }
            )
            return "Mock provider response"

        def fake_tongyi_ask(prompt, model="qwen-turbo"):
            cls.tongyi_calls.append({"prompt": prompt, "model": model})
            return "Mock Tongyi response"

        cls.patches = [
            patch.object(chatgpt_api, "ask", side_effect=fake_openai_ask),
            patch.object(tongyi_api, "ask", side_effect=fake_tongyi_ask),
            patch.object(
                chatgpt_api,
                "get_summary",
                wraps=chatgpt_api.get_summary,
            ),
            patch.object(
                tongyi_api,
                "get_summary",
                wraps=tongyi_api.get_summary,
            ),
        ]
        for active_patch in cls.patches:
            active_patch.start()

        try:
            build(config)
        except Exception:
            for active_patch in reversed(cls.patches):
                active_patch.stop()
            cls.temp_dir.cleanup()
            raise

        cls.chatgpt_summary_calls = chatgpt_api.get_summary.call_args_list
        cls.tongyi_summary_calls = tongyi_api.get_summary.call_args_list

    @classmethod
    def tearDownClass(cls):
        for active_patch in reversed(cls.patches):
            active_patch.stop()
        cls.temp_dir.cleanup()

    @staticmethod
    def calls_by_page(calls):
        return {call.kwargs["page"]: call.kwargs for call in calls}

    def test_site_level_chatgpt_defaults_and_code_filter(self):
        call = self.calls_by_page(self.chatgpt_summary_calls)["ChatGPT Site Defaults"]
        self.assertEqual(call["model"], "gpt-3.5-turbo")
        self.assertEqual(
            call["prompt"],
            "Please help me summarize the following content into an abstract within 200 words: ",
        )
        self.assertEqual(call["api_key"], "")
        self.assertEqual(call["base_url"], "")
        self.assertEqual(call["cache_dir"], ".test-cache")
        self.assertEqual(call["provider_name"], "chatgpt")
        self.assertEqual(call["provider_title"], "ChatGPT")
        self.assertFalse(call["cache"])

        provider_call = next(
            item
            for item in self.openai_calls
            if item["prompt"].startswith(
                "Please help me summarize the following content into an abstract"
            )
        )
        self.assertIn("# ChatGPT Site Defaults", provider_call["prompt"])
        self.assertNotIn("SITE_CODE_SENTINEL", provider_call["prompt"])
        self.assertEqual(provider_call["model"], "gpt-3.5-turbo")

    def test_page_level_chatgpt_options_override_site_values(self):
        call = self.calls_by_page(self.chatgpt_summary_calls)["ChatGPT Page Overrides"]
        self.assertEqual(call["model"], "page-chat-model")
        self.assertEqual(call["api_key"], "PAGE_OPENAI_KEY")
        self.assertEqual(call["base_url"], "https://chat-proxy.example/v1")
        self.assertEqual(call["cache_dir"], ".test-cache/page")
        self.assertEqual(call["provider_name"], "test-gateway")
        self.assertEqual(call["provider_title"], "Test Gateway")
        provider_call = next(
            item for item in self.openai_calls if item["model"] == "page-chat-model"
        )
        self.assertIn("PAGE_CODE_SENTINEL", provider_call["prompt"])
        self.assertEqual(provider_call["api_key"], "PAGE_OPENAI_KEY")
        self.assertEqual(provider_call["base_url"], "https://chat-proxy.example/v1")

    def test_deepseek_default_and_page_level_settings(self):
        calls = self.calls_by_page(self.chatgpt_summary_calls)
        default_call = calls["DeepSeek Defaults"]
        self.assertEqual(default_call["model"], "deepseek-flash")
        self.assertEqual(default_call["api_key"], "DEEPSEEK_API_KEY")
        self.assertEqual(default_call["base_url"], "https://api.deepseek.com")
        self.assertEqual(default_call["cache_suffix"], "_ai_summary_cache_deepseek.json")

        override_call = calls["DeepSeek Page Overrides"]
        self.assertEqual(override_call["model"], "page-deepseek-model")
        self.assertEqual(override_call["api_key"], "PAGE_DEEPSEEK_KEY")
        self.assertEqual(override_call["base_url"], "https://deepseek-proxy.example/v1")
        self.assertEqual(override_call["provider_title"], "DeepSeek Proxy")
        provider_call = next(
            item for item in self.openai_calls if item["model"] == "page-deepseek-model"
        )
        self.assertIn("DEEPSEEK_PAGE_CODE_SENTINEL", provider_call["prompt"])

    def test_tongyi_page_level_settings(self):
        calls = {call.kwargs["page"]: call.kwargs for call in self.tongyi_summary_calls}
        self.assertEqual(set(calls), {"Tongyi Defaults", "Tongyi Page Overrides"})
        defaults = calls["Tongyi Defaults"]
        self.assertEqual(defaults["model"], "qwen-turbo")
        self.assertEqual(
            defaults["prompt"],
            "Please help me summarize the following content into an abstract within 200 words: ",
        )
        overrides = calls["Tongyi Page Overrides"]
        self.assertEqual(overrides["model"], "page-qwen-model")
        self.assertEqual(overrides["prompt"], "Tongyi page instruction")
        self.assertEqual(overrides["provider_name"], "page-tongyi")
        self.assertFalse(overrides["cache"])

        tongyi_by_model = {call["model"]: call["prompt"] for call in self.tongyi_calls}
        self.assertIn("TONGYI_CODE_SENTINEL", tongyi_by_model["page-qwen-model"])
        self.assertNotIn("TONGYI_DEFAULT_CODE_SENTINEL", tongyi_by_model["qwen-turbo"])

    def test_pages_without_opt_in_do_not_call_a_provider(self):
        called_pages = {
            call.kwargs["page"]
            for call in self.chatgpt_summary_calls + self.tongyi_summary_calls
        }
        self.assertNotIn("No Summary Opt In", called_pages)

    def test_mocked_summaries_are_rendered(self):
        html = (self.site_dir / "chatgpt-site-defaults" / "index.html").read_text(
            encoding="utf-8"
        )
        self.assertIn("Mock provider response", html)
        self.assertIn("AI Summary powered by", html)

    def test_cache_uses_article_content_only(self):
        with tempfile.TemporaryDirectory() as cache_dir:
            initial_calls = len(self.openai_calls)
            common = {
                "page": "Cache Content Only",
                "markdown": "unchanged article body",
                "cache": True,
                "cache_dir": cache_dir,
            }
            chatgpt_api.get_summary(
                **common, prompt="first prompt", model="first-model"
            )
            chatgpt_api.get_summary(
                **common,
                prompt="changed prompt",
                model="different-model",
                base_url="https://different.example/v1",
            )
            self.assertEqual(len(self.openai_calls), initial_calls + 1)

            chatgpt_api.get_summary(
                **{**common, "markdown": "changed article body"},
                prompt="changed prompt",
                model="different-model",
            )
            self.assertEqual(len(self.openai_calls), initial_calls + 2)


if __name__ == "__main__":
    unittest.main()
