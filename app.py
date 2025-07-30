import streamlit as st 
from pdf2png import run_pdf_to_png_app
from CN_PNG import made_in_china

st.set_page_config(page_title='Streamlit App')

app_pages = {
    'PDF转图片': run_pdf_to_png_app,
    '微信头像添加国旗背景': made_in_china
}

st.sidebar.title("Web APP")
st.sidebar.markdown("---")
page = st.sidebar.radio('选择页面', list(app_pages.keys()))
app_pages[page]()
