from PIL import Image
import pytesseract

# 打开图片文件
image = Image.open("./1.png")

# 使用 pytesseract 进行 OCR
text = pytesseract.image_to_string(image)

# 输出识别的文字
print(text)
