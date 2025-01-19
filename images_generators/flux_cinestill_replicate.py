from replicate import Client
from configs import config


def generate_images(prompts):
    client = Client(api_token=config.REPLICATE_API_TOKEN)
    i = 0

    for prompt in prompts:
        print("CNSTILL, " + prompt)
        input = {
            "prompt": "CNSTILL, " + prompt + " in cinematic style, dark neon light",
            "lora_scale": 1,
            "aspect_ratio": "9:16",
            "guidance_scale": 3.5,
            "extra_lora_scale": 1,
            "output_quality": 100,
            "width": 810,
            "height": 1440
        }

        output = client.run(
            "adirik/flux-cinestill:216a43b9975de9768114644bbf8cd0cba54a923c6d0f65adceaccfc9383a938f",
            input=input
        )

        for index, item in enumerate(output):
            with open(f"./data/images/{i}.jpg", "wb") as file:
                file.write(item.read())

        i += 1