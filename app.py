import streamlit as st
from pdf2png import run_pdf_to_png_app
from CN_PNG import makde_in_china

st.set_page_config(page_title='AI 工具箱', layout='centered', page_icon='🧰')

# 侧边栏
st.sidebar.title("🧰 工具导航")
st.sidebar.markdown("选择你想使用的工具：")
page = st.sidebar.radio("功能页面", ["📄 PDF 转图片", "🇨🇳 微信头像加国旗背景"])
st.sidebar.markdown("---")
st.sidebar.caption("Made with ❤️ by QingKeLab")

# 页面跳转
if page == "📄 PDF 转图片":
    run_pdf_to_png_app()
else:
    makde_in_china()