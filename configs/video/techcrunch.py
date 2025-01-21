from data_connectors.techcrunch import fetch_posts
from images_generators.flux_cinestill_replicate import generate_images
from voice_generators.google_speech import text_to_speech
from social_publicators.youtube import upload_video_to_youtube

config = {
    "content": { 
        "fetcher": fetch_posts,
        "num_posts": 5,
        "storage_path": "./data/storages/techcrunch_posts.txt",
        "fetch_delay_sec": 3600,
        "pre_title": "Tech news",
        "prompt": """
                Role: You are the professional tech blogger
                Context: You know all about viral moments and you creating the shorts video for youtube shorts, instagram reels, tiktok based on the tech news. You receive the tech articles "{articles}".
                Task: Create the text for short video with the most interesting tech news from the articles. Make it short like not more than 40 secs. Don't use any formats like emoji etc, just return the text.
                \n{format_instructions}\n
            """,
    },
    "images": {
        "generator": generate_images,
        "lora_scale": 1,
        "aspect_ratio": "9:16",
        "guidance_scale": 3.5,
        "extra_lora_scale": 1,
        "output_quality": 100,
        "width": 810,
        "height": 1440,
        "additional_prompt": " in cinematic style, dark neon light",
        "image_folder_path": "./data/images/techcrunch",
    },
    "speech": {
        "model": text_to_speech,
        "name": "en-US-Journey-D",
        "language_code": "en-US",
        "voice_path": "voice.wav",
    },
    "video": {
        "image_folder_path": "./data/images/techcrunch",
        "output_video_file_name": "temp_video.mp4",
        "video_fps": 60,
        "image_animations_durations": 2,
        "blur_animation": 0.1,
        "transition_animation": 0.1,
    },
    "compose_config": {
        "voice_path": "voice.wav",
        "bg_music_path": "./data/bg_music/music.wav",
        "output_video_name": "output.mp4",
        "font_path": "./data/fonts/font.ttf",
        "font_size": 50,
        "text_color": 'white',
        "highlight_color": '#DF4040',
        "shadow_color": 'black',
        "shadow_opacity": 0.6,
        "shadow_offset_x": 0,
        "shadow_offset_y": 10,
        "stroke_color": 'black',
        "text_stroke_width": 4,
    },
    "social": {
        "youtube": {
            "uploader": upload_video_to_youtube,
            "credentials_path": "techcrunch_credentials.json",
            "token_path": "techcrunch_token.json",
        }
    },
    "telegram": {
        "chat_ids": [244526122, 344864924]
    }
}