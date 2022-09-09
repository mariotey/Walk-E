import cv2
import mediapipe as mp
import vectorMath

FONT_STYLE = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.5
LINE_THICK = 1
LINE_TYPE = cv2.LINE_AA

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

def pelvicRotate(image, camera_landmarks, world_landmarks):
    hip_camera_right = [camera_landmarks[hip_right].x, camera_landmarks[hip_right].y]
    hip_camera_left = [camera_landmarks[hip_left].x, camera_landmarks[hip_left].y]
       
    hip_world_right = [world_landmarks[hip_right].x, world_landmarks[hip_right].y, world_landmarks[hip_right].z]
    hip_world_left = [world_landmarks[hip_left].x, world_landmarks[hip_left].y, world_landmarks[hip_left].z]

    hip_rotate_right = vectorMath.cal_twoD_angle([hip_world_right[0], hip_world_right[2]], [0,0], [hip_world_right[0], 0])
    hip_rotate_left = vectorMath.cal_twoD_angle([hip_world_left[0], hip_world_left[2]], [0,0], [hip_world_left[0], 0])

    # if hip_world_right[2] > 0:
    #     cv2.putText(image, str(round(hip_rotate_right,2)),
    #         tuple(vectorMath.np.multiply(hip_camera_right, WEBCAM_RES).astype(int)), 
    #         FONT_STYLE, FONT_SCALE, (0, 0, 255), LINE_THICK, LINE_TYPE)
    # else:
    #     cv2.putText(image, str(round(hip_rotate_right,2)),
    #         tuple(vectorMath.np.multiply(hip_camera_right, WEBCAM_RES).astype(int)), 
    #         FONT_STYLE, FONT_SCALE, (0, 255, 0), LINE_THICK, LINE_TYPE)

    # if hip_world_right[2] > 0:
    #     cv2.putText(image, str(round(hip_rotate_left,2)),
    #         tuple(vectorMath.np.multiply(hip_camera_left, WEBCAM_RES).astype(int)), 
    #         FONT_STYLE, FONT_SCALE, (0, 0, 255), LINE_THICK, LINE_TYPE)
    # else:
    #     cv2.putText(image, str(round(hip_rotate_left,2)),
    #         tuple(vectorMath.np.multiply(hip_camera_left, WEBCAM_RES).astype(int)), 
    #         FONT_STYLE, FONT_SCALE, (0, 255, 0), LINE_THICK, LINE_TYPE)
    
    return hip_rotate_right, hip_rotate_left

def shoulderRotate(image, camera_landmarks, world_landmarks):
    shoulder_camera_right = [camera_landmarks[shoulder_right].x, camera_landmarks[shoulder_right].y]
    shoulder_camera_left = [camera_landmarks[shoulder_left].x, camera_landmarks[shoulder_left].y]
       
    shoulder_world_right = [world_landmarks[shoulder_right].x, world_landmarks[shoulder_right].y, world_landmarks[shoulder_right].z]
    shoulder_world_left = [world_landmarks[shoulder_left].x, world_landmarks[shoulder_left].y, world_landmarks[shoulder_left].z]

    shoulder_rotate_right = vectorMath.cal_twoD_angle([shoulder_world_right[0], shoulder_world_right[2]], [0,0], [shoulder_world_right[0], 0])
    shoulder_rotate_left = vectorMath.cal_twoD_angle([shoulder_world_left[0], shoulder_world_left[2]], [0,0], [shoulder_world_left[0], 0])

    # if shoulder_world_right[2] > 0:
    #     cv2.putText(image, str(round(shoulder_rotate_right,2)),
    #         tuple(vectorMath.np.multiply(shoulder_camera_right, WEBCAM_RES).astype(int)), 
    #         FONT_STYLE, FONT_SCALE, (0, 0, 255), LINE_THICK, LINE_TYPE)
    # else:
    #     cv2.putText(image, str(round(shoulder_rotate_right,2)),
    #         tuple(vectorMath.np.multiply(shoulder_camera_right, WEBCAM_RES).astype(int)), 
    #         FONT_STYLE, FONT_SCALE, (0, 255, 0), LINE_THICK, LINE_TYPE)

    # if shoulder_world_left[2] > 0:
    #     cv2.putText(image, str(round(shoulder_rotate_left,2)),
    #         tuple(vectorMath.np.multiply(shoulder_camera_left, WEBCAM_RES).astype(int)), 
    #         FONT_STYLE, FONT_SCALE, (0, 0, 255), LINE_THICK, LINE_TYPE)
    # else:
    #     cv2.putText(image, str(round(shoulder_rotate_left,2)),
    #         tuple(vectorMath.np.multiply(shoulder_camera_left, WEBCAM_RES).astype(int)), 
    #         FONT_STYLE, FONT_SCALE, (0, 255, 0), LINE_THICK, LINE_TYPE)
    
    return shoulder_rotate_right, shoulder_rotate_left

def hipFlex(image, camera_landmarks, world_landmarks):
    hip_camera_right = [camera_landmarks[hip_right].x, camera_landmarks[hip_right].y]
    hip_camera_left = [camera_landmarks[hip_left].x, camera_landmarks[hip_left].y]
       
    shoulder_world_right = [world_landmarks[shoulder_right].x, world_landmarks[shoulder_right].y, world_landmarks[shoulder_right].z]
    shoulder_world_left = [world_landmarks[shoulder_left].x, world_landmarks[shoulder_left].y, world_landmarks[shoulder_left].z]
    hip_world_right = [world_landmarks[hip_right].x, world_landmarks[hip_right].y, world_landmarks[hip_right].z]
    hip_world_left = [world_landmarks[hip_left].x, world_landmarks[hip_left].y, world_landmarks[hip_left].z]
    knee_world_right = [world_landmarks[knee_right].x, world_landmarks[knee_right].y, world_landmarks[knee_right].z]
    knee_world_left = [world_landmarks[knee_left].x, world_landmarks[knee_left].y, world_landmarks[knee_left].z]

    hip_flex_right = 180 - vectorMath.cal_threeD_angle(shoulder_world_right, hip_world_right, knee_world_right)
    hip_flex_left = 180 - vectorMath.cal_threeD_angle(shoulder_world_left, hip_world_left, knee_world_left)
    
    # if hip_flex_right < 0:
    #     cv2.putText(image, str(round(hip_flex_right,2)),
    #         tuple(vectorMath.np.multiply(hip_camera_right, WEBCAM_RES).astype(int)), 
    #         FONT_STYLE, FONT_SCALE, (0, 0, 255), LINE_THICK, LINE_TYPE)
    # else:
    #     cv2.putText(image, str(round(hip_flex_right,2)),
    #         tuple(vectorMath.np.multiply(hip_camera_right, WEBCAM_RES).astype(int)), 
    #         FONT_STYLE, FONT_SCALE, (0, 255, 0), LINE_THICK, LINE_TYPE)

    # if hip_flex_left < 0:
    #     cv2.putText(image, str(round(hip_flex_left,2)),
    #         tuple(vectorMath.np.multiply(hip_camera_left, WEBCAM_RES).astype(int)), 
    #         FONT_STYLE, FONT_SCALE, (0, 0, 255), LINE_THICK, LINE_TYPE)
    # else:
    #     cv2.putText(image, str(round(hip_flex_left,2)),
    #         tuple(vectorMath.np.multiply(hip_camera_left, WEBCAM_RES).astype(int)), 
    #         FONT_STYLE, FONT_SCALE, (0, 255, 0), LINE_THICK, LINE_TYPE)

    return hip_flex_right, hip_flex_left

def kneeFlex(image, camera_landmarks, world_landmarks):
    knee_camera_right = [camera_landmarks[knee_right].x, camera_landmarks[knee_right].y]
    knee_camera_left = [camera_landmarks[knee_left].x, camera_landmarks[knee_left].y]
       
    hip_world_right = [world_landmarks[hip_right].x, world_landmarks[hip_right].y, world_landmarks[hip_right].z]
    hip_world_left = [world_landmarks[hip_left].x, world_landmarks[hip_left].y, world_landmarks[hip_left].z]
    knee_world_right = [world_landmarks[knee_right].x, world_landmarks[knee_right].y, world_landmarks[knee_right].z]
    knee_world_left = [world_landmarks[knee_left].x, world_landmarks[knee_left].y, world_landmarks[knee_left].z]
    ankle_world_right = [world_landmarks[ankle_right].x, world_landmarks[ankle_right].y, world_landmarks[ankle_right].z]
    ankle_world_left = [world_landmarks[ankle_left].x, world_landmarks[ankle_left].y, world_landmarks[ankle_left].z]

    knee_flex_right = 180 - vectorMath.cal_threeD_angle(hip_world_right, knee_world_right, ankle_world_right)
    knee_flex_left = 180 - vectorMath.cal_threeD_angle(hip_world_left, knee_world_left, ankle_world_left)
    
    # cv2.putText(image, str(round(knee_flex_right,2)),
    #     tuple(vectorMath.np.multiply(knee_camera_right, WEBCAM_RES).astype(int)), 
    #     FONT_STYLE, FONT_SCALE, (0, 0, 0), LINE_THICK, LINE_TYPE)
    # cv2.putText(image, str(round(knee_flex_left,2)),
    #     tuple(vectorMath.np.multiply(knee_camera_left, WEBCAM_RES).astype(int)), 
    #     FONT_STYLE, FONT_SCALE, (0, 0, 0), LINE_THICK, LINE_TYPE)

    return knee_flex_right, knee_flex_left

def ankleFlex(image, camera_landmarks, world_landmarks):
    ankle_camera_right = [camera_landmarks[ankle_right].x, camera_landmarks[ankle_right].y]
    ankle_camera_left = [camera_landmarks[ankle_left].x, camera_landmarks[ankle_left].y]
       
    knee_world_right = [world_landmarks[knee_right].x, world_landmarks[knee_right].y, world_landmarks[knee_right].z]
    knee_world_left = [world_landmarks[knee_left].x, world_landmarks[knee_left].y, world_landmarks[knee_left].z]
    ankle_world_right = [world_landmarks[ankle_right].x, world_landmarks[ankle_right].y, world_landmarks[ankle_right].z]
    ankle_world_left = [world_landmarks[ankle_left].x, world_landmarks[ankle_left].y, world_landmarks[ankle_left].z]
    heel_world_right = [world_landmarks[heel_right].x, world_landmarks[heel_right].y, world_landmarks[heel_right].z]
    heel_world_left = [world_landmarks[heel_left].x, world_landmarks[heel_left].y, world_landmarks[heel_left].z]

    ankle_flex_right = 180 - vectorMath.cal_threeD_angle(knee_world_right, ankle_world_right, heel_world_right)
    ankle_flex_left = 180 - vectorMath.cal_threeD_angle(knee_world_left, ankle_world_left, heel_world_left)
    
    # if ankle_flex_right < 0:
    #     cv2.putText(image, str(round(ankle_flex_right,2)),
    #         tuple(vectorMath.np.multiply(ankle_camera_right, WEBCAM_RES).astype(int)), 
    #         FONT_STYLE, FONT_SCALE, (0, 0, 255), LINE_THICK, LINE_TYPE)
    # else:
    #     cv2.putText(image, str(round(ankle_flex_right,2)),
    #         tuple(vectorMath.np.multiply(ankle_camera_right, WEBCAM_RES).astype(int)), 
    #         FONT_STYLE, FONT_SCALE, (0, 255, 0), LINE_THICK, LINE_TYPE)

    # if ankle_flex_left < 0:
    #     cv2.putText(image, str(round(ankle_flex_left,2)),
    #         tuple(vectorMath.np.multiply(ankle_camera_left, WEBCAM_RES).astype(int)), 
    #         FONT_STYLE, FONT_SCALE, (0, 0, 255), LINE_THICK, LINE_TYPE)
    # else:
    #     cv2.putText(image, str(round(ankle_flex_left,2)),
    #         tuple(vectorMath.np.multiply(ankle_camera_left, WEBCAM_RES).astype(int)), 
    #         FONT_STYLE, FONT_SCALE, (0, 255, 0), LINE_THICK, LINE_TYPE)

    return ankle_flex_right, ankle_flex_left

def pelvicOblique(image, camera_landmarks, world_landmarks):
    hip_camera_right = [camera_landmarks[hip_right].x, camera_landmarks[hip_right].y]
    hip_camera_left = [camera_landmarks[hip_left].x, camera_landmarks[hip_left].y]
       
    hip_world_right = [world_landmarks[hip_right].x, world_landmarks[hip_right].y, world_landmarks[hip_right].z]
    # hip_world_left = [world_landmarks[hip_left].x, world_landmarks[hip_left].y, world_landmarks[hip_left].z]

    hip_oblique = vectorMath.cal_twoD_angle([hip_world_right[0], hip_world_right[1]], [0,0], [0,1]) - 90
    # hip_oblique_left = vectorMath.cal_twoD_angle([hip_world_left[0], hip_world_left[2]], [0,0], [hip_world_left[0], 0])

    # if hip_oblique_right < 0:
    #     cv2.putText(image, str(round(hip_oblique_right,2)),
    #         tuple(vectorMath.np.multiply(hip_camera_right, WEBCAM_RES).astype(int)), 
    #         FONT_STYLE, FONT_SCALE, (0, 0, 255), LINE_THICK, LINE_TYPE)
    # else:
    #     cv2.putText(image, str(round(hip_oblique_right,2)),
    #         tuple(vectorMath.np.multiply(hip_camera_right, WEBCAM_RES).astype(int)), 
    #         FONT_STYLE, FONT_SCALE, (0, 255, 0), LINE_THICK, LINE_TYPE)

    # if hip_oblique_left < 0:
    #     cv2.putText(image, str(round(hip_oblique_left,2)),
    #         tuple(vectorMath.np.multiply(hip_camera_left, WEBCAM_RES).astype(int)), 
    #         FONT_STYLE, FONT_SCALE, (0, 0, 255), LINE_THICK, LINE_TYPE)
    # else:
    #     cv2.putText(image, str(round(hip_oblique_left,2)),
    #         tuple(vectorMath.np.multiply(hip_camera_left, WEBCAM_RES).astype(int)), 
    #         FONT_STYLE, FONT_SCALE, (0, 255, 0), LINE_THICK, LINE_TYPE)

    
    # if hip_oblique < 0: 
    #     cv2.putText(image, str(round(hip_oblique,2)),
    #             tuple(vectorMath.np.multiply(hip_camera_right, WEBCAM_RES).astype(int)), 
    #             FONT_STYLE, FONT_SCALE, (0, 0, 255), LINE_THICK, LINE_TYPE)
    # else:
    #     cv2.putText(image, str(round(hip_oblique,2)),
    #             tuple(vectorMath.np.multiply(hip_camera_right, WEBCAM_RES).astype(int)), 
    #             FONT_STYLE, FONT_SCALE, (0, 255, 0), LINE_THICK, LINE_TYPE)
    
    return hip_oblique

def shoulderOblique(image, camera_landmarks, world_landmarks):
    hip_camera_right = [camera_landmarks[hip_right].x, camera_landmarks[hip_right].y]
    hip_camera_left = [camera_landmarks[hip_left].x, camera_landmarks[hip_left].y]
    
       
    shoulder_world_right = [world_landmarks[shoulder_right].x, world_landmarks[shoulder_right].y, world_landmarks[shoulder_right].z]
    shoulder_world_left = [world_landmarks[shoulder_left].x, world_landmarks[shoulder_left].y, world_landmarks[shoulder_left].z]
    
    shoulder_world_mid = [(shoulder_world_right[0] + shoulder_world_left[0])/2,
                          (shoulder_world_right[1] + shoulder_world_left[1])/2,
                          (shoulder_world_right[2] + shoulder_world_left[2])/2]
    
    # hip_world_right = [world_landmarks[hip_right].x, world_landmarks[hip_right].y, world_landmarks[hip_right].z]
    hip_world_left = [world_landmarks[hip_left].x, world_landmarks[hip_left].y, world_landmarks[hip_left].z]

    shoulder_oblique = 90 - vectorMath.cal_twoD_angle([shoulder_world_mid[0], shoulder_world_mid[1]], [0,0], [hip_world_left[0], hip_world_left[1]]) + 2

    # if shoulder_oblique < 0: #Left shoulder is higher
    #     cv2.putText(image, str(round(shoulder_oblique,2)),
    #         tuple(vectorMath.np.multiply(hip_camera_right, WEBCAM_RES).astype(int)), 
    #         FONT_STYLE, FONT_SCALE, (0, 0, 255), LINE_THICK, LINE_TYPE)
    # else:#Right shoulder is higher
    #     cv2.putText(image, str(round(shoulder_oblique,2)),
    #         tuple(vectorMath.np.multiply(hip_camera_right, WEBCAM_RES).astype(int)), 
    #         FONT_STYLE, FONT_SCALE, (0, 255, 0), LINE_THICK, LINE_TYPE)

    return shoulder_oblique