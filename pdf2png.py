import streamlit as st
import os 
import fitz
from PIL import Image
import time
from stqdm import stqdm
from streamlit.components.v1 import html 

def save_uploaded_file(uploadedfile):
  with open(os.path.join("./",uploadedfile.name),"wb") as f:
     f.write(uploadedfile.getbuffer())
  return st.success("Saved file :{} ".format(uploadedfile.name))

def pdf2png():
    html("<center><h1> pdf 转 png </center>")
    output="./"
    datafile = st.file_uploader("Upload pdf",type=['pdf'])

    if datafile is not None:
        file_details = {"FileName":datafile.name,"FileType":datafile.type}
        # df  = pd.read_csv(datafile)
        # st.dataframe(df)
        # Apply Function here
        save_uploaded_file(datafile)

        print(datafile)


        doc=fitz.open("./"+datafile.name)
        pages=doc.page_count
        st.write("文件页数：",pages)


        for page in stqdm(range(pages)):
            page1=doc.load_page(page)
            png=page1.get_pixmap(alpha=True)
        
        if os.path.exists(output) == False:
            os.mkdir(output)
            

        png.save( output +"{}.png".format(page))
        
        st.write("转换完成！！！")
        st.balloons()

        for i in range(fitz.open("./"+datafile.name).page_count):
            image=os.path.join(output+"{}.png".format(i))

        # image
        st.image(Image.open(image))
