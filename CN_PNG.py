from PIL import Image
import math
import streamlit as st


# key = 4.5  # 修改key值可以调整国旗的范围，推荐2~4之间的数字，支持小数
def makde_in_china():
    motherland_flag = Image.open('assert/china.png').convert("RGBA")
    head_picture = st.file_uploader("上传PNG或JPG")

    if head_picture:
        key = st.slider("选择透明度",4.5,8.0,3.0)
        head_picture = Image.open(head_picture)
        # 截图国旗上的五颗五角星
        flag_width, flag_height = motherland_flag.size
        crop_flag = motherland_flag.crop((66, 0, flag_height+66, flag_height))
        # 将国旗截图处理成颜色渐变
        for i in range(flag_height):
            for j in range(flag_height):
                color = crop_flag.getpixel((i, j))
                distance = int(math.sqrt(i*i + j*j))
                alpha = 255 - int(distance//key)
                new_color = (*color[0:-1], alpha if alpha > 0 else 0)
                crop_flag.putpixel((i, j), new_color)
        # 修改渐变图片的尺寸，适应头像大小，粘贴到头像上
        new_crop_flag = crop_flag.resize(head_picture.size)
        head_picture.paste(new_crop_flag, (0, 0), new_crop_flag)
        st.image(head_picture)

