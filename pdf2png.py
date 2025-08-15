import streamlit as st
import fitz  # PyMuPDF
import os, tempfile, zipfile, requests
from io import BytesIO

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

def run_pdf_to_png_app():
    st.title("📄 PDF 转 PNG 图片")
    st.markdown("支持上传 PDF 文件或输入 PDF 链接，将 PDF 每一页转换为清晰的 PNG 图片。")

    tab1, tab2 = st.tabs(["📤 上传文件", "🌐 输入链接"])

    zoom = st.slider("🔍 缩放比例（影响清晰度）", 1.0, 5.0, 2.0, step=0.5)
    rotation = st.selectbox("🔄 旋转角度", [0, 90, 180, 270])

    # 上传 PDF
    with tab1:
        uploaded_file = st.file_uploader("上传 PDF 文件", type=["pdf"])
        if uploaded_file:
            with st.spinner("正在转换为图片..."):
                paths, _ = pdf_to_images(uploaded_file.read(), zoom_x=zoom, zoom_y=zoom, rotation_angle=rotation)
            show_results(paths)

    # 输入 PDF 链接
    with tab2:
        pdf_url = st.text_input("请输入 PDF 链接（必须是直接 PDF 文件链接）")
        if pdf_url:
            if st.button("下载并转换"):
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

def show_results(paths):
    st.success(f"转换完成！共 {len(paths)} 页。")
    for i, p in enumerate(paths):
        st.image(p, caption=f"📄 第 {i + 1} 页", use_container_width=True)
    zip_file = zip_images(paths)
    st.download_button("📦 下载全部（ZIP）", data=zip_file, file_name="converted_images.zip", mime="application/zip")

# if __name__ == "__main__":
#     run_pdf_to_png_app()