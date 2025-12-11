import streamlit as st
import os, tempfile, zipfile, requests, re
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import textwrap
import fitz
import numpy as np

# ====== PDF 转图片（纵向合并功能） ======
def pdf_to_images(pdf_stream, pages_per_image=1, zoom_x=2.0, zoom_y=2.0, rotation_angle=0):
    images = []
    tmpdirname = tempfile.mkdtemp()
    
    # 临时目录用于存放单页的中间图片
    temp_page_dir = tempfile.mkdtemp()
    
    pdf = fitz.open(stream=pdf_stream, filetype="pdf")
    num_pages = len(pdf)
    
    # 确保 pages_per_image 至少为 1
    pages_per_image = max(1, pages_per_image)

    # 1. 预转换所有单页为 PIL Image 对象
    pil_pages = []
    page_width, page_height = 0, 0
    matrix = fitz.Matrix(zoom_x, zoom_y).prerotate(rotation_angle)
    
    for i in range(num_pages):
        pix = pdf[i].get_pixmap(matrix=matrix, alpha=False)
        img_data = pix.tobytes("ppm")
        pil_img = Image.open(BytesIO(img_data))
        pil_pages.append(pil_img)
        if i == 0:
            page_width, page_height = pil_img.size
            
    pdf.close()

    # 2. 按指定数量合并图片
    for i in range(0, num_pages, pages_per_image):
        current_pages = pil_pages[i:i + pages_per_image]
        
        # <<< 核心修改 >>>
        # 计算合并后画布的大小（纵向合并）
        merged_width = page_width  # 宽度保持单页宽度
        merged_height = page_height * len(current_pages) # 高度为所有页高之和
        
        # 创建空白画布
        merged_img = Image.new('RGB', (merged_width, merged_height), color='white')
        
        # 粘贴页面
        y_offset = 0  # 使用 Y 轴偏移量
        for page_img in current_pages:
            # 粘贴到 (0, y_offset) 位置
            merged_img.paste(page_img, (0, y_offset)) 
            # 增加 Y 偏移量
            y_offset += page_height 
        
        # 保存合并后的图片
        output_path = os.path.join(tmpdirname, f"merged_page_{i // pages_per_image + 1}.png")
        merged_img.save(output_path)
        images.append(output_path)
        
    return images, tmpdirname

def zip_images(image_paths):
    buffer = BytesIO()
    # 修正错误：使用 ZIP_DEFLATED
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
    in_code_block = False 
    for raw_line in md_text.split("\n"):
        line = raw_line.rstrip()
        
        if line.startswith("```"):
            in_code_block = not in_code_block
            continue
        
        if in_code_block:
            lines.append(("code", line))
            continue

        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            text = line.lstrip("#").strip()
            lines.append(("bold", f"{'  ' * (level-1)}{text}"))
        elif line.startswith("- "):
            lines.append(("normal", "• " + line[2:]))
        elif re.match(r"\d+\.\s", line):
            lines.append(("normal", line))
        elif "**" in line:
            text = line.replace("**", "")
            lines.append(("bold", text))
        elif line.startswith("    ") or line.startswith("\t"):
            lines.append(("code", line.strip()))
        else:
            lines.append(("normal", line))

    line_height = font.getbbox("A")[3] + 8
    
    total_lines = 0
    for style, text in lines:
        if style in ["bold", "code"]:
            total_lines += 1
        else:
            wrapped = textwrap.wrap(text, width=60)
            total_lines += max(1, len(wrapped))
            
    img_height = padding * 2 + total_lines * line_height
    
    img = Image.new("RGB", (width, img_height), color="white")
    draw = ImageDraw.Draw(img)

    y = padding
    code_bg_color = (240, 240, 240)

    for style, text in lines:
        if style == "bold":
            draw.text((padding, y), text, font=bold_font, fill="black")
            y += line_height
        elif style == "code":
            text_box_width = width - padding * 2
            draw.rectangle([padding, y, padding + text_box_width, y + line_height], fill=code_bg_color)
            draw.text((padding + 5, y), text, font=mono_font, fill="black")
            y += line_height
        else:
            wrapped = textwrap.wrap(text, width=60)
            if not wrapped:
                 y += line_height
            for wline in wrapped:
                draw.text((padding, y), wline, font=font, fill="black")
                y += line_height
            
    output_path = os.path.join(tempfile.mkdtemp(), "markdown.png")
    img.save(output_path)
    return output_path

# ====== 显示结果 ======
def show_results(paths):
    st.success(f"转换完成！共 {len(paths)} 张图片。")
    for i, p in enumerate(paths):
        img = Image.open(p)
        st.image(img, caption=f"图片 {i + 1}", use_container_width=True)
    
    zip_file = zip_images(paths)
    st.download_button("📦 下载全部（ZIP）", data=zip_file, file_name="converted_images.zip", mime="application/zip")

# ====== 主程序 ======
def run_pdf_to_png_app():
    st.title("📄 PDF / Markdown 转 PNG 图片")
    st.markdown("支持上传 PDF / 输入 PDF 链接 / 输入 Markdown 内容，生成 PNG 图片。")

    tab1, tab2, tab3 = st.tabs(["📤 上传 PDF", "🌐 PDF 链接", "📝 Markdown 转图片"])

    # PDF 专用参数
    st.sidebar.header("PDF 转换参数")
    zoom = st.sidebar.slider("🔍 缩放比例", 1.0, 5.0, 2.0, step=0.5)
    rotation = st.sidebar.selectbox("🔄 旋转角度", [0, 90, 180, 270])
    
    # 合并页数
    pages_per_image = st.sidebar.number_input(
        "合并页数（几页PDF合并为一张图）", 
        min_value=1, 
        value=1, 
        step=1,
        help="选择 1 表示不合并，选择大于 1 的数字表示该数量的页数将**纵向**合并为一张长图。"
    )

    # 上传 PDF
    with tab1:
        uploaded_file = st.file_uploader("上传 PDF 文件", type=["pdf"])
        if uploaded_file:
            with st.spinner("正在转换为图片..."):
                paths, _ = pdf_to_images(
                    uploaded_file.read(), 
                    pages_per_image=pages_per_image,
                    zoom_x=zoom, 
                    zoom_y=zoom, 
                    rotation_angle=rotation
                )
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
                    paths, _ = pdf_to_images(
                        pdf_bytes.read(), 
                        pages_per_image=pages_per_image,
                        zoom_x=zoom, 
                        zoom_y=zoom, 
                        rotation_angle=rotation
                    )
                show_results(paths)
            except Exception as e:
                st.error(f"下载或转换失败: {e}")

    # Markdown 转图片
    with tab3:
        md_input = st.text_area(
            "请输入 Markdown 内容",
            "# 标题示例\n\n- 列表1\n- 列表2\n\n**加粗文本**\n\n```python\n# 代码块示例\nprint('Hello Streamlit')\n```",
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
#     run_pdf_to_png_app()