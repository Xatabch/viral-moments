# Тут можно увидеть пример создания flow с конфигом techcrunch

from content_generators.base import create_content
from content_generators.prompts import get_prompts
from utils.count_images import calculate_frames_pydub
from video_generators.create_video import create_video
from video_generators.compose_video import merge_audio_video_with_subtitles

from configs.video.techcrunch import config as techcrunch

import whisper

if __name__ == "__main__":
    # 1. Получение статей
    get_posts = techcrunch["content"]["fetcher"]
    posts = get_posts(techcrunch["content"]["num_posts"])

    # 2. Генерация контента для поста
    content = create_content(posts, techcrunch["content"]["prompt"])
    print(content)

    # 3. Text to speech
    text_to_speech = techcrunch["speech"]["model"]
    text_to_speech(content["reels_text"], techcrunch["speech"])

    # 4. Подсчет изображений на длительность видео
    duration, frames = calculate_frames_pydub(techcrunch["compose_config"]["voice_path"])
    print(duration, frames)

    # 5. Создаем промпты для картинок для видео
    model = whisper.load_model("base")
    result = model.transcribe(techcrunch["compose_config"]["voice_path"], fp16=False, word_timestamps=True)
    segments = []
    for segment in result['segments']:
        segments.extend(segment['words'])

    prompts = get_prompts(segments, frames)
    print(f"Prompts: {len(prompts['prompts'])}")

    # 6. Генерируем картинки
    generate_images = techcrunch["images"]["generator"]
    generate_images(prompts['prompts'][:frames], techcrunch["images"])

    # 7. Делаем видео
    create_video(techcrunch["video"])

    # 8. Добавляем субтитры и звук
    merge_audio_video_with_subtitles(techcrunch["compose_config"])
