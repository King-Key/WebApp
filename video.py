import streamlit as st
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import tempfile
import os
from datetime import datetime

def create_video(images, audio_file, duration_per_image=2):
    clips = []
    for img in images:
        clip = ImageClip(img).set_duration(duration_per_image)
        clips.append(clip)

    video = concatenate_videoclips(clips, method="compose")
    audio = AudioFileClip(audio_file)
    video = video.set_audio(audio)
    
    temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    video.write_videofile(temp_output.name, codec="libx264", audio_codec="aac")
    return temp_output.name

def make_video_from_audio_and_images():
    st.title("🎬 音频 + 图片合成视频")

    audio_file = st.file_uploader("上传音频文件", type=["mp3", "wav"])
    image_files = st.file_uploader("上传多张图片", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    duration = st.slider("每张图片展示时长（秒）", 1, 10, 2)

    if audio_file and image_files:
        if st.button("开始生成视频"):
            with st.spinner("生成中，请稍等..."):
                # 保存临时图片文件
                temp_img_paths = []
                for img_file in image_files:
                    temp_path = os.path.join(tempfile.gettempdir(), img_file.name)
                    with open(temp_path, "wb") as f:
                        f.write(img_file.read())
                    temp_img_paths.append(temp_path)

                # 保存音频文件
                temp_audio_path = os.path.join(tempfile.gettempdir(), audio_file.name)
                with open(temp_audio_path, "wb") as f:
                    f.write(audio_file.read())

                # 生成视频
                video_path = create_video(temp_img_paths, temp_audio_path, duration)

                st.success("视频生成成功！")
                st.video(video_path)
                with open(video_path, "rb") as file:
                    st.download_button("📥 下载视频", file, file_name="output_video.mp4", mime="video/mp4")