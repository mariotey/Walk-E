import mediapipe as mp
mp_pose = mp.solutions.pose

def request_lm(world_lm, time):
    new_data = {
        "ref_heel": [],
        "shoulder": [],
        "hip": [],
        "knee": [],
        "ankle": [],
        "toe": [],
        "time": []
    }

    ref_time = time[0]
    
    for idx, images in enumerate(world_lm):
        new_data["ref_heel"].append(images[mp_pose.PoseLandmark["LEFT_HEEL"].value])
        new_data["shoulder"].append(images[mp_pose.PoseLandmark["LEFT_SHOULDER"].value])
        new_data["hip"].append(images[mp_pose.PoseLandmark["LEFT_HIP"].value])
        new_data["knee"].append(images[mp_pose.PoseLandmark["LEFT_KNEE"].value])
        new_data["ankle"].append(images[mp_pose.PoseLandmark["LEFT_ANKLE"].value])
        new_data["toe"].append(images[mp_pose.PoseLandmark["LEFT_FOOT_INDEX"].value])
        new_data["time"].append(time[idx] - ref_time)
    
    return new_data