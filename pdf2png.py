import streamlit as st
import fitz  # PyMuPDF
import os, tempfile, zipfile
from io import BytesIO

def pdf_to_images(pdf_file, zoom_x=2.0, zoom_y=2.0, rotation_angle=0):
    images = []
    tmpdirname = tempfile.mkdtemp()
    pdf = fitz.open(stream=pdf_file.read(), filetype="pdf")
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

def run_pdf_to_png_app():
    st.title("📄 PDF 转 PNG 图片")
    st.markdown("将 PDF 每一页转换为清晰的 PNG 图片。")

    uploaded_file = st.file_uploader("📤 上传 PDF 文件", type=["pdf"])
    if uploaded_file:
        zoom = st.slider("🔍 缩放比例（影响清晰度）", 1.0, 5.0, 2.0, step=0.5)
        rotation = st.selectbox("🔄 旋转角度", [0, 90, 180, 270])

        with st.spinner("正在转换为图片..."):
            paths, _ = pdf_to_images(uploaded_file, zoom_x=zoom, zoom_y=zoom, rotation_angle=rotation)

        st.success(f"转换完成！共 {len(paths)} 页。")
        for i, p in enumerate(paths):
            st.image(p, caption=f"📄 第 {i + 1} 页", use_container_width=True)

        zip_file = zip_images(paths)
        st.download_button("📦 下载全部（ZIP）", data=zip_file, file_name="converted_images.zip", mime="application/zip")