import streamlit as st 
from pdf2png import pdf2png
from search_github_app import search_github
from search_arxiv_app import search_arxiv
from mp42gif import mp42gif
from CN_PNG import makde_in_china
from transprompt import transPrompt

st.set_page_config(page_title='Streamlit App')

app_pages = {
    'pdf2png': pdf2png,
    'GitHub': search_github,
    'Arxiv': search_arxiv,
    'video2gif': mp42gif,
    '微信头像添加国旗背景': makde_in_china,
    '提示词翻译'： transPrompt
}

st.sidebar.write("Web APP")
st.sidebar.write("---")
page = st.sidebar.radio('选择页面', tuple(app_pages.keys()))

# 执行选择的页面
app_pages[page]()
