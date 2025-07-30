import os
import math
from PIL import Image
import streamlit as st
from io import BytesIO

def made_in_china():
    st.title("🇨🇳 微信头像添加国旗背景")
    st.markdown("上传头像，自动添加五角星渐变国旗背景")

    flag_path = os.path.join("assets", "china.png")
    try:
        motherland_flag = Image.open(flag_path).convert("RGBA")
    except Exception as e:
        st.error(f"无法加载国旗图片: {e}")
        return

    head_picture = st.file_uploader("上传头像（PNG或JPG）", type=["png", "jpg", "jpeg"])
    if head_picture:
        key = st.slider("渐变强度（值越大，覆盖越轻）", 2.0, 8.0, 4.5, step=0.1)
        head_picture = Image.open(head_picture).convert("RGBA")
        flag_width, flag_height = motherland_flag.size
        crop_flag = motherland_flag.crop((66, 0, flag_height + 66, flag_height))
        for i in range(flag_height):
            for j in range(flag_height):
                color = crop_flag.getpixel((i, j))
                distance = int(math.sqrt(i * i + j * j))
                alpha = max(255 - int(distance / key), 0)
                new_color = (*color[:-1], alpha)
                crop_flag.putpixel((i, j), new_color)
        resized_flag = crop_flag.resize(head_picture.size)
        head_picture.paste(resized_flag, (0, 0), resized_flag)
        st.image(head_picture, caption="添加国旗后的头像")
        buffer = BytesIO()
        head_picture.save(buffer, format="PNG")
        buffer.seek(0)
        st.download_button("📥 下载头像", data=buffer, file_name="china_avatar.png", mime="image/png")
