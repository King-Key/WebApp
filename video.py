from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    concatenate_videoclips,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips
)
from PIL import Image
import os
import tempfile

def make_video_from_audio_and_images(audio_file, image_files, subtitle_text="这是一个合成视频", duration_per_image=3):
    # 加载音频
    audio = AudioFileClip(audio_file)

    # 判断 Pillow 版本使用正确的 resample
    try:
        resample = Image.Resampling.LANCZOS
    except AttributeError:
        resample = Image.ANTIALIAS

    # 创建视频片段列表
    clips = []
    for idx, img_file in enumerate(image_files):
        # 打开图片并转换为 RGB 格式
        image = Image.open(img_file).convert("RGB")

        # 缩放为统一尺寸（可自定义）
        image = image.resize((720, 480), resample)

        # 临时保存处理后的图片
        tmp_img_path = os.path.join(tempfile.gettempdir(), f"frame_{idx}.png")
        image.save(tmp_img_path)

        # 创建 ImageClip
        img_clip = ImageClip(tmp_img_path).set_duration(duration_per_image).fadein(0.5).fadeout(0.5)

        # 添加字幕
        subtitle = TextClip(subtitle_text, fontsize=24, color='white', font='Arial', bg_color='black')
        subtitle = subtitle.set_duration(duration_per_image).set_position(("center", "bottom"))

        # 合成字幕和图像
        final_clip = CompositeVideoClip([img_clip, subtitle])
        clips.append(final_clip)

    # 拼接所有图像片段
    video = concatenate_videoclips(clips, method="compose")

    # 配上音频并设置为最终时长
    video = video.set_audio(audio).set_duration(audio.duration)

    # 输出视频文件
    output_path = os.path.join(tempfile.gettempdir(), "final_video.mp4")
    video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')

    return output_path