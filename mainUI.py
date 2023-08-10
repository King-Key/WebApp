import streamlit as st 
from pdf2png import pdf2png
from search_github_app import search_github
from search_arxiv_app import search_arxiv
from mp42gif import mp42gif

st.set_page_config(page_title='Streamlit App')

app_pages = {
    'pdf2png': pdf2png,
    'GitHub': search_github,
    'Arxiv': search_arxiv,
    'video2gif': mp42gif
}

st.sidebar.write("Web APP")
st.sidebar.write("---")
page = st.sidebar.radio('选择页面', tuple(app_pages.keys()))

# 执行选择的页面
app_pages[page]()
