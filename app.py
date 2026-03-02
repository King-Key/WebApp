import streamlit as st

from CN_PNG import made_in_china
from article_to_xhs import run_article_to_xhs_app
from pdf2png import run_pdf_to_png_app


st.set_page_config(page_title='AI 工具箱', layout='centered', page_icon='🧰')

# 侧边栏
st.sidebar.title("🧰 工具导航")
st.sidebar.markdown("选择你想使用的工具：")
pages = {
    "📄 PDF 转图片": run_pdf_to_png_app,
    "🇨🇳 微信头像加国旗背景": made_in_china,
    "📝 链接转小红书图片": run_article_to_xhs_app,
}
page = st.sidebar.radio("功能页面", list(pages.keys()))
st.sidebar.markdown("---")
st.sidebar.caption("Made with ❤️ by WangGuo")

# 页面跳转
pages[page]()
