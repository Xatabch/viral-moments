from mflux import Flux1, Config

def generate_images(prompts):
    # Load the model
    flux = Flux1.from_alias(
        alias="schnell",  # "schnell" or "dev"
        quantize=8,       # 4 or 8
    )

    i = 0

    for prompt in prompts:
        # Generate an image
        image = flux.generate_image(
        seed=2,
        prompt=prompt,
        config=Config(
            num_inference_steps=4,  # "schnell" works well with 2-4 steps, "dev" works well with 20-25 steps
            height=1280,
            width=720,
            )
        )

        image.save(path=f"images/{i}.jpg")

        i += 1