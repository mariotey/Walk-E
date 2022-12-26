def data_coord():
    pose_data = {
        "nose": [],
        "left_eye_inner": [],
        "left_eye": [],
        "left_eye_outer": [],
        "right_eye_inner": [],
        "right_eye": [],
        "right_eye_outer": [],
        "left_ear": [],
        "right_ear": [],
        "mouth_left": [],
        "mouth_right": [],
        "left_shoulder": [],
        "right_shoulder":[],
        "left_elbow":[],
        "right_elbow": [],
        "left_wrist": [],
        "right_wrist": [],
        "left_pinky": [],
        "right_pinky": [],
        "left_index": [],
        "right_index": [],
        "left_thumb": [],
        "right_thumb": [],
        "left_hip": [],
        "right_hip": [],
        "left_knee": [],
        "right_knee": [],
        "left_ankle": [],
        "right_ankle": [],
        "left_heel": [],
        "right_heel": [],
        "left_foot_index": [],
        "right_foot_index": []
    }

    return pose_data

def append_lm(world_lm):
    def format_lm(world_landmarks):
        data_json = {
            "x": world_landmarks.x,
            "y": world_landmarks.y,
            "z": world_landmarks.z
        }

        return data_json
    
    jsondata = {
        "nose": format_lm(world_lm[0]),
        "left_eye_inner": format_lm(world_lm[1]),
        "left_eye": format_lm(world_lm[2]),
        "left_eye_outer": format_lm(world_lm[3]),
        "right_eye_inner": format_lm(world_lm[4]),
        "right_eye": format_lm(world_lm[5]),
        "right_eye_outer": format_lm(world_lm[6]),
        "left_ear": format_lm(world_lm[7]),
        "right_ear": format_lm(world_lm[8]),
        "mouth_left": format_lm(world_lm[9]),
        "mouth_right": format_lm(world_lm[10]),
        "left_shoulder": format_lm(world_lm[11]),
        "right_shoulder": format_lm(world_lm[12]),
        "left_elbow": format_lm(world_lm[13]),
        "right_elbow": format_lm(world_lm[14]),
        "left_wrist": format_lm(world_lm[15]),
        "right_wrist": format_lm(world_lm[16]),
        "left_pinky": format_lm(world_lm[17]),
        "right_pinky": format_lm(world_lm[18]),
        "left_index": format_lm(world_lm[19]),
        "right_index": format_lm(world_lm[20]),
        "left_thumb": format_lm(world_lm[21]),
        "right_thumb": format_lm(world_lm[22]),
        "left_hip": format_lm(world_lm[23]),
        "right_hip": format_lm(world_lm[24]),
        "left_knee": format_lm(world_lm[25]),
        "right_knee": format_lm(world_lm[26]),
        "left_ankle": format_lm(world_lm[27]),
        "right_ankle": format_lm(world_lm[28]),
        "left_heel": format_lm(world_lm[29]),
        "right_heel": format_lm(world_lm[30]),
        "left_foot_index": format_lm(world_lm[31]),
        "right_foot_index": format_lm(world_lm[32])
    }

    return jsondata
