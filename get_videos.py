import requests
import os
from configs import config


def search_videos_on_pexels(tag, num_results=5):
    """Ищет видео на Pexels по указанному тегу."""
    url = "https://api.pexels.com/videos/search"
    headers = {
        "Authorization": config.PEXELS_API_KEY
    }
    params = {
        "query": tag,
        "per_page": num_results,
        "size": "large",
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        video_files = []
        for video in data.get("videos", []):
            # Проверяем, что хотя бы одна версия видео удовлетворяет условиям ширины и высоты
            for file in video.get("video_files", []):
                if file["width"] > 2000 and file["height"] > 700:
                    video_files.append(file["link"])
                    break
        return video_files
    else:
        print(f"Ошибка при запросе к Pexels API: {response.status_code}")
        return []


def download_videos(video_urls, save_dir=config.VIDEOS_FOLDER):
    """Скачивает видео по указанным ссылкам и сохраняет их в указанную папку."""
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    for i, url in enumerate(video_urls):
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            video_path = os.path.join(save_dir, f"video_{i + 1}.mp4")
            with open(video_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            print(f"Видео сохранено: {video_path}")
        else:
            print(f"Не удалось скачать видео: {url}")


def get_videos_by_tag(tag):
    total_videos_needed = 5
    video_urls = []

    while len(video_urls) < total_videos_needed:
        num_results = total_videos_needed - len(video_urls)
        new_videos = search_videos_on_pexels(tag, num_results)
        if not new_videos:
            print("Не удалось найти больше подходящих видео.")
            break
        video_urls.extend(new_videos[:num_results])

    # Выводим ссылки на найденные видео
    print("Найденные видео на Pexels:")
    for url in video_urls:
        print(url)
