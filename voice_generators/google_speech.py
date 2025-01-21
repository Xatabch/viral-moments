from google.cloud import texttospeech

def text_to_speech(text, config):
    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.VoiceSelectionParams(
        name=config["name"],
        language_code=config["language_code"]
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    path = config["voice_path"]
    # The response's audio_content is binary.
    with open(path, "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        print(f"Audio content written to file {path}")