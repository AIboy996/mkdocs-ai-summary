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
        cache_file = f"{cache_dir}_ai_summary_cache2.json"
        if os.path.exists(cache_file):
            with open(cache_file, "r+") as f:
                cache_dict = json.load(f)
        else:
            cache_dict = {}

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
            cache_dict[page] = {"content_md5": content_md5, "ai_summary": ai_summary}
            with open(f"{cache_dir}/_ai_summary_cache2.json", "w+") as f:
                cache_dict = json.dump(cache_dict, f)
    else:
        ai_summary = ask(question, model=model)
    return f"""!!! chatgpt-summary "AI Summary powered by [ChatGPT](https://chat.openai.com/)"
    {ai_summary}
"""
