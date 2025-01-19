from replicate import Client
from configs import config


def generate_images(prompts):
    client = Client(api_token=config.REPLICATE_API_TOKEN)
    i = 0

    for prompt in prompts:
        print(prompt)
        input = {
            "prompt": prompt + " in cinematic style, dark neon light",
            "aspect_ratio": "9:16"
        }

        output = client.run(
            "black-forest-labs/flux-1.1-pro-ultra",
            input=input
        )

        with open(f"./data/images/{i}.jpg", "wb") as file:
            file.write(output.read())

        i += 1