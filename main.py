from get_article import get_article_for_content
from content_generator import create_content
from get_videos import get_videos_by_tag
from tts import text_to_speech
from create_video import create_video_from_content

if __name__ == "__main__":
    # 1. Получаем статью
    # get_article_for_content()

    #2. Генерируем контент для ролика
    content = create_content()
    print(content)
    
    # 3. Получаем видео по тегам
    # get_videos_by_tag(content['tag'])
    
    # # 4. Генерируем озвучку
    # text_to_speech(content['reels_text'])
    
    # # 5. Собираем все в видео
    # create_video_from_content()
