from data_connectors.techcrunch import fetch_posts
from content_generators.techcrunch import create_content
from voice_generators.kokoro_replicate import text_to_speech
from utils.count_images import calculate_frames_pydub
from images_generators.flux_replicate import generate_images
from video_generators.create_video import create_video
from video_generators.compose_video import merge_audio_video_with_subtitles

def create_video_with_data(data):
    # 1. Generate content for post
    tech_content = create_content(data)
    print(tech_content)

    # 2. Tts with kokoro
    text_to_speech(tech_content['reels_text'])

    # 3. Count images
    duration, frames = calculate_frames_pydub("voice.wav")
    print(duration, frames)

    # 4. Generate images
    generate_images(tech_content['prompts'][:frames])

    # 5. Create video
    create_video("data/images", output_file="video.mp4", fps=60, image_durations=[2] * frames)

    # 6. Add subtitles
    merge_audio_video_with_subtitles("video.mp4", "voice.wav", "data/bg_music/music.wav", "output.mp4", "./data/fonts/font.ttf")