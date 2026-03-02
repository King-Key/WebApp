# Streamlit 多功能工具集

## 功能介绍

本项目包含三个 Streamlit 页面：

1. **PDF 转 PNG 图片**
   - 上传 PDF 文件并逐页转换为图片
   - 支持清晰度和旋转角度调节
   - 支持在线预览和打包下载所有图片

2. **微信头像添加国旗背景**
   - 上传 PNG/JPG 头像
   - 添加中国国旗五角星渐变背景
   - 支持调整渐变强度和下载新头像

3. **文章链接转小红书图片**
   - 输入文章 URL 自动抓取标题和正文
   - 自动分页生成小红书风格封面图 + 正文图
   - 支持在线预览和 ZIP 打包下载

## 项目结构

```
.
├── app.py                # 主入口
├── pdf2png.py            # PDF 转图模块
├── CN_PNG.py             # 国旗头像模块
├── article_to_xhs.py     # 文章链接转小红书图片模块
├── assets/
│   └── china.png         # 中国国旗图片
├── requirements.txt
└── README.md
```

## 使用方法

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 启动应用：

```bash
streamlit run app.py
```

## 预览截图

> 请在网页中上传图片后体验。

---



## 📦 在线部署（Streamlit Community Cloud）

你可以通过以下方式将项目部署到 [Streamlit Cloud](https://streamlit.io/cloud)：

1. 将本项目上传到 GitHub 仓库
2. 打开：https://streamlit.io/cloud
3. 点击 “New app”，选择你上传的仓库
4. 设置：
   - **Main file path**: `app.py`
   - **Python version**: `3.10` 或自动识别
   - **Packages**: 自动读取 `requirements.txt`
5. 点击部署即可在线访问！
