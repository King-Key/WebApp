import streamlit as st
# 导入你的其他功能模块
# from pdf2png import run_pdf_to_png_app 
# from CN_PNG import makde_in_china
# from video import make_video_from_audio_and_images

# 导入新的功能模块
from paper2vedio import run_paper_to_video_app 

st.set_page_config(page_title='AI 工具箱', layout='centered', page_icon='🧰')

# 侧边栏
st.sidebar.title("🧰 工具导航")
st.sidebar.markdown("选择你想使用的工具：")
page = st.sidebar.radio("功能页面", 
                        ["📰 论文转播客视频", # 新增功能
                         "📄 PDF 转图片", 
                         "🇨🇳 微信头像加国旗背景",
                         "🎬 音频 + 图片合成视频"])
st.sidebar.markdown("---")
st.sidebar.caption("Made with ❤️ by WangGuo")

# 页面跳转
if page == "📰 论文转播客视频": # 新增功能页面
    run_paper_to_video_app()
elif page == "📄 PDF 转图片":
    # run_pdf_to_png_app() # 替换为你的实际函数名
    st.info("功能占位：PDF 转图片") # 占位符
elif page == "🇨🇳 微信头像加国旗背景":
    # makde_in_china() # 替换为你的实际函数名
    st.info("功能占位：头像加国旗") # 占位符
elif page == "🎬 音频 + 图片合成视频":
    # make_video_from_audio_and_images() # 替换为你的实际函数名
    st.info("功能占位：合成视频") # 占位符