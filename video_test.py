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
from moviepy.video.fx import Crop, Resize

from configs import config

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
        # resized = clip.resized(height=final_h)
        resized = clip.with_effects([vfx.Resize(height=final_h)])
        excess_w = resized.w - final_w
        cropped = Crop(x1=excess_w // 2, width=final_w).apply(resized)
    else:
        # Клип выше, масштабируем по ширине и кропаем по высоте
        # resized = clip.resized(width=final_w)
        resized = clip.with_effects([vfx.Resize(width=final_w)])
        excess_h = resized.h - final_h
        cropped = Crop(y1=excess_h // 2, height=final_h).apply(resized)

    return cropped


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

folder_with_videos = config.VIDEOS_FOLDER
combined_video = build_video_to_match_duration(folder_with_videos, 20)
reels_clip = to_reels_format(combined_video, final_w=config.VIDEO_WITH, final_h=config.VIDEO_HEIGHT)

reels_clip.write_videofile(
        "test.mp4",
        codec="libx264",
        audio_codec="aac",
        fps=reels_clip.fps  # или, скажем, fps=30
)