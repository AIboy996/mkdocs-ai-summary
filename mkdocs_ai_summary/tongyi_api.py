import os
import json
import random
from hashlib import md5
from http import HTTPStatus
from dashscope import Generation

MAX_LENGTH = 6000


class AiSummaryError(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def ask(prompt):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
    ]
    response = Generation.call(
        model="qwen-turbo",
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


def get_summary_tongyi(page, prompt, markdown, cache=True, cache_dir="./"):
    question = (prompt + markdown)[: MAX_LENGTH - 10]
    if cache:
        content_md5 = md5(markdown.encode("utf-8")).hexdigest()
        cache_file = f"{cache_dir}_ai_summary_cache.json"
        if os.path.exists(cache_file):
            with open(cache_file, "r+") as f:
                cache_dict = json.load(f)
        else:
            cache_dict = {}

        # asked before
        if page in cache_dict:
            if content_md5 == cache_dict[page]["content_md5"]:
                ai_summary = cache_dict[page]["ai_summary"]
            # asked before, but content changed
            else:
                ai_summary = ask(question)
        # do not aksed before
        else:
            ai_summary = ask(question)
            cache_dict[page] = {"content_md5": content_md5, "ai_summary": ai_summary}
            with open(f"{cache_dir}/_ai_summary_cache.json", "w+") as f:
                cache_dict = json.dump(cache_dict, f)
    else:
        ai_summary = ask(question)
    return f"""!!! tongyiai-summary "AI Summary powered by [通义千问](https://tongyi.aliyun.com/)"
    {ai_summary}
"""

