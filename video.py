from moviepy.editor import (
    ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
)
import streamlit as st
import tempfile
import os
from datetime import datetime


def make_video_from_audio_and_images():
    st.title("🎬 图片 + 音频生成视频（含字幕和转场）")
    st.write("上传音频和图片，自动合成带字幕和转场的视频。")

    audio_file = st.file_uploader("上传音频文件", type=["mp3", "wav"])
    image_files = st.file_uploader("上传多张图片", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    subtitle_input = st.text_area("填写字幕（可选，每行一张图片）", height=150, placeholder="每张图片一句话，不填写则自动编号。")

    crossfade_duration = st.slider("设置转场时长（秒）", 0.5, 2.0, 1.0, step=0.1)

    if audio_file and image_files:
        with st.spinner("视频生成中..."):

            # 读取音频文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.name)[-1]) as tmp_audio:
                tmp_audio.write(audio_file.read())
                audio_path = tmp_audio.name
            audio_clip = AudioFileClip(audio_path)
            total_duration = audio_clip.duration

            # 准备字幕
            subtitle_lines = subtitle_input.strip().splitlines() if subtitle_input.strip() else [
                f"图片 {i+1}" for i in range(len(image_files))
            ]

            duration_per_img = total_duration / len(image_files)
            clips = []

            for idx, (img_file, subtitle) in enumerate(zip(image_files, subtitle_lines)):
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(img_file.name)[-1]) as tmp_img:
                    tmp_img.write(img_file.read())
                    img_path = tmp_img.name

                # 图像片段
                image_clip = ImageClip(img_path).set_duration(duration_per_img).resize(height=720)

                # 文本片段（字幕）
                txt_clip = TextClip(subtitle, fontsize=40, color='white', bg_color='black', font='Arial-Bold')
                txt_clip = txt_clip.set_duration(duration_per_img).set_position(('center', 'bottom'))

                # 合成图像+字幕
                final_clip = CompositeVideoClip([image_clip, txt_clip])
                clips.append(final_clip)

            # 添加转场
            final_video = concatenate_videoclips(clips, method="compose", padding=-crossfade_duration, 
                                                 transition=lambda c1, c2: c1.crossfadeout(crossfade_duration))

            final_video = final_video.set_audio(audio_clip)

            # 导出视频
            now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(tempfile.gettempdir(), f"video_{now_str}.mp4")
            final_video.write_videofile(output_path, fps=24, codec='libx264')

            with open(output_path, "rb") as f:
                st.success("✅ 视频生成成功！")
                st.download_button("📥 下载视频", f.read(), file_name="合成视频.mp4", mime="video/mp4")