from pydub import AudioSegment

def calculate_frames_pydub(wav_file_path, frame_duration=2, animation_duration=0.1):
    """
    Рассчитать количество кадров для аудиофайла с помощью pydub.

    :param wav_file_path: Путь к WAV файлу.
    :param frame_duration: Длительность одного кадра в секундах.
    :param animation_duration: Длительность одной анимации в секундах.
    :return: Длина аудио и необходимое количество кадров.
    """
    try:
        # Загрузка аудиофайла
        audio = AudioSegment.from_file(wav_file_path)
        
        # Длина аудио в секундах
        duration_seconds = len(audio) / 1000  # pydub возвращает длину в миллисекундах
        
        # Рассчитываем общее время одного кадра (кадр + анимация)
        total_frame_duration = frame_duration + animation_duration
        
        # Определяем количество кадров
        num_frames_needed = int(duration_seconds / total_frame_duration)
        
        return duration_seconds, num_frames_needed

    except Exception as e:
        return f"Ошибка обработки файла: {e}", None
