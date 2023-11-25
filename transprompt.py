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
    user_input = st.text_input("请输入中文文本:")

    if user_input:
        # 选择目标语言
        target_language = st.selectbox("选择目标语言:", ["英语", "Spanish", "French"])

        # 将目标语言转换成标准格式
        language_mapping = {"英语": "en", "Spanish": "es", "French": "fr"}
        target_language_code = language_mapping.get(target_language, "en")

        # 翻译文本
        translated_text = translate_text(user_input, model, tokenizer, target_language=target_language_code)

        # 显示翻译结果
        st.write(f"翻译结果 ({target_language}): {translated_text}")