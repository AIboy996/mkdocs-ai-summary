import logging
from hashlib import md5
from openai import OpenAI

from .cache import with_cache, load_cache, save_cache


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


def get_summary(
    page,
    prompt,
    markdown,
    cache=True,
    cache_dir="./",
    model="gpt-3.5-turbo",
    logger=logging.Logger(""),
    cache_suffix="_ai_summary_cache_chatgpt.json",
):
    question = prompt + ":\n\n" + markdown
    if cache:
        content_md5 = md5(markdown.encode("utf-8")).hexdigest()
        cache_dict = load_cache(cache_dir, cache_suffix)
        ai_summary = with_cache(ask, cache_dict, model, logger)(
            page, question, content_md5  # ask question with cache
        )
        cache_dict[page] = {"content_md5": content_md5, "ai_summary": ai_summary}
        # always refresh the cache
        save_cache(cache_dict, cache_dir, file_suffix=cache_suffix)
    else:
        ai_summary = ask(question, model=model)
    removed_line_break = ai_summary.replace(r"\n", "")
    return f"""!!! chatgpt-summary "AI Summary powered by [ChatGPT](https://chat.openai.com/)"
    {removed_line_break}
"""
