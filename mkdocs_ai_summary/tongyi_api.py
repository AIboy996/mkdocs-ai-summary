import os
import json
import random
from hashlib import md5
from http import HTTPStatus
from dashscope import Generation
import logging

from .chatgpt_api import get_cache_dict, ask_with_cache

MAX_LENGTH = 6000


class AiSummaryError(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def ask(prompt, model="qwen-turbo"):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
    ]
    response = Generation.call(
        model=model,
        messages=messages,
        seed=random.randint(1, 10000),
        result_format="text",
    )
    if response.status_code == HTTPStatus.OK:
        return response["output"]["text"]
    else:
        raise AiSummaryError(
            "Request id: %s, Status code: %s, error code: %s, error message: %s"
            % (
                response.request_id,
                response.status_code,
                response.code,
                response.message,
            )
        )


def get_summary_tongyi(
    page,
    prompt,
    markdown,
    cache=True,
    cache_dir="./",
    model="qwen-turbo",
    logger=logging.Logger(""),
):
    question = (prompt + markdown)[: MAX_LENGTH - 10]
    if cache:
        content_md5 = md5(markdown.encode("utf-8")).hexdigest()
        cache_dict = get_cache_dict(cache_dir, file_suffix="_ai_summary_cache1.json")
        ai_summary = ask_with_cache(
            question, page, content_md5, model, cache_dict, logger
        )
        # always refresh the cache
        cache_dict[page] = {"content_md5": content_md5, "ai_summary": ai_summary}
        with open(f"{cache_dir}/_ai_summary_cache2.json", "w+") as f:
            cache_dict = json.dump(cache_dict, f, indent=4)
    else:
        ai_summary = ask(question, model=model)
    removed_line_break = ai_summary.replace(r"\n", "")
    return f"""!!! tongyiai-summary "AI Summary powered by [通义千问](https://tongyi.aliyun.com/)"
    {removed_line_break}
"""
