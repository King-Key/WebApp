import streamlit as st
import fitz  # PyMuPDF
import os, tempfile, zipfile, requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

def pdf_to_images(pdf_stream, zoom_x=2.0, zoom_y=2.0, rotation_angle=0):
    images = []
    tmpdirname = tempfile.mkdtemp()
    pdf = fitz.open(stream=pdf_stream, filetype="pdf")
    for i in range(len(pdf)):
        matrix = fitz.Matrix(zoom_x, zoom_y).prerotate(rotation_angle)
        pix = pdf[i].get_pixmap(matrix=matrix, alpha=False)
        path = os.path.join(tmpdirname, f"page_{i + 1}.png")
        pix.save(path)
        images.append(path)
    pdf.close()
    return images, tmpdirname

def zip_images(image_paths):
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for p in image_paths:
            zipf.write(p, arcname=os.path.basename(p))
    buffer.seek(0)
    return buffer

def text_to_image(text, font_size=32, image_width=800, padding=20):
    # 创建画布
    font = ImageFont.load_default()
    try:
        font = ImageFont.truetype("arial.ttf", font_size)  # 尝试用更好看的字体
    except:
        pass

    # 估算高度
    lines = text.split("\n")
    line_height = font.getbbox("A")[3] + 10
    image_height = padding * 2 + line_height * len(lines)

    img = Image.new("RGB", (image_width, image_height), color="white")
    draw = ImageDraw.Draw(img)

    y_text = padding
    for line in lines:
        draw.text((padding, y_text), line, font=font, fill="black")
        y_text += line_height

    output_path = os.path.join(tempfile.mkdtemp(), "text_image.png")
    img.save(output_path)
    return output_path

def show_results(paths):
    st.success(f"转换完成！共 {len(paths)} 页/张。")
    for i, p in enumerate(paths):
        st.image(p, caption=f"图片 {i + 1}", use_container_width=True)
    zip_file = zip_images(paths)
    st.download_button("📦 下载全部（ZIP）", data=zip_file, file_name="converted_images.zip", mime="application/zip")

def run_pdf_to_png_app():
    st.title("📄 PDF/文字 转 PNG 图片")
    st.markdown("支持上传 PDF / 输入 PDF 链接 / 输入文字内容，生成 PNG 图片。")

    tab1, tab2, tab3 = st.tabs(["📤 上传 PDF", "🌐 PDF 链接", "📝 文字转图片"])

    zoom = st.slider("🔍 缩放比例（PDF专用）", 1.0, 5.0, 2.0, step=0.5)
    rotation = st.selectbox("🔄 旋转角度（PDF专用）", [0, 90, 180, 270])

    # 上传 PDF
    with tab1:
        uploaded_file = st.file_uploader("上传 PDF 文件", type=["pdf"])
        if uploaded_file:
            with st.spinner("正在转换为图片..."):
                paths, _ = pdf_to_images(uploaded_file.read(), zoom_x=zoom, zoom_y=zoom, rotation_angle=rotation)
            show_results(paths)

    # PDF 链接
    with tab2:
        pdf_url = st.text_input("请输入 PDF 链接")
        if pdf_url and st.button("下载并转换", key="link_convert"):
            try:
                with st.spinner("正在下载 PDF..."):
                    r = requests.get(pdf_url, timeout=15)
                    r.raise_for_status()
                    pdf_bytes = BytesIO(r.content)
                with st.spinner("正在转换为图片..."):
                    paths, _ = pdf_to_images(pdf_bytes.read(), zoom_x=zoom, zoom_y=zoom, rotation_angle=rotation)
                show_results(paths)
            except Exception as e:
                st.error(f"下载或转换失败: {e}")

    # 文字转图片
    with tab3:
        text_input = st.text_area("请输入要生成图片的文字", height=200)
        font_size = st.slider("字体大小", 12, 72, 32)
        if st.button("生成图片", key="text_convert"):
            if text_input.strip():
                path = text_to_image(text_input, font_size=font_size)
                show_results([path])
            else:
                st.warning("请输入文字内容！")

# if __name__ == "__main__":
#     run_app()