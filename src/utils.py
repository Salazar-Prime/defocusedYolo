import pandas as pd
import numpy as np
import cv2


def match_template_in_image(img, template, threshold, detection_type="multiple"):
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    w, h = template.shape[::-1]
    results = []

    if detection_type == "multiple":
        loc = np.where(res >= threshold)
        results = [
            {"x top left": pt[0], "y top left": pt[1], "width": w, "height": h}
            for i, pt in enumerate(zip(*loc[::-1]))
        ]

    elif detection_type == "single":
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        results.append(
            {
                "x top left": max_loc[0],
                "y top left": max_loc[1],
                "width": w,
                "height": h,
            }
        )

    return pd.DataFrame(results).astype("int")


def annotate_bounding_boxes_over_image(img, df, add_particle_id=False):
    # Convert image to 3-channel so that the boxes can be visualized easily
    img_color = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

    for index, row in df.iterrows():
        cv2.rectangle(
            img_color,
            (row["x top left"], row["y top left"]),
            (row["x top left"] + row["width"], row["y top left"] + row["height"]),
            (0, 0, 255),
            2,
        )  # color
        if add_particle_id:
            cv2.putText(
                img_color,
                str(row["particleID"]),
                (row["x top left"], row["y top left"] - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2,
            )

    return img_color


def crop(img, row, offset=0):
    return img[
        row["y top left"] - offset : row["y top left"] + row["height"] + offset,
        row["x top left"] - offset : row["x top left"] + row["width"] + offset,
    ]


def mask(img, row, offset=0):
    # create an inverted mask around the particle
    mask = np.zeros(img.shape, dtype=np.uint8)
    mask[
        row["y top left"] - offset : row["y top left"] + row["height"] + offset,
        row["x top left"] - offset : row["x top left"] + row["width"] + offset,
    ] = 1
    # mulitply the mask with the image
    return cv2.bitwise_and(img, img, mask=mask)


def match_particle_in_video(vidcap, threshold, df, search_range):
    # df already contains the detection from first frame
    dfReturn = df.copy()
    currentFrameID = 1
    success = True
    while True:
        success, currentFrame = vidcap.read()
        if not success:
            break
        print(f"Processing Frame {currentFrameID}")
        currentFrame = currentFrame[:, :, 1]  # green channel only
        # loop over all templates
        for index, row in df.iterrows():
            currentTemplate = crop(currentFrame, row, 0)
            subImg = crop(currentFrame, row, search_range)
            matchParticle = match_template_in_image(
                subImg, currentTemplate, threshold, detection_type="single"
            )
            matchParticle["particleID"] = row["particleID"]
            matchParticle["frame"] = currentFrameID
            # offset the x and y coordinates by row value and search range
            matchParticle["x top left"] = (
                matchParticle["x top left"] + row["x top left"] - search_range
            )
            matchParticle["y top left"] = (
                matchParticle["y top left"] + row["y top left"] - search_range
            )
            dfReturn = pd.concat([dfReturn, matchParticle])
        currentFrameID += 1
    return dfReturn
