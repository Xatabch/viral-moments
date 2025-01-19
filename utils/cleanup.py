import os


def cleanup(directory):
    """
    Удаляет файлы с расширениями .mp4, .wav и .pdf из указанной директории и всех её поддиректорий,
    исключая директорию .venv.

    :param directory: Путь к директории, в которой будет происходить очистка.
    """
    extensions_to_remove = {'.mp4', '.wav', '.pdf', '.jpg'}

    for root, dirs, files in os.walk(directory):
        # Исключаем директорию .venv из обхода
        if '.venv' in dirs:
            dirs.remove('.venv')

        for file in files:
            if os.path.splitext(file)[1].lower() in extensions_to_remove and file != 'music.wav':
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Удален файл: {file_path}")
                except Exception as e:
                    print(f"Не удалось удалить {file_path}: {e}")


if __name__ == "__main__":
    cleanup("./")
