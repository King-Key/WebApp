import streamlit as st
import fitz  # PyMuPDF
import os, tempfile, zipfile, requests, re
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import textwrap

# ====== PDF 转图片 ======
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

# ====== Markdown 转图片（简易样式版） ======
def markdown_to_image(md_text, font_size=20, width=800, padding=20):
    # 尝试加载字体
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
        bold_font = ImageFont.truetype("arialbd.ttf", font_size)
        mono_font = ImageFont.truetype("cour.ttf", font_size)
    except:
        font = ImageFont.load_default()
        bold_font = font
        mono_font = font

    lines = []
    for raw_line in md_text.split("\n"):
        line = raw_line.rstrip()
        
        # 标题
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            text = line.lstrip("#").strip()
            lines.append(("bold", f"{'  ' * (level-1)}{text}"))
        # 代码块（```开头结尾）
        elif line.startswith("```") or line.endswith("```"):
            lines.append(("code", ""))
        elif line.startswith("- "):
            lines.append(("normal", "• " + line[2:]))
        elif re.match(r"\d+\.\s", line):
            lines.append(("normal", line))
        elif "**" in line:  # 粗体
            text = line.replace("**", "")
            lines.append(("bold", text))
        elif line.startswith("    ") or line.startswith("\t"):
            lines.append(("code", line.strip()))
        else:
            lines.append(("normal", line))

    # 计算图片高度
    line_height = font.getbbox("A")[3] + 8
    img_height = padding * 2 + len(lines) * line_height
    img = Image.new("RGB", (width, img_height), color="white")
    draw = ImageDraw.Draw(img)

    y = padding
    code_bg_color = (240, 240, 240)

    for style, text in lines:
        if style == "bold":
            draw.text((padding, y), text, font=bold_font, fill="black")
        elif style == "code":
            text_box_width = width - padding * 2
            draw.rectangle([padding, y, padding + text_box_width, y + line_height], fill=code_bg_color)
            draw.text((padding + 5, y), text, font=mono_font, fill="black")
        else:
            wrapped = textwrap.wrap(text, width=60)
            for wline in wrapped:
                draw.text((padding, y), wline, font=font, fill="black")
                y += line_height
            y -= line_height  # 避免多加一次
        y += line_height

    output_path = os.path.join(tempfile.mkdtemp(), "markdown.png")
    img.save(output_path)
    return output_path

# ====== 显示结果 ======
def show_results(paths):
    st.success(f"转换完成！共 {len(paths)} 张图片。")
    for i, p in enumerate(paths):
        st.image(p, caption=f"图片 {i + 1}", use_container_width=True)
    zip_file = zip_images(paths)
    st.download_button("📦 下载全部（ZIP）", data=zip_file, file_name="converted_images.zip", mime="application/zip")

# ====== 主程序 ======
def run_pdf_to_png_app():
    st.title("📄 PDF / Markdown 转 PNG 图片")
    st.markdown("支持上传 PDF / 输入 PDF 链接 / 输入 Markdown 内容，生成 PNG 图片。")

    tab1, tab2, tab3 = st.tabs(["📤 上传 PDF", "🌐 PDF 链接", "📝 Markdown 转图片"])

    zoom = st.slider("🔍 缩放比例（PDF 专用）", 1.0, 5.0, 2.0, step=0.5)
    rotation = st.selectbox("🔄 旋转角度（PDF 专用）", [0, 90, 180, 270])

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
        md_input = st.text_area(
            "请输入 Markdown 内容",
            "# 标题示例\n\n- 列表1\n- 列表2\n\n**加粗文本**\n\n```\n代码块示例\n```",
            height=300
        )
        font_size = st.slider("字体大小", 12, 40, 20)
        if st.button("生成图片", key="md_convert"):
            if md_input.strip():
                path = markdown_to_image(md_input, font_size=font_size)
                show_results([path])
            else:
                st.warning("请输入 Markdown 内容！")

# if __name__ == "__main__":
#     run_app()