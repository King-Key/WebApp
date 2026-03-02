import os
import re
import tempfile
import textwrap
import zipfile
from typing import Iterable
from io import BytesIO
from urllib.parse import urlparse

import requests
import streamlit as st
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont


CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1440
PADDING_X = 96
PADDING_TOP = 180
PADDING_BOTTOM = 120


def _load_font(size: int, bold: bool = False):
    regular_candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    bold_candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    candidates = bold_candidates if bold else regular_candidates
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:
                continue
    return ImageFont.load_default()


def _wrap_text(line: str, width: int):
    if not line:
        return [""]
    return textwrap.wrap(line, width=width, break_long_words=True, replace_whitespace=False)


def _safe_filename(name: str):
    return re.sub(r'[\\/:*?"<>|]+', "_", name).strip("_") or "article"


def fetch_article(url: str, timeout: int = 20):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or resp.encoding
    soup = BeautifulSoup(resp.text, "html.parser")

    title = ""
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        title = og_title["content"].strip()
    if not title and soup.title:
        title = soup.title.get_text(strip=True)
    if not title:
        title = "未命名文章"

    selectors = ["article p", "main p", ".post p", ".entry-content p", ".article p"]
    paragraph_nodes = []
    for selector in selectors:
        paragraph_nodes = soup.select(selector)
        if len(paragraph_nodes) >= 3:
            break
    if len(paragraph_nodes) < 3:
        paragraph_nodes = soup.find_all("p")

    paragraphs = []
    for node in paragraph_nodes:
        text = re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip()
        if len(text) >= 20:
            paragraphs.append(text)

    # 去重并保持顺序
    seen = set()
    unique_paragraphs = []
    for p in paragraphs[:300]:
        if p not in seen:
            seen.add(p)
            unique_paragraphs.append(p)

    if not unique_paragraphs:
        desc = soup.find("meta", attrs={"name": "description"})
        if desc and desc.get("content"):
            unique_paragraphs = [desc["content"].strip()]

    return title, unique_paragraphs


def paginate_paragraphs(
    paragraphs: Iterable[str], line_width: int = 22, max_lines_per_page: int = 20
):
    pages = []
    current_lines = []
    for paragraph in paragraphs:
        lines = _wrap_text(paragraph, width=line_width)
        needed = len(lines) + 1  # 加一行间距
        if current_lines and len(current_lines) + needed > max_lines_per_page:
            pages.append("\n".join(current_lines))
            current_lines = []
        current_lines.extend(lines)
        current_lines.append("")

    if current_lines:
        pages.append("\n".join(current_lines).strip())
    return pages


def _draw_cover(title: str, domain: str, out_path: str):
    img = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), color=(250, 244, 235))
    draw = ImageDraw.Draw(img)

    # 轻量背景层次
    draw.ellipse((-220, -180, 620, 660), fill=(255, 220, 175))
    draw.ellipse((580, 820, 1320, 1700), fill=(255, 207, 140))
    draw.rectangle((0, 0, CANVAS_WIDTH, 130), fill=(227, 76, 60))

    title_font = _load_font(72, bold=True)
    sub_font = _load_font(36)
    label_font = _load_font(34)

    card_left = 70
    card_top = 260
    card_right = CANVAS_WIDTH - 70
    card_bottom = CANVAS_HEIGHT - 180
    draw.rounded_rectangle(
        (card_left, card_top, card_right, card_bottom),
        radius=34,
        fill=(255, 255, 255),
    )

    draw.text((100, 70), "小红书图文稿", font=label_font, fill=(255, 255, 255))
    wrapped_title = _wrap_text(title, width=14)
    y = 360
    for line in wrapped_title[:8]:
        draw.text((110, y), line, font=title_font, fill=(42, 39, 34))
        y += 88

    draw.text((110, CANVAS_HEIGHT - 250), f"来源：{domain}", font=sub_font, fill=(105, 99, 92))
    draw.text((110, CANVAS_HEIGHT - 200), "保存图片即可发布", font=sub_font, fill=(227, 76, 60))
    img.save(out_path)


def _draw_content_page(title: str, content: str, page_no: int, total_pages: int, out_path: str):
    img = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), color=(248, 248, 246))
    draw = ImageDraw.Draw(img)

    title_font = _load_font(42, bold=True)
    body_font = _load_font(40)
    foot_font = _load_font(30)

    draw.rectangle((0, 0, CANVAS_WIDTH, 130), fill=(255, 255, 255))
    draw.line((70, 130, CANVAS_WIDTH - 70, 130), fill=(222, 222, 220), width=2)
    draw.text((70, 46), "笔记正文", font=title_font, fill=(54, 54, 52))
    draw.text((CANVAS_WIDTH - 260, 52), f"{page_no}/{total_pages}", font=foot_font, fill=(130, 130, 128))

    title_lines = _wrap_text(title, width=20)[:2]
    y = PADDING_TOP
    for line in title_lines:
        draw.text((PADDING_X, y), line, font=title_font, fill=(30, 30, 28))
        y += 56
    y += 24

    body_lines = content.split("\n")
    line_h = 56
    for line in body_lines:
        draw.text((PADDING_X, y), line, font=body_font, fill=(65, 65, 62))
        y += line_h
        if y > CANVAS_HEIGHT - PADDING_BOTTOM:
            break

    draw.text((PADDING_X, CANVAS_HEIGHT - 70), "由 AI 工具箱自动生成", font=foot_font, fill=(150, 150, 148))
    img.save(out_path)


def build_xhs_images(title: str, paragraphs: Iterable[str], domain: str, max_pages: int = 8):
    temp_dir = tempfile.mkdtemp()

    pages = paginate_paragraphs(paragraphs, line_width=22, max_lines_per_page=18)
    if not pages:
        pages = ["未提取到正文，请更换链接或手动整理内容。"]

    pages = pages[:max_pages]
    image_paths = []

    cover_path = os.path.join(temp_dir, "01_cover.png")
    _draw_cover(title=title, domain=domain or "未知来源", out_path=cover_path)
    image_paths.append(cover_path)

    total = len(pages)
    for idx, page_text in enumerate(pages, start=1):
        page_path = os.path.join(temp_dir, f"{idx + 1:02d}_content.png")
        _draw_content_page(title=title, content=page_text, page_no=idx, total_pages=total, out_path=page_path)
        image_paths.append(page_path)
    return image_paths, temp_dir


def zip_images(image_paths):
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for path in image_paths:
            zipf.write(path, arcname=os.path.basename(path))
    buffer.seek(0)
    return buffer


def run_article_to_xhs_app():
    st.title("📝 文章链接转小红书图片")
    st.markdown("输入文章链接，自动提取正文并生成适合发布的小红书图片。")

    article_url = st.text_input("文章链接", placeholder="https://example.com/article")
    max_pages = st.slider("最多正文图片页数", min_value=2, max_value=12, value=6, step=1)

    if st.button("生成小红书图片", key="article_to_xhs"):
        if not article_url.strip():
            st.warning("请输入文章链接。")
            return
        if not article_url.startswith(("http://", "https://")):
            st.warning("链接格式不正确，请以 http:// 或 https:// 开头。")
            return

        try:
            with st.spinner("正在抓取文章内容..."):
                title, paragraphs = fetch_article(article_url)
            if not paragraphs:
                st.error("未提取到可用正文，请尝试更换链接。")
                return

            parsed = urlparse(article_url)
            domain = parsed.netloc or "未知来源"
            with st.spinner("正在生成图片..."):
                image_paths, _ = build_xhs_images(
                    title=title,
                    paragraphs=paragraphs,
                    domain=domain,
                    max_pages=max_pages,
                )

            st.success(f"已生成 {len(image_paths)} 张图片。")
            st.caption(f"文章标题：{title}")
            st.caption(f"来源站点：{domain}")

            for i, path in enumerate(image_paths, start=1):
                st.image(path, caption=f"第 {i} 张", use_container_width=True)

            archive_name = f"{_safe_filename(title)[:30]}_xhs_images.zip"
            st.download_button(
                "📦 下载全部图片（ZIP）",
                data=zip_images(image_paths),
                file_name=archive_name,
                mime="application/zip",
            )
        except Exception as e:
            st.error(f"生成失败：{e}")
