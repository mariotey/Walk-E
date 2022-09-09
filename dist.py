import cv2
import mediapipe as mp
import vectorMath

mp_pose = mp.solutions.pose # Pose Estimation Model

right_hip = mp_pose.PoseLandmark.RIGHT_HIP.value
left_hip = mp_pose.PoseLandmark.LEFT_HIP.value

def detect(image, landmarks):
    right_hip_camera = [landmarks[right_hip].x, landmarks[right_hip].y]
    left_hip_camera = [landmarks[left_hip].x, landmarks[left_hip].y]

    hip_dist = vectorMath.cal_twoD_dist(right_hip_camera, left_hip_camera)
    # print("Hip Length:", hip_dist)
    
    cv2.rectangle(image, (0,0), (300, 25), (245,117,16), -1)
            
    if hip_dist > 0.1:
        cv2.putText(image, "Too Close! Walk-E will accelerate", (15,12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
    elif hip_dist < 0.07:
        cv2.putText(image, "Too Far! Walk-E will slow down", (15,12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
    else:
        cv2.putText(image, "Walk-E will maintain current speed", (15,12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
