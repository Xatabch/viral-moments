from replicate import Client
from configs import config as base_config

def generate_images(prompts, config):
    client = Client(api_token=base_config.REPLICATE_API_TOKEN)
    i = 0

    for prompt in prompts:
        if config["additional_prompt"]:
            prompt = prompt + config["additional_prompt"]

        print("CNSTILL, " + prompt)

        input = {
            "prompt": "CNSTILL, " + prompt,
            "lora_scale": config["lora_scale"],
            "aspect_ratio": config["aspect_ratio"],
            "guidance_scale": config["guidance_scale"],
            "extra_lora_scale": config["extra_lora_scale"],
            "output_quality": config["output_quality"],
            "width": config["width"],
            "height": config["height"]
        }

        output = client.run(
            "adirik/flux-cinestill:216a43b9975de9768114644bbf8cd0cba54a923c6d0f65adceaccfc9383a938f",
            input=input
        )

        folder = config["image_folder_path"]
        path = f"{folder}/{i}.jpg"

        for _, item in enumerate(output):
            with open(path, "wb") as file:
                file.write(item.read())

        i += 1