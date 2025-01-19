from elevenlabs.client import ElevenLabs
from elevenlabs import save
from configs import config

def text_to_speech(text):
    client = ElevenLabs(
        api_key=config.ELEVEN_LABS_KEY,
    )

    audio = client.generate(
        text=text,
        voice="Brian",
        model="eleven_multilingual_v2"
    )

    save(audio, 'voice.wav')