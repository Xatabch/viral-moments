import os
import whisper_timestamped as whisper
from moviepy import (
    VideoFileClip,
    AudioFileClip,
    CompositeVideoClip,
    TextClip,
    concatenate_videoclips,
    vfx
)
from moviepy.video.fx import Crop
from configs import config


def transcribe_with_whisper_timestamped(audio_path: str,
                                        model_name: str = "medium",
                                        language: str = "en") -> list:
    """
    Распознаёт речь из audio_path с помощью whisper-timestamped.
    Возвращает список слов со start/end, например:
      [
        {"word": "Привет", "start": 0.45, "end": 0.71},
        ...
      ]
    """
    model = whisper.load_model(model_name)
    result = model.transcribe(
        audio_path,
        language=language,
        word_timestamps=True
    )

    all_words = []
    segments = result.get("segments", [])
    for seg in segments:
        for w in seg["words"]:
            word_text = w["word"].strip()
            start_time = w["start"]
            end_time = w["end"]
            all_words.append({
                "word": word_text,
                "start": start_time,
                "end": end_time
            })

    return all_words


def build_video_to_match_duration(folder_with_videos: str,
                                  needed_duration: float) -> VideoFileClip:
    """
    Сшивает (конкатенирует) ролики из папки folder_with_videos так,
    чтобы суммарная длительность была >= needed_duration.

    - Если всех роликов не хватает, начинает брать их заново по кругу (зацикливание).
    - Если при добавлении последнего клипа перебираем нужное время, обрезаем его до остатка.
    - Возвращает итоговый VideoFileClip ровно на needed_duration сек.
    """

    # Собираем список файлов в папке
    video_files = sorted([
        f for f in os.listdir(folder_with_videos)
        if f.lower().endswith((".mp4", ".mov", ".avi", ".mkv"))
    ])
    if not video_files:
        raise FileNotFoundError(f"В папке '{folder_with_videos}' не найдено ни одного видео!")

    final_clips = []
    total_dur = 0.0
    idx = 0

    # Пока не набрали нужную длину
    while total_dur < needed_duration:
        video_file = video_files[idx]
        idx = (idx + 1) % len(video_files)  # Переходим к следующему с зацикливанием

        clip_path = os.path.join(folder_with_videos, video_file)
        clip = VideoFileClip(clip_path)

        leftover = needed_duration - total_dur
        if clip.duration <= leftover:
            # Берём весь клип целиком
            final_clips.append(clip)
            total_dur += clip.duration
        else:
            # Берём только нужный отрезок, чтобы точно получить needed_duration
            sub = clip.subclipped(0, leftover)
            final_clips.append(sub)
            total_dur += leftover
            break  # набрали всё

    # Склеиваем
    combined_clip = concatenate_videoclips(final_clips, method="compose")

    # На всякий случай убедимся, что длина ровно та же
    if combined_clip.duration > needed_duration:
        combined_clip = combined_clip.subclipped(0, needed_duration)

    return combined_clip


def to_reels_format(clip: VideoFileClip, final_w=1080, final_h=1920) -> VideoFileClip:
    """
    Масштабирует клип до нужных пропорций с небольшим превышением,
    а затем обрезает лишние части для заполнения кадра без полей.
    """
    # Вычисляем соотношение сторон
    orig_w, orig_h = clip.size
    target_aspect = final_w / final_h
    orig_aspect = orig_w / orig_h

    if orig_aspect > target_aspect:
        # Клип шире, масштабируем по высоте и кропаем по ширине
        resized = clip.resized(height=final_h)
        excess_w = resized.w - final_w
        cropped = Crop(x1=excess_w // 2, width=final_w).apply(resized)
    else:
        # Клип выше, масштабируем по ширине и кропаем по высоте
        resized = clip.resized(width=final_w)
        excess_h = resized.h - final_h
        cropped = Crop(y1=excess_h // 2, height=final_h).apply(resized)

    return cropped


def create_text_clips(words: list,
                      font_size=40,
                      text_color='black',
                      font="Arial",
                      position=('center', 'bottom'),
                      bg_color=(255, 255, 255),
                      bg_opacity=1.0,
                      pad_x=20,
                      pad_y=10) -> list:
    """
    Создаёт список клипов с текстом + белой плашкой.
    При этом размер плашки подгоняется под размер текста.

    words: [{"word": "...", "start": 0.45, "end": 0.71}, ...]
    font_size: размер шрифта
    text_color: цвет текста (например, 'black')
    font: название шрифта (Arial, ...)
    position: куда ставить плашку ('center','bottom') и т.д.
    bg_color: цвет фона (r,g,b), например (255,255,255) для белого
    bg_opacity: прозрачность плашки (1.0 = непрозрачно)
    pad_x, pad_y: отступы вокруг текста
    """
    text_clips = []
    for w in words:
        start_t = w["start"]
        end_t = w["end"]
        duration = end_t - start_t
        word_text = w["word"]

        txt_clip = TextClip(text=word_text,
                            font=font,
                            font_size=font_size,
                            color=text_color,
                            bg_color=bg_color,
                            margin=(pad_x, pad_y))

        # 3) Задаём время появления и позицию
        txt_box = (
            txt_clip
            .with_start(start_t)
            .with_duration(duration)
            .with_position(position)
        )
        text_clips.append(txt_box)

    return text_clips


def create_video_from_content():
    # Параметры
    folder_with_videos = config.VIDEOS_FOLDER  # Папка с роликами (n файлов), из которых собираем «фон»
    audio_path = config.VOICE_FILE_NAME  # Ваше озвученное аудио
    output_path = config.OUTPUT_VIDEO_NAME

    # Шаг 1. Распознаём речь, получаем список слов
    words = transcribe_with_whisper_timestamped(
        audio_path=audio_path,
        model_name="medium",  # 'tiny', 'small', 'large' и т.д. на ваше усмотрение
        language=config.CONTENT_LANGUAGE
    )
    if not words:
        print("Не удалось распознать ни одного слова. Останавливаемся.")
        return

    # Длительность аудио (конец последнего слова)
    total_speech_duration = words[-1]["end"]
    print(f"Всего слов: {len(words)}, длительность речи ~ {total_speech_duration:.2f} сек.")

    # Шаг 2. Собираем фоновое видео нужной длительности
    #        (добавляем ролики из папки по порядку, если не хватит, идём по кругу, последний обрезаем).
    print("Формируем единое видео из папки...")
    combined_video = build_video_to_match_duration(folder_with_videos, total_speech_duration)
    print(f"Готовый фоновый ролик: {combined_video.duration:.2f} сек.")

    # Шаг 3. Создаём аудиоклип из озвучки
    voice_clip = AudioFileClip(audio_path)

    # Шаг 4. Подменяем звуковую дорожку фонового видео нашей озвучкой
    video_with_new_audio = combined_video.with_audio(voice_clip)

    # Шаг 5. Создаём клипы с «белой плашкой» под каждое слово
    text_clips = create_text_clips(
        words=words,
        font_size=config.TEXT_SIZE,
        text_color=config.TEXT_COLOR,
        font=config.TEXT_FONT,
        position=('center', 'center'),
        bg_color=(255, 255, 255),  # белый фон
        bg_opacity=1.0,
        pad_x=20,  # дополнительные отступы по горизонтали
        pad_y=10  # отступы по вертикали
    )

    # Шаг 6. Накладываем текст (с плашками) поверх видео
    final = CompositeVideoClip([video_with_new_audio, *text_clips])

    # Шаг 7. Приводим итог к формату Instagram Reels (9:16), например 1080x1920,
    #        без чёрных полей — масштабируем и обрезаем лишнее по центру.
    reels_clip = to_reels_format(final, final_w=config.VIDEO_WITH, final_h=config.VIDEO_HEIGHT)

    # Шаг 8. Сохраняем результат
    #       Обратите внимание: fps можно взять от исходных клипов, или задать принудительно (например, 30).
    reels_clip.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=combined_video.fps  # или, скажем, fps=30
    )

    print("Готово! Итоговый файл:", output_path)