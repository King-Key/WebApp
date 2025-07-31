from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    concatenate_videoclips,
    CompositeVideoClip,
    TextClip
)
from PIL import Image
import os
import tempfile

# 自动兼容 Pillow 新旧版本的缩放方式
try:
    resample = Image.Resampling.LANCZOS
except AttributeError:
    resample = Image.LANCZOS

def make_video_from_audio_and_images(images, audio_file, subtitles=None, duration_per_image=3):
    """
    将上传的图片与音频合成为一个视频，图片可加字幕，含淡入淡出转场效果。

    :param images: 图片文件列表（streamlit 上传的文件）
    :param audio_file: 音频文件（streamlit 上传的文件）
    :param subtitles: 字幕文本列表（可选）
    :param duration_per_image: 每张图持续秒数
    :return: 输出视频路径
    """
    clips = []
    tmp_dir = tempfile.mkdtemp()

    for idx, img_file in enumerate(images):
        # 保存临时图片
        img_path = os.path.join(tmp_dir, f"image_{idx}.png")
        image = Image.open(img_file).convert("RGB")
        image = image.resize((1280, 720), resample)
        image.save(img_path)

        # 创建 ImageClip 并加字幕
        img_clip = ImageClip(img_path).set_duration(duration_per_image)

        # 添加字幕（如果有）
        if subtitles and idx < len(subtitles) and subtitles[idx].strip():
            txt = TextClip(subtitles[idx], fontsize=48, color='white', font='Arial-Bold', method='caption',
                           size=(1180, None)).set_position(("center", "bottom")).set_duration(duration_per_image)
            img_clip = CompositeVideoClip([img_clip, txt])

        # 添加淡入淡出效果
        img_clip = img_clip.crossfadein(0.5).crossfadeout(0.5)

        clips.append(img_clip)

    # 合并所有图片 clip
    video = concatenate_videoclips(clips, method="compose")

    # 添加音频
    audio = AudioFileClip(audio_file)
    final = video.set_audio(audio)

    # 保证音视频同步，裁剪为音频长度
    final = final.set_duration(audio.duration)

    # 输出文件路径
    output_path = os.path.join(tmp_dir, "output_video.mp4")
    final.write_videofile(output_path, fps=24)

    return output_path