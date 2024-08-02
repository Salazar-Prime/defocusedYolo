import streamlit as st

import cv2
from utils import (
    match_template_in_image,
    annotate_bounding_boxes_over_image,
    match_particle_in_video,
    crop,
    mask,
)
import numpy as np
import tempfile
import pandas as pd
import json


from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas

##### CONSTANT USER PARAMETERS #####


##### SIDEBAR #####

st.sidebar.title('User Parameters')

stroke_width = st.sidebar.slider("Stroke width: ", 1, 25, 3)
stroke_color = st.sidebar.color_picker("Stroke color hex: ")
drawing_mode = st.sidebar.selectbox('Drawing tool:', ("rect", "transform"))

st.sidebar.title("Display Parameters")

add_particle_id = st.sidebar.checkbox("Display Particle ID")
clear_canvas = st.sidebar.button("Clear Canvas", key = "clear_canvas")

##### MAIN PAGE #####

st.title('Match and find particles in a Video')


video = st.file_uploader("Upload a video", type=["mp4", "avi"])


if video is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(video.read())
    cap = cv2.VideoCapture(tfile.name)
    #frame 0
    ret, frame0 = cap.read()
    # ? why need to change cap object to a gray-scale image (only shows intensity) and then change it back to RGB scale
    #frame0 = frame0[:, :, 1]
    #convert from np.array to Image object
    frame0_image = Image.fromarray(frame0, 'RGB')
    #frame0_image = Image.fromarray(cv2.cvtColor(frame0, cv2.COLOR_GRAY2RGB))


    #session_State initialization.
    if "drawn_obj" not in st.session_state:
        st.session_state["drawn_obj"] = {}
    if "check_left" not in st.session_state:
        st.session_state["check_left"] = False
    if "check_right" not in st.session_state:
        st.session_state["check_right"] = False
    if "check_up" not in st.session_state:
        st.session_state["check_up"] = False
    if "check_down" not in st.session_state:
        st.session_state["check_down"] = False
    if "check_clear" not in st.session_state:
        st.session_state["check_clear"] = False

    #display buttons.
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Left ", key = "left"):
            st.session_state["check_left"] = True
        if st.session_state["check_left"]:
            st.session_state["drawn_obj"]["left"] = st.session_state["drawn_obj"]["left"] - 10
    with col2:
        if st.button("Right", key = "right"):
            st.session_state["check_right"] = True
        if st.session_state["check_right"]:
            st.session_state["drawn_obj"]["left"] = st.session_state["drawn_obj"]["left"] + 10
    with col3:
        if st.button("Up   ", key = "up"):
            st.session_state["check_up"] = True
        if st.session_state["check_up"]:
            st.session_state["drawn_obj"]["top"] = st.session_state["drawn_obj"]["top"] - 10
    with col4:
        if st.button("Down ", key = "down"):
            st.session_state["check_down"] = True
        if st.session_state["check_down"]:
            st.session_state["drawn_obj"]["top"] = st.session_state["drawn_obj"]["top"] + 10


    #task2: clear_canvas
    if clear_canvas:
        st.session_state["drawn_obj"] = {}
        st.session_state["check_clear"] = True
        st.rerun()


    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_image= frame0_image,
        update_streamlit= True,
        height=frame0_image.height,  
        initial_drawing = {'version': '4.4.0', 'objects': [st.session_state["drawn_obj"]] }
        if st.session_state["drawn_obj"] != {} 
        else None,
        drawing_mode= drawing_mode,
        point_display_radius= 0,
        key="canvas",
    )


    if canvas_result.json_data is not None and (st.session_state["check_left"] == False and
                                        st.session_state["check_right"] == False and
                                        st.session_state["check_up"] == False and 
                                        st.session_state["check_down"] == False) and st.session_state["check_clear"] == False: 
        objects = pd.json_normalize(canvas_result.json_data["objects"])
        for col in objects.select_dtypes(include=['object']).columns:
            objects[col] = objects[col].astype("str")
        
        #final dataframe contains information of the location of the newly drawn bboxes
        myDF = pd.DataFrame(columns = ['x top left', 'y top left', 'width', 'height'])
        
        st.session_state["drawn_obj"] = canvas_result.json_data["objects"][0]


    #restate the buttons back to the original status.
    if st.session_state["check_left"]:
        st.session_state["check_left"] = False
    if st.session_state["check_right"]:
        st.session_state["check_right"] = False
    if st.session_state["check_up"]:
        st.session_state["check_up"] = False
    if st.session_state["check_down"]:
        st.session_state["check_down"] = False
    if st.session_state["check_clear"]:
        st.session_state["check_clear"] = False
     