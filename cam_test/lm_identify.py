import mediapipe as mp
import cv2
import numpy as np
import cam_math

mp_pose = mp.solutions.pose # Pose Estimation Model

righthip_value = mp_pose.PoseLandmark.RIGHT_HIP.value
lefthip_value = mp_pose.PoseLandmark.LEFT_HIP.value
rightheel_value = mp_pose.PoseLandmark.RIGHT_HEEL.value
leftheel_value = mp_pose.PoseLandmark.LEFT_HEEL.value
righttoe_value = mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value
lefttoe_value = mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value

def detect(image, landmarks):
    right_hip_camera = [landmarks[righthip_value].x, landmarks[righthip_value].y]
    left_hip_camera = [landmarks[lefthip_value].x, landmarks[lefthip_value].y]

    hip_dist = cam_math.cal_twoD_dist(right_hip_camera, left_hip_camera)
    print("Hip Length:", hip_dist)
       
    if hip_dist > (0.15 * 1.05):
        cv2.rectangle(image, (0,0), (300, 25), (16,117,245), -1)
        cv2.putText(image, f"Hip Length: {hip_dist}", (15,12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA)
    elif hip_dist < (0.15 * 0.8):
        cv2.rectangle(image, (0,0), (300, 25), (117,245,16), -1)
        cv2.putText(image, f"Hip Length: {hip_dist}", (15,12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)  
    else:
        cv2.rectangle(image, (0,0), (300, 25), (245,117,16), -1)
        cv2.putText(image, f"Hip Length: {hip_dist}", (15,12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA)
        
    return hip_dist

def hip(image, camera_lm, world_lm):
    righthip_cam = [camera_lm[righthip_value].x, camera_lm[righthip_value].y]
    righthip_text = round(world_lm[righthip_value].y,2)

    cv2.putText(image, str(righthip_text),
                tuple(np.multiply(righthip_cam, [640, 480]).astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2, cv2.LINE_AA)
    
    lefthip_cam = [camera_lm[lefthip_value].x, camera_lm[lefthip_value].y]
    lefthip_text = round(world_lm[lefthip_value].y,2)

    cv2.putText(image, str(lefthip_text),
                tuple(np.multiply(lefthip_cam, [640, 480]).astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2, cv2.LINE_AA)
    
    return righthip_text, lefthip_text
    
def left_heel(image, camera_lm, world_lm):
    leftheel_cam = [camera_lm[leftheel_value].x, camera_lm[leftheel_value].y]
    leftheel_y = round(world_lm[leftheel_value].y,2)

    cv2.putText(image, str(leftheel_y),
                tuple(np.multiply(leftheel_cam, [640, 480]).astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2, cv2.LINE_AA)
    
def right_heel(image, camera_lm, world_lm):
    rightheel_cam = [camera_lm[rightheel_value].x, camera_lm[rightheel_value].y]
    rightheel_y = round(world_lm[rightheel_value].y,2)

    cv2.putText(image, str(rightheel_y),
                tuple(np.multiply(rightheel_cam, [640, 480]).astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2, cv2.LINE_AA)

def right_toe(image, camera_lm, world_lm):
    righttoe_cam = [camera_lm[righttoe_value].x, camera_lm[righttoe_value].y]
    righttoe_text = round(world_lm[righttoe_value].y,2)

    cv2.putText(image, str(righttoe_text),
                tuple(np.multiply(righttoe_cam, [640, 480]).astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2, cv2.LINE_AA)
    
def gait_logic(image, camera_lm, world_lm):
    leftheel_cam = [camera_lm[leftheel_value].x, camera_lm[leftheel_value].y]

    leftheel_x = round(world_lm[leftheel_value].x,2)

    cv2.putText(image, str(leftheel_x),
        tuple(np.multiply(leftheel_cam, [640, 480]).astype(int)),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2, cv2.LINE_AA)
