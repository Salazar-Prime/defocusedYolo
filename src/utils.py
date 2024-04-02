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

    df = pd.DataFrame(results).astype("int")
    return df


def annotate_bounding_boxes_over_image(img, df, add_particle_id=False):
    # Convert image to 3-channel so that the boxes can be visualized easily
    img_color = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

    for index, row in df.iterrows():
        # np.random.seed(row['particle'])
        # color = tuple(np.random.choice(range(256), size=3))
        # color = (int(color[0]), int(color[1]), int(color[2]))
        # print(color)
        # print(row['x top left'], row['y top left'], row['x bottom right'], row['y bottom right'])
        cv2.rectangle(
            img_color,
            (row["x top left"], row["y top left"]),
            (row["x top left"] + row["width"], row["y top left"] + row["height"]),
            (0, 0, 255),
            2,
        )  # color
        if add_particle_id:
            # particle ID will be the index of the row
            cv2.putText(
                img_color,
                str(index),
                (row["x top left"], row["y top left"] - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2,
            )

    return img_color
