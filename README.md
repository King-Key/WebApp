# Streamlit 多功能工具集

## 功能介绍

本项目包含两个 Streamlit 页面：

1. **PDF 转 PNG 图片**
   - 上传 PDF 文件并逐页转换为图片
   - 支持清晰度和旋转角度调节
   - 支持在线预览和打包下载所有图片

2. **微信头像添加国旗背景**
   - 上传 PNG/JPG 头像
   - 添加中国国旗五角星渐变背景
   - 支持调整渐变强度和下载新头像

## 项目结构

```
.
├── app.py                # 主入口
├── pdf2png.py            # PDF 转图模块
├── CN_PNG.py             # 国旗头像模块
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

