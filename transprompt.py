import streamlit as st
from transformers import MarianMTModel, MarianTokenizer

def transPrompt():
    def translate_text(text, model, tokenizer, target_language='en'):
        # 使用模型和标记器进行翻译
        inputs = tokenizer(text, return_tensors="pt", truncation=True)
        outputs = model.generate(**inputs, target_language=target_language)
        translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return translated_text

    # 选择翻译模型和标记器（这里以Marian MT为例）
    model_name = "Helsinki-NLP/opus-mt-zh-en"
    model = MarianMTModel.from_pretrained(model_name)
    tokenizer = MarianTokenizer.from_pretrained(model_name)

    # Streamlit界面
    st.title("中英文翻译器")

    # 输入框
    user_input = st.text_input("请输入中文文本，用逗号隔开:")

    if user_input:
        # 选择目标语言
        target_language = st.selectbox("选择目标语言:", ["英语", "Spanish", "French"])

        # 将目标语言转换成标准格式
        language_mapping = {"英语": "en", "Spanish": "es", "French": "fr"}
        target_language_code = language_mapping.get(target_language, "en")

        # 以逗号分隔中文文本
        chinese_texts = user_input.split(',')

        # 翻译每个中文文本
        translated_texts = [translate_text(text.strip(), model, tokenizer, target_language=target_language_code) for text in chinese_texts]

        # 将翻译结果以逗号分隔显示
        translated_result = ', '.join(translated_texts)

        # 显示翻译结果
        st.write(f"翻译结果 ({target_language}): {translated_result}")