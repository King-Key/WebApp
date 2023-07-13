import streamlit as st
import requests

def search_github():
    st.title('GitHub 项目搜索')

    # 输入关键词
    keyword = st.text_input("输入关键词")
    count = st.number_input("输入数量", min_value=1, step=1)

    # 当用户点击“搜索”按钮时执行的函数
    if st.button('搜索'):
        # 使用GitHub API进行搜索
        url = f"https://api.github.com/search/repositories?q={keyword}&sort=stars&order=desc"
        response = requests.get(url).json()
        projects = response['items'][:count]

        for project in projects:
            st.subheader(project['name'])
            st.write(f"Star Count: {project['stargazers_count']}")
            st.write(f"Project Link: [{project['html_url']}]({project['html_url']})")
            st.write(f"Description: {project['description']}")
            st.write('---')