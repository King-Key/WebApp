import streamlit as st
import requests
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import re

def search_arxiv():
    st.title('Arxiv 最新论文')

    def translate_english_to_chinese(text):
        model_name = "Helsinki-NLP/opus-mt-en-zh"  # 英文到中文的翻译模型
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        max_length = 4000  # 每个拆分的最大长度，根据模型的最大输入长度进行调整
        split_texts = [text[i:i+max_length] for i in range(0, len(text), max_length)]

        translated_texts = []
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)

        for split_text in split_texts:
            inputs = tokenizer.encode(split_text, return_tensors="pt", padding=True, truncation=True).to(device)
            outputs = model.generate(inputs)
            translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            translated_texts.append(translated_text)

        return ''.join(translated_texts)


    # 输入关键词
    keywords = st.text_input('输入关键词（用逗号分隔）')
    quantity = st.number_input('请输入要搜索的项目数量', min_value=1, step=1)


    if st.button('搜索'):
        st.write('正在搜索 Arxiv...')
        keyword_list = keywords.split(',')

        for keyword in keyword_list:
            st.subheader(f'关键词: {keyword}')
            url = f"https://arxiv.org/search/?query={keyword}&searchtype=all&abstracts=show&order=-announced_date_first&size=50"
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            paper_list = soup.find_all('li', class_='arxiv-result')

            if len(paper_list) == 0:
                st.write('没有找到匹配的论文。')
            else:
                for i, paper in enumerate(paper_list):
                    title = paper.find('p', class_='title is-5 mathjax').text.strip()
                    authors = paper.find('p', class_='authors').text.strip()
                    abstract = paper.find('span', class_='abstract-full').text.strip()
                    published_date = paper.find("p", class_="is-size-7").text.strip()
                    paper_link = paper.find('p',class_='list-title is-inline-block').text
                    paper_link = re.search(r'\d+(\.\d+)?',paper_link).group()
                    print(type(paper_link))

                    if i < quantity:
                        st.write(f'### {i+1}. {title}')
                        st.write(f'{"".join(authors.split())}')
                        st.write(f'提交时间: {published_date}')
                        st.write(f'link: https://arxiv.org/pdf/{paper_link}')
                        st.write(f'摘要: {abstract}')
                        abstract=translate_english_to_chinese(abstract)
                        st.write(f'中文翻译: {abstract}')
                            
                            
                        st.write('---')