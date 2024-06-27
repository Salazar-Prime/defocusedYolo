import streamlit as st


# import pandas as pd
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


from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas


##### CONSTANT USER PARAMETERS #####


##### SIDEBAR #####
st.sidebar.title("User Parameters")


# choice. Find template in image. Find and track template in video
detection_type = st.sidebar.selectbox(
    "Detection Type",
    ["Find template in an image", "Find and track template in a video",
     "Annotate the first frame of a video"],
    index=0,
)  


if detection_type !=  "Annotate the first frame of a video":
    template_threshold = st.sidebar.slider(
        "Threshold for Template Matching", min_value=0.0, max_value=1.0, value=0.9
    )


    search_range = st.sidebar.number_input(
        "Search Range (pixels)", min_value=0, max_value=50, value=10
    )
else:
    stroke_width = st.sidebar.slider("Stroke width: ", 1, 25, 3)
    stroke_color = st.sidebar.color_picker("Stroke color hex: ")    


st.sidebar.title("Display Parameters")


add_particle_id = st.sidebar.checkbox("Display Particle ID")


##### MAIN PAGE #####


st.title("Match and find particles in a Video")
col1_1, col1_2 = st.columns([1, 1])
with col1_1:
    if detection_type == "Find template in an image":
        img = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])
    elif (detection_type == "Find and track template in a video") or (detection_type == "Annotate the first frame of a video"):
        video = st.file_uploader("Upload a video", type=["mp4", "avi"])


with col1_2:
    if detection_type != "Annotate the first frame of a video":
        template = st.file_uploader("Upload a template", type=["jpg", "png", "jpeg" ])
   


# template matching in image
if (
    detection_type == "Find template in an image"
    and img is not None
    and template is not None
):
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


# # template matching in video
# if (
#     detection_type == "Find and track template in a video"
#     and video is not None
#     and template is not None
# ):
#     # get first frame from video
#     tfile = tempfile.NamedTemporaryFile(delete=False)
#     tfile.write(video.read())


#     # video and template in green channel only
#     cap = cv2.VideoCapture(tfile.name)
#     templateGreen = cv2.imdecode(np.frombuffer(template.read(), np.uint8), 1)
#     templateGreen = templateGreen[:, :, 1]


#     # add visual break in the UI
#     st.markdown("---")


#     # get annotation for the first frame
#     ret, frame = cap.read()
#     frameGreen = frame[:, :, 1]
#     matchedParticles_F0 = match_template_in_image(
#         frameGreen, templateGreen, template_threshold, detection_type="multiple"
#     )
#     # add particleID and frame number
#     matchedParticles_F0["particleID"] = matchedParticles_F0.index
#     matchedParticles_F0["frame"] = 0


#     st.write(f"Found {len(matchedParticles_F0)} Particles in Frame 0")


#     dfVideo = match_particle_in_video(
#         cap, template_threshold, matchedParticles_F0, search_range
#     )




if (
    detection_type == "Find and track template in a video"
    and video is not None
    and template is not None
):
    template = cv2.imdecode(np.frombuffer(template.read(), np.uint8), 1)
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(video.read())
    cap = cv2.VideoCapture(tfile.name) #cap stands for "video CAPture object"
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))


    # create a slider with number of frames
    frameSlider = st.slider(
        "Select Frame Number", min_value=0, max_value=frame_count, value=0
    )
    # frame 0
    ret, frame0 = cap.read()
    frame0 = frame0[:, :, 1]
    matchedParticles_F0 = match_template_in_image(
        frame0,
        template[:, :, 1],
        template_threshold,
        detection_type="multiple",
    )
    matchedParticles_F0["particleID"] = matchedParticles_F0.index
    matchedParticles_F0["frame"] = 0
    # get the frame from slider
    cap.set(cv2.CAP_PROP_POS_FRAMES, frameSlider)
    ret, currentFrame = cap.read()
    if ret:  # frame exists
        dfFrame = pd.DataFrame()
        for index, row in matchedParticles_F0.iterrows():
            currentTemplate = crop(frame0, row, 0)
            subImg = mask(currentFrame[:, :, 1], row, search_range)
            matchParticle = match_template_in_image(
                subImg, currentTemplate, template_threshold, detection_type="single"
            )
            matchParticle["particleID"] = row["particleID"]
            matchParticle["frame"] = frameSlider
            dfFrame = pd.concat([dfFrame, matchParticle])
        # annotate the image
        annotated_img = annotate_bounding_boxes_over_image(
            currentFrame[:, :, 1], dfFrame, add_particle_id
        )
        st.image(
            annotated_img,
            caption=f"Annotated Frame {frameSlider}",
            use_column_width=True,
        )
   
if (
    detection_type == "Annotate the first frame of a video"
    and video is not None
):  
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(video.read())
    cap = cv2.VideoCapture(tfile.name)
    #frame 0
    ret, frame0 = cap.read()
    frame0 = frame0[:, :, 1]
    #convert from np.array to Image object
    frame0_image = Image.fromarray(cv2.cvtColor(frame0, cv2.COLOR_GRAY2RGB))


    canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_image= frame0_image,
    update_streamlit= True,
    height=frame0_image.height,  
    drawing_mode= 'rect',
    point_display_radius= 0,
    key="canvas",
    )


    if canvas_result.image_data is not None:
            st.image(canvas_result.image_data)
    if canvas_result.json_data is not None:
        objects = pd.json_normalize(canvas_result.json_data["objects"])
        for col in objects.select_dtypes(include=['object']).columns:
            objects[col] = objects[col].astype("str")

        #final dataframe contains information of the location of the newly drawn bboxes
        if len(objects) != 0:
            myDF = pd.DataFrame(columns = ['x top left', 'y top left', 'width', 'height'])
            myDF['x top left'] = objects['left']
            myDF['y top left'] = objects['top']
            myDF['width'] = objects['width']
            myDF['height'] = objects['height']
            st.dataframe(myDF)


        #show the dataframe on Streamlit  
        def convert_df(df):
            return df.to_csv().encode("utf-8")
        
        if len(objects) != 0:
            csv = convert_df(myDF)

            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name="templates.csv",
                mime="text/csv",
            )  
