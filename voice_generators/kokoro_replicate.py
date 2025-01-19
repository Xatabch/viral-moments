from replicate import Client
from configs import config

def text_to_speech(text):
    client = Client(api_token=config.REPLICATE_API_TOKEN)

    input = {
        "text": text,
        "speed": 1,
        "voice": "am_adam",
    }

    output = client.run(
        "jaaari/kokoro-82m:dfdf537ba482b029e0a761699e6f55e9162cfd159270bfe0e44857caa5f275a6",
        input=input
    )

    with open("voice.wav", "wb") as file:
        file.write(output.read())