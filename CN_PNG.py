from PIL import Image
import math
import streamlit as st

def makde_in_china():
    st.title("🇨🇳 微信头像加国旗")
    st.markdown("上传头像，自动添加渐变国旗背景。")

    flag = Image.open('assets/china.png').convert("RGBA")
    head = st.file_uploader("📤 上传头像 (PNG/JPG)", type=["png", "jpg", "jpeg"])

    if head:
        strength = st.slider("🇨🇳 国旗渐变强度", 4.0, 8.0, 4.5, 0.1)
        head = Image.open(head).convert("RGBA")
        w, h = flag.size
        region = flag.crop((66, 0, h + 66, h))

        for i in range(h):
            for j in range(h):
                c = region.getpixel((i, j))
                d = int(math.sqrt(i * i + j * j))
                alpha = 255 - int(d // strength)
                region.putpixel((i, j), (*c[0:-1], max(0, alpha)))

        overlay = region.resize(head.size)
        head.paste(overlay, (0, 0), overlay)
        st.image(head, caption="🇨🇳 添加成功的头像", use_container_width=True)