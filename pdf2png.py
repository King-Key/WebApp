import streamlit as st
import fitz  # PyMuPDF
import os, tempfile, zipfile, requests
from io import BytesIO
import markdown2
from weasyprint import HTML

def run_pdf_to_png_app(pdf_stream, zoom_x=2.0, zoom_y=2.0, rotation_angle=0):
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

def markdown_to_image(md_text):
    """将 Markdown 转换为 PNG 图片"""
    html_content = markdown2.markdown(md_text, extras=["fenced-code-blocks", "tables", "strike", "task_list"])
    styled_html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: "Microsoft YaHei", Arial, sans-serif; font-size: 16px; padding: 20px; background: white; color: black; }}
            pre, code {{ background: #f4f4f4; padding: 5px; border-radius: 5px; }}
            h1, h2, h3, h4, h5, h6 {{ color: #333; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; }}
        </style>
    </head>
    <body>{html_content}</body>
    </html>
    """
    tmpdir = tempfile.mkdtemp()
    output_path = os.path.join(tmpdir, "markdown.png")
    HTML(string=styled_html).write_png(output_path)
    return output_path

def show_results(paths):
    st.success(f"转换完成！共 {len(paths)} 张图片。")
    for i, p in enumerate(paths):
        st.image(p, caption=f"图片 {i + 1}", use_container_width=True)
    zip_file = zip_images(paths)
    st.download_button("📦 下载全部（ZIP）", data=zip_file, file_name="converted_images.zip", mime="application/zip")

def run_app():
    st.title("📄 PDF/Markdown 转 PNG 图片")
    st.markdown("支持上传 PDF / 输入 PDF 链接 / 输入 Markdown 内容，生成 PNG 图片。")

    tab1, tab2, tab3 = st.tabs(["📤 上传 PDF", "🌐 PDF 链接", "📝 Markdown 转图片"])

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

    # Markdown 转图片
    with tab3:
        md_input = st.text_area("请输入 Markdown 内容", height=300, placeholder="# 这是标题\n\n- 列表1\n- 列表2\n\n**加粗文本**")
        if st.button("生成图片", key="md_convert"):
            if md_input.strip():
                path = markdown_to_image(md_input)
                show_results([path])
            else:
                st.warning("请输入 Markdown 内容！")

# if __name__ == "__main__":
#     run_app()