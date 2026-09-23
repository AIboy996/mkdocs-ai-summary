import os
import logging
from hashlib import md5
from functools import partial
from openai import OpenAI

from .cache import with_cache, load_cache, save_cache


def ask(prompt, model="gpt-3.5-turbo", api_key=None, base_url=None):
    kwargs = {}
    if api_key:
        # api_key is the name of an environment variable that holds the key
        key = os.environ.get(api_key)
        if not key:
            raise ValueError(f"API key environment variable {api_key!r} is not set")
        kwargs["api_key"] = key
    if base_url:
        kwargs["base_url"] = base_url
    client = OpenAI(**kwargs)
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a personal assistant, skilled in summarizing.",
            },
            {"role": "user", "content": prompt},
        ],
    )

    return completion.choices[0].message.content


def get_summary(
    page,
    prompt,
    markdown,
    cache=True,
    cache_dir="./",
    model="gpt-3.5-turbo",
    logger=logging.Logger(""),
    cache_suffix="_ai_summary_cache_chatgpt.json",
    api_key=None,
    base_url=None,
    provider_name="chatgpt",
    provider_title="ChatGPT",
    provider_link="https://chat.openai.com/",
):
    separator = "" if prompt.rstrip().endswith(":") else ":"
    question = prompt + separator + "\n\n" + markdown
    ask_fn = partial(ask, api_key=api_key, base_url=base_url)
    if cache:
        content_md5 = md5(markdown.encode("utf-8")).hexdigest()
        cache_dict = load_cache(cache_dir, cache_suffix)
        ai_summary = with_cache(ask_fn, cache_dict, model, logger)(
            page, question, content_md5
        )
        cache_dict[page] = {"content_md5": content_md5, "ai_summary": ai_summary}
        # always refresh the cache
        save_cache(cache_dict, cache_dir, file_suffix=cache_suffix)
    else:
        ai_summary = ask_fn(question, model=model)
    removed_line_break = ai_summary.replace(r"\n", "")
    return f"""!!! {provider_name}-summary "AI Summary powered by [{provider_title}]({provider_link})"
    {removed_line_break}
"""
