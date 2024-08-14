import os

from wordcloud import WordCloud


def generate_wordcloud(word_freq, this_dir, filename="wordcloud.png", min_count=5):
    # カウント数が min_count 以上の単語だけをフィルタリング
    filtered_word_freq = {
        word: count for word, count in word_freq.items() if count >= min_count
    }

    # WordCloudオブジェクトを作成
    font_path = f"{this_dir}/font/SawarabiGothic-Regular.ttf"
    print(font_path)
    wordcloud = WordCloud(
        width=1200,
        height=800,
        background_color="white",
        font_path=font_path,
        max_font_size=100,
        max_words=256,
    )

    # フィルタリングされた単語頻度データからワードクラウドを生成
    wordcloud.generate_from_frequencies(filtered_word_freq)
    output_dir = f"{this_dir}/output"
    os.makedirs(output_dir, exist_ok=True)
    wordcloud.to_file(f"{output_dir}/{filename}")

    # フィルタリングの結果を表示（オプション）
    print(filtered_word_freq)
    print(f"Original word count: {len(word_freq)}")
    print(f"Filtered word count: {len(filtered_word_freq)}")
