from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    TextClip,
    CompositeVideoClip,
    CompositeAudioClip,
    concatenate_audioclips
)
import whisper

def normalize_text(text):
    """
    Приводит текст к верхнему регистру.
    """
    return text.upper()

def split_text_to_fit(text, max_line_length):
    """
    Разбивает текст на строки, чтобы каждая строка не превышала заданную длину.
    """
    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        if current_length + len(word) + len(current_line) <= max_line_length:
            current_line.append(word)
            current_length += len(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word)

    if current_line:
        lines.append(" ".join(current_line))

    return lines

def create_shadow_clip(text, fontsize, color, stroke_width, stroke_color, x, y, start_time, end_time, font, opacity):
    """Создает текстовый клип для тени."""
    return TextClip(
        txt=normalize_text(text),
        fontsize=fontsize,
        font=font,
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        color=color,
    ).set_position((x, y)).set_start(start_time).set_end(end_time).set_opacity(opacity)

def create_line_clips(
    words_list,
    start_time,
    end_time,
    video_w,
    video_h,
    font,
    text_color,
    font_size,
    shadow_opacity,
    shadow_color,
    shadow_offset_x,
    shadow_offset_y,
    stroke_color,
    text_stroke_width,
    line_y_start=-50,
):
    """
    Создаёт TextClip для каждого слова, располагая их по строкам с переносом.
    """
    clips = []
    current_line_words = []
    current_line_width = 0
    line_height = font_size * 1.2  # Примерный интервал между строками
    current_y_offset = line_y_start

    for word_data in words_list:
        w, _, _ = word_data
        temp_clip = TextClip(
            txt=normalize_text(w),
            fontsize=font_size,
            font=font,
            stroke_width=text_stroke_width,
            stroke_color=stroke_color,
            color=text_color
        )
        word_width, _ = temp_clip.size
        temp_clip.close()

        # Проверяем, поместится ли слово на текущей строке
        if current_line_width + word_width + (10 if current_line_words else 0) < video_w * 0.9: # 90% ширины экрана
            current_line_words.append(word_data)
            current_line_width += word_width + (10 if len(current_line_words) > 1 else 0)
        else:
            # Начинаем новую строку
            if current_line_words:
                # Создаем клипы для предыдущей строки
                total_width = sum(TextClip(txt=normalize_text(wd[0]), fontsize=font_size, font=font).size[0] + 10 for wd in current_line_words) - 10
                line_x_start = (video_w - total_width) // 2
                x_offset = 0
                for w_data in current_line_words:
                    w, _, _ = w_data
                    # Создаем тень
                    shadow_clip = create_shadow_clip(
                        text=w,
                        fontsize=font_size,
                        color=shadow_color,
                        stroke_width=text_stroke_width,
                        stroke_color=stroke_color,
                        x=line_x_start + x_offset + shadow_offset_x,
                        y=video_h // 2 + current_y_offset + int(video_h * 0.2) + shadow_offset_y,
                        start_time=start_time,
                        end_time=end_time,
                        font=font,
                        opacity=shadow_opacity
                    )
                    clips.append(shadow_clip)
                    # Создаем основной текст
                    text_clip = TextClip(
                        txt=normalize_text(w),
                        fontsize=font_size,
                        font=font,
                        stroke_width=text_stroke_width,
                        stroke_color=stroke_color,
                        color=text_color
                    ).set_position(
                        (line_x_start + x_offset, video_h // 2 + current_y_offset + int(video_h * 0.2)) # Смещение на 20% вниз
                    ).set_start(start_time).set_end(end_time)
                    clips.append(text_clip)
                    x_offset += TextClip(txt=normalize_text(w), fontsize=font_size, font=font).size[0] + 10
                current_y_offset += line_height
                current_line_words = [word_data]
                current_line_width = word_width
            else:
                # Если одно слово слишком длинное, чтобы поместиться на строку
                current_line_words = [word_data]
                current_line_width = word_width

    # Обрабатываем последнюю строку
    if current_line_words:
        total_width = sum(TextClip(txt=normalize_text(wd[0]), fontsize=font_size, font=font).size[0] + 10 for wd in current_line_words) - 10
        line_x_start = (video_w - total_width) // 2
        x_offset = 0
        for w_data in current_line_words:
            w, _, _ = w_data
            # Создаем тень
            shadow_clip = create_shadow_clip(
                text=w,
                fontsize=font_size,
                color=shadow_color,
                stroke_width=text_stroke_width,
                stroke_color=stroke_color,
                x=line_x_start + x_offset + shadow_offset_x,
                y=video_h // 2 + current_y_offset + int(video_h * 0.2) + shadow_offset_y,
                start_time=start_time,
                end_time=end_time,
                font=font,
                opacity=shadow_opacity
            )
            clips.append(shadow_clip)
            # Создаем основной текст
            text_clip = TextClip(
                txt=normalize_text(w),
                fontsize=font_size,
                font=font,
                stroke_width=text_stroke_width,
                stroke_color=stroke_color,
                color='white'
            ).set_position(
                (line_x_start + x_offset, video_h // 2 + current_y_offset + int(video_h * 0.2)) # Смещение на 20% вниз
            ).set_start(start_time).set_end(end_time)
            clips.append(text_clip)
            x_offset += TextClip(txt=normalize_text(w), fontsize=font_size, font=font).size[0] + 10

    return clips

def create_highlight_clips(
    words_list,
    video_w,
    video_h,
    font,
    font_size,
    text_color,
    shadow_color,
    shadow_offset_x,
    shadow_offset_y,
    stroke_color,
    text_stroke_width,
    shadow_opacity,
    line_y_start=-50,
):
    """
    Создаёт красные (подсвеченные) TextClip с тенью для каждого слова, располагая их по строкам с переносом.
    """
    clips = []
    current_line_words = []
    current_line_width = 0
    line_height = font_size * 1.2
    current_y_offset = line_y_start

    for word_data in words_list:
        w, w_start, w_end = word_data
        temp_clip = TextClip(
            txt=normalize_text(w),
            fontsize=font_size,
            font=font,
            stroke_width=text_stroke_width,
            stroke_color=stroke_color,
            color=text_color
        )
        word_width, _ = temp_clip.size
        temp_clip.close()

        if current_line_width + word_width + (10 if current_line_words else 0) < video_w * 0.9:
            current_line_words.append(word_data)
            current_line_width += word_width + (10 if len(current_line_words) > 1 else 0)
        else:
            if current_line_words:
                total_width = sum(TextClip(txt=normalize_text(wd[0]), fontsize=font_size, font=font).size[0] + 10 for wd in current_line_words) - 10
                line_x_start = (video_w - total_width) // 2
                x_offset = 0
                for w_data in current_line_words:
                    w, w_start, w_end = w_data
                    # Создаем тень
                    shadow_clip = create_shadow_clip(
                        text=w,
                        fontsize=font_size,
                        color=shadow_color,
                        stroke_width=text_stroke_width,
                        stroke_color=stroke_color,
                        x=line_x_start + x_offset + shadow_offset_x,
                        y=video_h // 2 + current_y_offset + int(video_h * 0.2) + shadow_offset_y,
                        start_time=w_start,
                        end_time=w_end,
                        font=font,
                        opacity=shadow_opacity
                    )
                    clips.append(shadow_clip)
                    # Создаем основной текст
                    text_clip = TextClip(
                        txt=normalize_text(w),
                        fontsize=font_size,
                        font=font,
                        stroke_width=text_stroke_width,
                        stroke_color=stroke_color,
                        color=text_color
                    ).set_position(
                        (line_x_start + x_offset, video_h // 2 + current_y_offset + int(video_h * 0.2)) # Смещение на 20% вниз
                    ).set_start(w_start).set_end(w_end)
                    clips.append(text_clip)
                    x_offset += TextClip(txt=normalize_text(w), fontsize=font_size, font=font).size[0] + 10
                current_y_offset += line_height
                current_line_words = [word_data]
                current_line_width = word_width
            else:
                current_line_words = [word_data]
                current_line_width = word_width

    if current_line_words:
        total_width = sum(TextClip(txt=normalize_text(wd[0]), fontsize=font_size, font=font).size[0] + 10 for wd in current_line_words) - 10
        line_x_start = (video_w - total_width) // 2
        x_offset = 0
        for w_data in current_line_words:
            w, w_start, w_end = w_data
            # Создаем тень
            shadow_clip = create_shadow_clip(
                text=w,
                fontsize=font_size,
                color=shadow_color,
                stroke_width=text_stroke_width,
                stroke_color=stroke_color,
                x=line_x_start + x_offset + shadow_offset_x,
                y=video_h // 2 + current_y_offset + int(video_h * 0.2) + shadow_offset_y,
                start_time=w_start,
                end_time=w_end,
                font=font,
                opacity=shadow_opacity
            )
            clips.append(shadow_clip)
            # Создаем основной текст
            text_clip = TextClip(
                txt=normalize_text(w),
                fontsize=font_size,
                font=font,
                stroke_width=text_stroke_width,
                stroke_color=stroke_color,
                color=text_color
            ).set_position(
                (line_x_start + x_offset, video_h // 2 + current_y_offset + int(video_h * 0.2)) # Смещение на 20% вниз
            ).set_start(w_start).set_end(w_end)
            clips.append(text_clip)
            x_offset += TextClip(txt=normalize_text(w), fontsize=font_size, font=font).size[0] + 10

    return clips

def merge_audio_video_with_subtitles(compose_config):
    """
    Накладывает аудио на видео и добавляет субтитры с тенью,
    разделяя их на блоки, строки и подсвечивая текущее слово.
    Музыка обрезается или зацикливается под длину основной аудиодорожки.
    """
    try:
        print("Распознавание речи с помощью Whisper...")
        model = whisper.load_model("base")
        result = model.transcribe(compose_config['voice_path'], fp16=False, word_timestamps=True)

        # Загрузка видео и основной аудиодорожки
        video_path = "temp_video.mp4" # Предполагается, что видео создается на предыдущем шаге
        video = VideoFileClip(video_path)
        audio = AudioFileClip(compose_config['voice_path'])
        audio_duration = audio.duration

        # Загрузка фоновой музыки
        background_music = AudioFileClip(compose_config['bg_music_path']).volumex(0.2)
        music_duration = background_music.duration

        # Обработка фоновой музыки
        if music_duration >= audio_duration:
            # Обрезаем музыку до длины аудио
            background_music = background_music.subclip(0, audio_duration)
        else:
            # Зацикливаем музыку
            n_repeats = int(audio_duration // music_duration)
            remainder = audio_duration % music_duration

            repeated_music = [background_music] * n_repeats
            if remainder > 0:
                repeated_music.append(background_music.subclip(0, remainder))

            background_music = concatenate_audioclips(repeated_music)

        combined_audio = CompositeAudioClip([audio, background_music])
        video_with_audio = video.set_audio(combined_audio)

        video_w, video_h = video.size

        max_words_per_block = 4
        pause_threshold = 0.3

        subtitle_clips = []

        for segment in result['segments']:
            words = segment['words']
            block_start = words[0]['start']
            current_block_words = []

            for i in range(len(words)):
                w = words[i]['word']
                w_start = words[i]['start']
                w_end = words[i]['end']
                current_block_words.append((w, w_start, w_end))

                is_last_word = (i == len(words) - 1)
                if not is_last_word:
                    next_pause = words[i+1]['start'] - words[i]['end']
                else:
                    next_pause = 0

                if (len(current_block_words) == max_words_per_block
                    or is_last_word
                    or next_pause > pause_threshold):

                    block_end = current_block_words[-1][2]

                    # Клипы (видны во всё время блока)
                    white_clips = create_line_clips(
                        words_list=current_block_words,
                        start_time=block_start,
                        end_time=block_end,
                        video_w=video_w,
                        video_h=video_h,
                        font=compose_config['font_path'],
                        font_size=compose_config['font_size'],
                        text_color=compose_config['text_color'],
                        shadow_color=compose_config['shadow_color'],
                        shadow_offset_x=compose_config['shadow_offset_x'],
                        shadow_offset_y=compose_config['shadow_offset_y'],
                        stroke_color=compose_config['stroke_color'],
                        text_stroke_width=compose_config['text_stroke_width'],
                        shadow_opacity=compose_config['shadow_opacity']
                    )
                    subtitle_clips.extend(white_clips)

                    # Подсветка клипов (подсвечиваются лишь при произнесении)
                    highlight_clips = create_highlight_clips(
                        words_list=current_block_words,
                        video_w=video_w,
                        video_h=video_h,
                        font=compose_config['font_path'],
                        font_size=compose_config['font_size'],
                        text_color=compose_config['highlight_color'],
                        shadow_color=compose_config['shadow_color'],
                        shadow_offset_x=compose_config['shadow_offset_x'],
                        shadow_offset_y=compose_config['shadow_offset_y'],
                        stroke_color=compose_config['stroke_color'],
                        text_stroke_width=compose_config['text_stroke_width'],
                        shadow_opacity=compose_config['shadow_opacity'],
                    )
                    subtitle_clips.extend(highlight_clips)

                    current_block_words = []
                    if not is_last_word:
                        block_start = words[i+1]['start']

        final_video = CompositeVideoClip([video_with_audio] + subtitle_clips)
        final_video.write_videofile(compose_config['output_video_name'], codec="libx264", audio_codec="aac")

        print(f"Видео с субтитрами сохранено в: {compose_config['output_video_name']}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")