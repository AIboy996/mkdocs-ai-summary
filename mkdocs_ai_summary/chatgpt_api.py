import os
import json
import logging
from hashlib import md5
from openai import OpenAI


def ask(prompt, model="gpt-3.5-turbo"):
    client = OpenAI()
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


def get_cache_dict(cache_dir, file_suffix="_ai_summary_cache2"):
    cache_file = cache_dir + file_suffix
    if os.path.exists(cache_file):
        with open(cache_file, "r+") as f:
            cache_dict = json.load(f)
    else:
        cache_dict = {}
    return cache_dict


def ask_with_cache(question, page, content_md5, model, cache_dict, logger):
    # asked before
    if page in cache_dict:
        if content_md5 == cache_dict[page]["content_md5"]:
            ai_summary = cache_dict[page]["ai_summary"]
            logger.info("Using cache.")
        # asked before, but content changed
        else:
            ai_summary = ask(question, model=model)
    # do not aksed before
    else:
        ai_summary = ask(question, model=model)
    return ai_summary


def get_summary_chatgpt(
    page,
    prompt,
    markdown,
    cache=True,
    cache_dir="./",
    model="gpt-3.5-turbo",
    logger=logging.Logger(""),
):
    question = prompt + markdown
    if cache:
        content_md5 = md5(markdown.encode("utf-8")).hexdigest()
        cache_dict = get_cache_dict(cache_dir, file_suffix="_ai_summary_cache2.json")
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
    return f"""!!! chatgpt-summary "AI Summary powered by [ChatGPT](https://chat.openai.com/)"
    {removed_line_break}
"""
