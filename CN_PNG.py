from PIL import Image
import numpy as np
import streamlit as st


@st.cache_resource
def _load_flag():
    return Image.open("assets/china.png").convert("RGBA")


def _build_overlay(flag: Image.Image, strength: float, target_size):
    _, h = flag.size
    region = flag.crop((66, 0, h + 66, h)).convert("RGBA")
    region_arr = np.array(region, dtype=np.uint8)

    y_idx, x_idx = np.indices((h, h))
    distance = np.sqrt(x_idx * x_idx + y_idx * y_idx)
    alpha_mask = np.clip(255 - np.floor(distance / strength), 0, 255).astype(np.uint8)
    region_arr[..., 3] = np.minimum(region_arr[..., 3], alpha_mask)

    return Image.fromarray(region_arr, mode="RGBA").resize(target_size)


def made_in_china():
    st.title("🇨🇳 微信头像加国旗")
    st.markdown("上传头像，自动添加渐变国旗背景。")

    flag = _load_flag()
    head = st.file_uploader("📤 上传头像 (PNG/JPG)", type=["png", "jpg", "jpeg"])

    if head:
        strength = st.slider("🇨🇳 国旗渐变强度", 4.0, 8.0, 4.5, 0.1)
        head = Image.open(head).convert("RGBA")
        overlay = _build_overlay(flag=flag, strength=strength, target_size=head.size)
        head.paste(overlay, (0, 0), overlay)
        st.image(head, caption="🇨🇳 添加成功的头像", use_container_width=True)


# backward compatibility
def makde_in_china():
    made_in_china()
