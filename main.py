from get_arxiv_article import get_article

from get_techcrunch_articles import fetch_posts
from techcrunch_content_generator import create_content

from content_generator import create_content as create_arxiv_content
from get_videos import get_videos_by_tag
from tts import text_to_speech
from create_video import create_video_from_content

if __name__ == "__main__":
    # 1. Получаем статью
    # get_article()
    posts = fetch_posts(5)

    # 2. Генерируем контент для ролика
    tech_content = create_content(posts)
    print(tech_content)

    # 3. Генерируем arxiv контент
    # arxiv_content = create_arxiv_content()
    # print(arxiv_content)
    
    # 3. Получаем видео по тегам
    # get_videos_by_tag(content['tag'])
    
    # # 4. Генерируем озвучку
    # text_to_speech(content['reels_text'])
    
    # # 5. Собираем все в видео
    # create_video_from_content()
