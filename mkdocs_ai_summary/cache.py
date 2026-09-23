import os
import json
from logging import Logger


def load_cache(cache_dir, file_suffix="_ai_summary_cache.json"):
    cache_file = os.path.join(cache_dir, file_suffix)
    if os.path.exists(cache_file):
        with open(cache_file, "r+") as f:
            cache_dict = json.load(f)
    else:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict, cache_dir, file_suffix="_ai_summary_cache.json"):
    cache_file = os.path.join(cache_dir, file_suffix)
    os.makedirs(os.path.dirname(cache_file) or ".", exist_ok=True)
    with open(cache_file, "w+") as f:
        json.dump(cache_dict, f, indent=4)


def with_cache(
    ask,  # function to ask ai
    cache_dict: dict,
    model: str,
    logger: Logger,
):
    def ask_with_cache(page, question, content_md5):
        nonlocal model, cache_dict, logger
        if page in cache_dict and content_md5 == cache_dict[page]["content_md5"]:
            ai_summary = cache_dict[page]["ai_summary"]
            logger.info("Using cache.")
            return ai_summary
        ai_summary = ask(question, model=model)
        logger.info(f"Get answer from {model}.")
        return ai_summary

    return ask_with_cache
