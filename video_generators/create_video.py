import cv2
import numpy as np
from PIL import Image
import glob
import os

def load_images(image_paths):
    """Загружает изображения (PIL -> BGR для OpenCV) в порядке чисел в именах файлов."""
    sorted_paths = sorted(image_paths, key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))
    return [cv2.cvtColor(np.array(Image.open(p)), cv2.COLOR_RGB2BGR) for p in sorted_paths]

def create_sequences(num_images):
    """
    Динамически создает последовательности анимаций и переходов для указанного количества изображений.
    """
    base_animation_sequence = [
        zoom_out_animation,
        slide_left_to_right_inside,
        zoom_in_animation,
        zoom_out_animation,
        zoom_out_animation
    ]
    base_transition_sequence = [
        bottom_to_top_transition,
        left_to_right_transition,
        top_right_to_bottom_left_transition,
        bottom_to_top_transition
    ]

    animation_sequence = [base_animation_sequence[i % len(base_animation_sequence)] for i in range(num_images)]
    transition_sequence = [base_transition_sequence[i % len(base_transition_sequence)] for i in range(num_images - 1)]

    return animation_sequence, transition_sequence

# ---------------------------------------------------------------------------------
#                       Утилита для масштабирования/обрезки
# ---------------------------------------------------------------------------------

def resize_and_crop(img, scale, shape):
    """
    Масштабируем картинку относительно (h, w) и обрезаем по центру до точно (h, w).
    """
    h, w = shape
    new_w = int(w * scale)
    new_h = int(h * scale)
    scaled_img = cv2.resize(img, (new_w, new_h))

    dy = int((new_h - h) * 0.5)
    dx = int((new_w - w) * 0.5)
    roi = scaled_img[dy:dy + h, dx:dx + w]
    return roi

# ---------------------------------------------------------------------------------
#                          Подготовка к анимации img2
# ---------------------------------------------------------------------------------

def prepare_for_animation(img, animation_func, shape,
                          scale_pan=1.2, scale_in=(1.0, 1.2), scale_out=(1.2, 1.0)):
    """
    Готовит (масштабирует) изображение `img` к тому состоянию,
    с которого начнётся анимация `animation_func`.
    """
    if animation_func == zoom_out_animation:
        start_scale = scale_out[0]
    elif animation_func == zoom_in_animation:
        start_scale = scale_in[0]
    elif animation_func in (
            slide_left_to_right_inside,
            slide_right_to_left_inside,
            slide_top_to_bottom_inside,
            slide_bottom_to_top_inside,
            slide_top_left_to_bottom_right_inside
    ):
        start_scale = scale_pan
    else:
        start_scale = 1.0

    return resize_and_crop(img, start_scale, shape)

# ---------------------------------------------------------------------------------
#                       Анимации (PAN) одного изображения
# ---------------------------------------------------------------------------------

def slide_left_to_right_inside(img, steps, shape, scale):
    h, w = shape
    zoom_w = int(w * scale)
    zoom_h = int(h * scale)
    zoomed_img = cv2.resize(img, (zoom_w, zoom_h))

    frames = []
    start_x = 0
    end_x = zoom_w - w

    for step in range(steps + 1):
        cur_x = int(start_x + (end_x - start_x) * step / steps)
        roi = zoomed_img[0:h, cur_x:cur_x + w]
        frames.append(roi)
    return frames

def slide_right_to_left_inside(img, steps, shape, scale):
    h, w = shape
    zoom_w = int(w * scale)
    zoom_h = int(h * scale)
    zoomed_img = cv2.resize(img, (zoom_w, zoom_h))

    frames = []
    start_x = zoom_w - w
    end_x = 0

    for step in range(steps + 1):
        cur_x = int(start_x + (end_x - start_x) * step / steps)
        roi = zoomed_img[0:h, cur_x:cur_x + w]
        frames.append(roi)
    return frames

def slide_top_to_bottom_inside(img, steps, shape, scale):
    h, w = shape
    zoom_w = int(w * scale)
    zoom_h = int(h * scale)
    zoomed_img = cv2.resize(img, (zoom_w, zoom_h))

    frames = []
    start_y = 0
    end_y = zoom_h - h

    for step in range(steps + 1):
        cur_y = int(start_y + (end_y - start_y) * step / steps)
        roi = zoomed_img[cur_y:cur_y + h, 0:w]
        frames.append(roi)
    return frames

def slide_bottom_to_top_inside(img, steps, shape, scale):
    h, w = shape
    zoom_w = int(w * scale)
    zoom_h = int(h * scale)
    zoomed_img = cv2.resize(img, (zoom_w, zoom_h))

    frames = []
    start_y = zoom_h - h
    end_y = 0

    for step in range(steps + 1):
        cur_y = int(start_y + (end_y - start_y) * step / steps)
        roi = zoomed_img[cur_y:cur_y + h, 0:w]
        frames.append(roi)
    return frames

def slide_top_left_to_bottom_right_inside(img, steps, shape, scale):
    h, w = shape
    zoom_w = int(w * scale)
    zoom_h = int(h * scale)
    zoomed_img = cv2.resize(img, (zoom_w, zoom_h))

    frames = []
    start_x, start_y = 0, 0
    end_x = zoom_w - w
    end_y = zoom_h - h

    for step in range(steps + 1):
        cur_x = int(start_x + (end_x - start_x) * step / steps)
        cur_y = int(start_y + (end_y - start_y) * step / steps)
        roi = zoomed_img[cur_y:cur_y + h, cur_x:cur_x + w]
        frames.append(roi)
    return frames

# ---------------------------------------------------------------------------------
#                       Zoom-анимации одного изображения
# ---------------------------------------------------------------------------------

def zoom_in_animation(img, steps, shape, start_scale, end_scale):
    """
    Анимация увеличения: от start_scale к end_scale.
    """
    frames = []
    for step in range(steps + 1):
        alpha = step / steps
        scale = start_scale + alpha * (end_scale - start_scale)
        roi = resize_and_crop(img, scale, shape)
        frames.append(roi)
    return frames

def zoom_out_animation(img, steps, shape, start_scale, end_scale):
    """
    Анимация уменьшения: от start_scale к end_scale.
    """
    frames = []
    for step in range(steps + 1):
        alpha = step / steps
        scale = start_scale + alpha * (end_scale - start_scale)
        roi = resize_and_crop(img, scale, shape)
        frames.append(roi)
    return frames

# ---------------------------------------------------------------------------------
#                       Эффект Blur
# ---------------------------------------------------------------------------------

def blur_effect(img, steps, shape):
    """
    Эффект размытия, возвращает список кадров.
    """
    h, w = shape
    base = cv2.resize(img, (w, h))

    frames = []
    max_kernel_size = 51
    for i in range(steps):
        ksize = 1 + 2 * (i * max_kernel_size // steps)
        blurred = cv2.GaussianBlur(base, (ksize, ksize), 0)
        frames.append(blurred)
    return frames

# ---------------------------------------------------------------------------------
#                       Переходы между изображениями
# ---------------------------------------------------------------------------------
def top_to_bottom_transition(img1, img2, steps, shape):
    h, w = shape
    i1 = cv2.resize(img1, (w, h))
    i2 = cv2.resize(img2, (w, h))

    frames = []
    for step in range(steps + 1):
        dy = int(h * step / steps)
        slide = np.zeros_like(i1)
        slide[:h - dy, :] = i1[dy:, :]
        slide[h - dy:, :] = i2[:dy, :]
        frames.append(slide)
    return frames

def bottom_to_top_transition(img1, img2, steps, shape):
    h, w = shape
    i1 = cv2.resize(img1, (w, h))
    i2 = cv2.resize(img2, (w, h))

    frames = []
    for step in range(steps + 1):
        dy = int(h * step / steps)
        slide = np.zeros_like(i1)
        slide[dy:, :] = i1[:h - dy, :]
        slide[:dy, :] = i2[h - dy:, :]
        frames.append(slide)
    return frames

def left_to_right_transition(img1, img2, steps, shape):
    h, w = shape
    i1 = cv2.resize(img1, (w, h))
    i2 = cv2.resize(img2, (w, h))

    frames = []
    for step in range(steps + 1):
        dx = int(w * step / steps)
        slide = np.zeros_like(i1)
        slide[:, :w - dx] = i1[:, dx:]
        slide[:, w - dx:] = i2[:, :dx]
        frames.append(slide)
    return frames

def right_to_left_transition(img1, img2, steps, shape):
    h, w = shape
    i1 = cv2.resize(img1, (w, h))
    i2 = cv2.resize(img2, (w, h))

    frames = []
    for step in range(steps + 1):
        dx = int(w * step / steps)
        slide = np.zeros_like(i1)
        slide[:, dx:] = i1[:, :w - dx]
        slide[:, :dx] = i2[:, w - dx:]
        frames.append(slide)
    return frames

def top_right_to_bottom_left_transition(img1, img2, steps, shape):
    h, w = shape
    i1 = cv2.resize(img1, (w, h))
    i2 = cv2.resize(img2, (w, h))

    frames = []
    for step in range(steps + 1):
        dx = w - int(w * step / steps)
        dy = int(h * step / steps)
        slide = np.zeros_like(i1)

        slide[dy:, :dx] = i1[:h - dy, w - dx:]
        slide[:dy, dx:] = i2[h - dy:, :w - dx]
        frames.append(slide)
    return frames

# ---------------------------------------------------------------------------------
#                           Основная логика (main)
# ---------------------------------------------------------------------------------

def create_video(video_config):
    image_paths = glob.glob(f"{video_config['image_folder_path']}/*.jpg")
    images = load_images(image_paths)
    num_images = len(images)

    if num_images < 2:
        print("Нужно минимум 2 изображения для слайдшоу.")
        return

    image_duration = video_config['image_animations_durations']
    h, w, _ = images[0].shape
    fps = video_config['video_fps']
    blur_animation_duration = video_config.get('blur_animation', 0.1)
    transition_animation_duration = video_config.get('transition_animation', 0.1)
    output_file = video_config['output_video_file_name']

    animation_sequence, transition_sequence = create_sequences(num_images)

    def get_animation(i):
        return animation_sequence[i % len(animation_sequence)]

    def get_transition(i):
        return transition_sequence[i % len(transition_sequence)]

    all_frames = []

    for i in range(num_images - 1):
        img1 = images[i]
        img2 = images[i + 1]

        next_anim_func = get_animation(i + 1) if i + 1 < num_images - 1 else None
        current_anim_func = get_animation(i)
        anim_steps = int(fps * image_duration)

        if current_anim_func == zoom_in_animation:
            animation_frames = zoom_in_animation(img1, steps=anim_steps, shape=(h, w),
                                                 start_scale=1.0, end_scale=1.2)
        elif current_anim_func == zoom_out_animation:
            animation_frames = zoom_out_animation(img1, steps=anim_steps, shape=(h, w),
                                                  start_scale=1.2, end_scale=1.0)
        elif current_anim_func in (
                slide_left_to_right_inside,
                slide_right_to_left_inside,
                slide_top_to_bottom_inside,
                slide_bottom_to_top_inside,
                slide_top_left_to_bottom_right_inside
        ):
            animation_frames = current_anim_func(img1, steps=anim_steps, shape=(h, w), scale=1.2)
        else:
            animation_frames = [cv2.resize(img1, (w, h))]

        all_frames.extend(animation_frames)
        final_animated_frame = animation_frames[-1]

        blur_steps = int(fps * blur_animation_duration)
        blur_frames = blur_effect(final_animated_frame, steps=blur_steps, shape=(h, w))
        all_frames.extend(blur_frames)
        blurred_image = blur_frames[-1]

        img2_prepared = prepare_for_animation(img2, next_anim_func,
                                              shape=(h, w),
                                              scale_pan=1.2,
                                              scale_in=(1.0, 1.2),
                                              scale_out=(1.2, 1.0))

        transition_func = get_transition(i)
        transition_steps = int(fps * transition_animation_duration)
        transition_frames = transition_func(blurred_image, img2_prepared,
                                            steps=transition_steps, shape=(h, w))
        all_frames.extend(transition_frames)

    # Обработка последнего изображения с анимацией
    last_index = num_images - 1
    last_img = images[last_index]
    current_anim_func = get_animation(last_index)
    anim_steps = int(fps * image_duration)

    if current_anim_func == zoom_in_animation:
        animation_frames = zoom_in_animation(last_img, steps=anim_steps, shape=(h, w),
                                             start_scale=1.0, end_scale=1.2)
    elif current_anim_func == zoom_out_animation:
        animation_frames = zoom_out_animation(last_img, steps=anim_steps, shape=(h, w),
                                              start_scale=1.2, end_scale=1.0)
    elif current_anim_func in (
            slide_left_to_right_inside,
            slide_right_to_left_inside,
            slide_top_to_bottom_inside,
            slide_bottom_to_top_inside,
            slide_top_left_to_bottom_right_inside
    ):
        animation_frames = current_anim_func(last_img, steps=anim_steps, shape=(h, w), scale=1.2)
    else:
        animation_frames = [cv2.resize(last_img, (w, h))]

    all_frames.extend(animation_frames)

    print(f"Всего кадров: {len(all_frames)}")

    fourcc = cv2.VideoWriter.fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_file, fourcc, fps, (w, h))
    for f in all_frames:
        writer.write(f)
    writer.release()
    print(f"Слайдшоу сохранено: {output_file}")