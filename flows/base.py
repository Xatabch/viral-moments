from content_generators.base import create_content
from content_generators.prompts import get_prompts
from utils.count_images import calculate_frames_pydub
from video_generators.create_video import create_video
from video_generators.compose_video import merge_audio_video_with_subtitles
import whisper

async def create_video_with_data(posts, config):
    # 1. Генерация контента для поста
    content = create_content(posts, config["content"]["prompt"])

    # 2. Text to speech
    text_to_speech = config["speech"]["model"]
    text_to_speech(content["reels_text"], config["speech"])

    # 3. Подсчет изображений на длительность видео
    _, frames = calculate_frames_pydub(config["compose_config"]["voice_path"])

    # 4. Создаем промпты для картинок для видео
    model = whisper.load_model("base")
    result = model.transcribe(config["compose_config"]["voice_path"], fp16=False, word_timestamps=True)
    segments = []
    for segment in result['segments']:
        segments.extend(segment['words'])

    prompts = get_prompts(segments, frames)

    # 5. Генерируем картинки
    generate_images = config["images"]["generator"]
    generate_images(prompts['prompts'][:frames], config["images"])

    # 6. Делаем видео
    create_video(config["video"])

    # 7. Добавляем субтитры и звук
    merge_audio_video_with_subtitles(config["compose_config"])


    return content
