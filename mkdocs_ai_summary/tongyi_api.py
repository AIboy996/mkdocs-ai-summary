import logging
from hashlib import md5
from http import HTTPStatus
from dashscope import Generation

from .cache import with_cache, load_cache, save_cache

MAX_LENGTH = 6000


class AiSummaryRequestError(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def ask(prompt, model="qwen-turbo"):
    messages = [
        {
            "role": "system",
            "content": "You are a personal assistant, skilled in summarizing.",
        },
        {"role": "user", "content": prompt},
    ]
    response = Generation.call(
        model=model,
        messages=messages,
        result_format="text",
    )
    if response.status_code == HTTPStatus.OK:
        return response["output"]["text"]
    else:
        raise AiSummaryRequestError(
            "Request id: %s, Status code: %s, error code: %s, error message: %s"
            % (
                response.request_id,
                response.status_code,
                response.code,
                response.message,
            )
        )


def get_summary(
    page,
    prompt,
    markdown,
    cache=True,
    cache_dir="./",
    model="qwen-turbo",
    logger=logging.Logger(""),
    cache_suffix="_ai_summary_cache_tongyi.json",
):
    question = prompt + ":\n\n" + markdown
    if cache:
        content_md5 = md5(markdown.encode("utf-8")).hexdigest()
        cache_dict = load_cache(cache_dir, cache_suffix)
        ai_summary = with_cache(ask, cache_dict, model, logger)(
            page, question[: MAX_LENGTH - 10], content_md5  # ask question with cache
        )
        cache_dict[page] = {"content_md5": content_md5, "ai_summary": ai_summary}
        # always refresh the cache
        save_cache(cache_dict, cache_dir, file_suffix=cache_suffix)
    else:
        ai_summary = ask(question, model=model)
    removed_line_break = ai_summary.replace(r"\n", "")
    return f"""!!! tongyiai-summary "AI Summary powered by [通义千问](https://tongyi.aliyun.com/)"
    {removed_line_break}
"""
