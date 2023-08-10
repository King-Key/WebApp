import streamlit 
import os
from streamlit.components.v1 import html 
from moviepy.editor import VideoFileClip


def save_uploaded_file(uploadedfile):
  with open(os.path.join("./",uploadedfile.name),"wb") as f:
     f.write(uploadedfile.getbuffer())
  return streamlit.success("Saved file :{} ".format(uploadedfile.name))

def mp42gif():
    html("<center><h1> 视频 转 gif </center>")
    datafile = streamlit.file_uploader("Upload 视频文件",type=['mp4,mov'])
    if datafile is not None:
        file_details = {"FileName":datafile.name,"FileType":datafile.type}
        save_uploaded_file(datafile)
        videoClip=VideoFileClip(datafile.name).resize((488,225))
        videoClip.write_gif("output.gif",fps=15)
        streamlit.balloons()
        streamlit.image("output.gif")
