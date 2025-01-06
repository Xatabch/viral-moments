from elevenlabs.client import ElevenLabs
from pydub import AudioSegment
import io
from configs import config

def text_to_speech(text):
    client = ElevenLabs(
        api_key=config.ELEVEN_LABS_KEY,
    )

    # Собираем аудио из генератора в байтовый объект
    audio_bytes = b"".join(audio for audio in client.generate(
        text=text,
        voice="Brian",
        model="eleven_multilingual_v2"
    ))

    # Сохранение аудио в формате WAV
    audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
    audio_segment.export(config.VOICE_FILE_NAME, format="wav")

    print("Аудиофайл успешно сохранен как voice.wav")
