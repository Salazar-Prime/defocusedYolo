import streamlit as st

# import pandas as pd
import cv2
from utils import match_template_in_image, annotate_bounding_boxes_over_image
import numpy as np

##### CONSTANT USER PARAMETERS #####

##### SIDEBAR #####
st.sidebar.title("User Parameters")

# choice. Find template in image. Find and track template in video
detection_type = st.sidebar.selectbox(
    "Detection Type",
    ["Find template in an image", "Find and track template in a video"],
    index=0,
)

template_threshold = st.sidebar.slider(
    "Threshold for Template Matching", min_value=0.0, max_value=1.0, value=0.9
)

search_range = st.sidebar.number_input(
    "Search Range (pixels)", min_value=0, max_value=50, value=10
)

st.sidebar.title("Display Parameters")

add_particle_id = st.sidebar.checkbox("Display Particle ID")

##### MAIN PAGE #####

st.title("Match and find particles in a Video")
col1_1, col1_2 = st.columns([1, 1])
with col1_1:
    if detection_type == "Find template in an image":
        img = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])
    elif detection_type == "Find and track template in a video":
        video = st.file_uploader("Upload a video", type=["mp4", "avi"])

with col1_2:
    template = st.file_uploader("Upload a template", type=["jpg", "png", "jpeg"])

if img is not None and template is not None:
    # img and template in green channel only
    imgGreen = cv2.imdecode(np.frombuffer(img.read(), np.uint8), 1)
    imgGreen = imgGreen[:, :, 1]
    templateGreen = cv2.imdecode(np.frombuffer(template.read(), np.uint8), 1)
    templateGreen = templateGreen[:, :, 1]

    matchedParticles = match_template_in_image(
        imgGreen, templateGreen, template_threshold, detection_type="multiple"
    )

    # add visual break in the UI
    st.markdown("---")

    col2_1, col2_2 = st.columns([1, 1])
    with col2_1:
        st.write("Matched Particles")
        st.write(matchedParticles)
    with col2_2:
        st.write("Annotated Image")
        annotated_img = annotate_bounding_boxes_over_image(
            imgGreen, matchedParticles, add_particle_id
        )
        st.image(annotated_img, caption="Annotated Image", use_column_width=True)
