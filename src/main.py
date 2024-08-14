import os
import json
import asyncio

from kishida_lex_wordcloud.kantei import KanteiClient
from kishida_lex_wordcloud.text_processor import TextProcessor
from kishida_lex_wordcloud.wc_gen import generate_wordcloud


this_dir = os.path.abspath(os.path.dirname(__file__))
json_path = os.path.join(this_dir, "config.json")
with open(json_path, "r", encoding="utf-8") as f:
    conf = json.load(f)


async def main():
    kc = KanteiClient()
    tp = TextProcessor(d=conf["ditc_path"])
    article_count = 0
    async for article in kc.get_data():
        if article:
            tp.update_word_frequencies(article)
            article_count += 1
    word_freq = tp.get_word_frequencies()
    generate_wordcloud(word_freq, this_dir, min_count=5)


if __name__ == "__main__":
    asyncio.run(main())
