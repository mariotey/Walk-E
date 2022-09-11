import numpy as np
import cv2
import mediapipe as mp
import vectorMath

FONT_STYLE = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.5
LINE_THICK = 1
LINE_TYPE = cv2.LINE_AA

MIN_CHUNKSIZE = 3
MIN_STRIDETIME = 3
POINTS_SPACE = 20

WEBCAM_RES = [640,480]

mp_pose = mp.solutions.pose # Pose Estimation Model

shoulder_right = mp_pose.PoseLandmark.RIGHT_SHOULDER.value
shoulder_left = mp_pose.PoseLandmark.LEFT_SHOULDER.value
elbow_right = mp_pose.PoseLandmark.RIGHT_ELBOW.value
elbow_left = mp_pose.PoseLandmark.LEFT_ELBOW.value
wrist_right = mp_pose.PoseLandmark.RIGHT_WRIST.value
wrist_left = mp_pose.PoseLandmark.LEFT_WRIST.value
hip_right = mp_pose.PoseLandmark.RIGHT_HIP.value
hip_left = mp_pose.PoseLandmark.LEFT_HIP.value
knee_right= mp_pose.PoseLandmark.RIGHT_KNEE.value
knee_left = mp_pose.PoseLandmark.LEFT_KNEE.value
ankle_right = mp_pose.PoseLandmark.RIGHT_ANKLE.value
ankle_left = mp_pose.PoseLandmark.LEFT_ANKLE.value
heel_right = mp_pose.PoseLandmark.RIGHT_HEEL.value
heel_left = mp_pose.PoseLandmark.LEFT_HEEL.value

def modify_raw(raw_list, time_list, unit_space):
    new_data = []
    new_time = []
  
    for i in range(0, len(raw_list)-1):        
        new_data_add = np.linspace(raw_list[i], 
                                raw_list[i+1], 
                                num=unit_space)
        new_time_add = np.linspace(time_list[i],
                                time_list[i+1],
                                num=unit_space)
        for x in range(0, len(new_data_add) - 1):
            new_data.append(new_data_add[x])
            new_time.append(new_time_add[x])
        
    new_data.append(raw_list[-1])
    new_time.append(time_list[-1])
            
    return new_data, new_time

def get_heel_data(image, camera_landmarks, world_landmarks):
    heel_camera_left = [camera_landmarks[heel_left].x, camera_landmarks[heel_left].y]
    
    heel_world_right = [world_landmarks[heel_right].x, world_landmarks[heel_right].y, world_landmarks[heel_right].z]
    heel_world_left = [world_landmarks[heel_left].x, world_landmarks[heel_left].y, world_landmarks[heel_left].z]

    # print("Heel L:", heel_world_left, "\n")

    cv2.putText(image, str(round(world_landmarks[heel_left].y,2)),
            tuple(vectorMath.np.multiply(heel_camera_left, WEBCAM_RES).astype(int)), 
            FONT_STYLE, FONT_SCALE, (0, 0, 255), LINE_THICK, LINE_TYPE)

    return world_landmarks[heel_left].x, world_landmarks[heel_left].y, world_landmarks[heel_left].z

def get_gaitcycle_data(heel_baseline, raw_heel, raw_time):    
    modified_gait = []
    modified_time = []
    separate_index = []

    format_data, format_time = modify_raw(raw_heel, raw_time, POINTS_SPACE)

    for elem in format_data:
       if round(elem,2) == round(heel_baseline,2):
        separate_index.append(format_data.index(elem))
    
    for x in range(0, len(separate_index) - 1):
        modified_gait.append(format_data[separate_index[x]:separate_index[x+1]])
        modified_time.append(format_time[separate_index[x]:separate_index[x+1]])
    
    modified_gait.append(format_data[separate_index[-1]::])
    modified_time.append(format_time[separate_index[-1]::])

    valid_gait = []
    valid_time = []

    for i in range(len(modified_gait)):
        if len(modified_gait[i]) > MIN_CHUNKSIZE:
            if i != len(modified_gait) -1:
                modified_gait[i].append(heel_baseline)
                modified_time[i].append(modified_time[i][-1])
            valid_gait.append(modified_gait[i])
            valid_time.append(modified_time[i])

    new_gait = []
    new_time = []

    print(len(valid_gait))

    for x in range(len(valid_gait)):
        if max(valid_gait[x]) > heel_baseline:            
            try:
                if (valid_time[x+1][-1] - valid_time[x][0]) < MIN_STRIDETIME: 
                    new_gait.append(valid_gait[x] + valid_gait[x+1])
                    new_time.append(valid_time[x] + valid_time[x+1])
            except:
                new_gait.append(valid_gait[x])
                new_time.append(valid_time[x])
            print(x)

    return new_gait, new_time

def hipFlex(world_landmarks):      
    shoulder_world_right = [world_landmarks[shoulder_right].x, world_landmarks[shoulder_right].y, world_landmarks[shoulder_right].z]
    shoulder_world_left = [world_landmarks[shoulder_left].x, world_landmarks[shoulder_left].y, world_landmarks[shoulder_left].z]
    hip_world_right = [world_landmarks[hip_right].x, world_landmarks[hip_right].y, world_landmarks[hip_right].z]
    hip_world_left = [world_landmarks[hip_left].x, world_landmarks[hip_left].y, world_landmarks[hip_left].z]
    knee_world_right = [world_landmarks[knee_right].x, world_landmarks[knee_right].y, world_landmarks[knee_right].z]
    knee_world_left = [world_landmarks[knee_left].x, world_landmarks[knee_left].y, world_landmarks[knee_left].z]

    hip_flex_right = 180 - vectorMath.cal_threeD_angle(shoulder_world_right, hip_world_right, knee_world_right)
    hip_flex_left = 180 - vectorMath.cal_threeD_angle(shoulder_world_left, hip_world_left, knee_world_left)
    
    print("Hip R:", hip_flex_right, " ", "Hip L:", hip_flex_left, "\n")

    return hip_flex_right, hip_flex_left

def kneeFlex(world_landmarks):
    hip_world_right = [world_landmarks[hip_right].x, world_landmarks[hip_right].y, world_landmarks[hip_right].z]
    hip_world_left = [world_landmarks[hip_left].x, world_landmarks[hip_left].y, world_landmarks[hip_left].z]
    knee_world_right = [world_landmarks[knee_right].x, world_landmarks[knee_right].y, world_landmarks[knee_right].z]
    knee_world_left = [world_landmarks[knee_left].x, world_landmarks[knee_left].y, world_landmarks[knee_left].z]
    ankle_world_right = [world_landmarks[ankle_right].x, world_landmarks[ankle_right].y, world_landmarks[ankle_right].z]
    ankle_world_left = [world_landmarks[ankle_left].x, world_landmarks[ankle_left].y, world_landmarks[ankle_left].z]

    knee_flex_right = 180 - vectorMath.cal_threeD_angle(hip_world_right, knee_world_right, ankle_world_right)
    knee_flex_left = 180 - vectorMath.cal_threeD_angle(hip_world_left, knee_world_left, ankle_world_left)
    
    print("Knee R:", knee_flex_right, " ", "Knee L:", knee_flex_left, "\n")

    return knee_flex_right, knee_flex_left

def ankleFlex(world_landmarks):
    knee_world_right = [world_landmarks[knee_right].x, world_landmarks[knee_right].y, world_landmarks[knee_right].z]
    knee_world_left = [world_landmarks[knee_left].x, world_landmarks[knee_left].y, world_landmarks[knee_left].z]
    ankle_world_right = [world_landmarks[ankle_right].x, world_landmarks[ankle_right].y, world_landmarks[ankle_right].z]
    ankle_world_left = [world_landmarks[ankle_left].x, world_landmarks[ankle_left].y, world_landmarks[ankle_left].z]
    heel_world_right = [world_landmarks[heel_right].x, world_landmarks[heel_right].y, world_landmarks[heel_right].z]
    heel_world_left = [world_landmarks[heel_left].x, world_landmarks[heel_left].y, world_landmarks[heel_left].z]

    ankle_flex_right = 180 - vectorMath.cal_threeD_angle(knee_world_right, ankle_world_right, heel_world_right)
    ankle_flex_left = 180 - vectorMath.cal_threeD_angle(knee_world_left, ankle_world_left, heel_world_left)
    
    print("Ankle R:", ankle_flex_right, " ", "Ankle L:", ankle_flex_left, "\n")

    return ankle_flex_right, ankle_flex_left
