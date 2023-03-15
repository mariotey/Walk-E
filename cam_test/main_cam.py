import cv2
import mediapipe as mp
import walkE_math

mp_pose = mp.solutions.pose # Pose Estimation Model

# Drawing utilities for visualizing poses
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose  # Pose Estimation Model

WAIT_TIME = 5

# Get Realtime Webcam Feed
cap = cv2.VideoCapture(0)  # Get Video Capture Device

#################################################################################################

def detect(image, landmarks):
    right_hip = mp_pose.PoseLandmark.RIGHT_HIP.value
    left_hip = mp_pose.PoseLandmark.LEFT_HIP.value

    right_hip_camera = [landmarks[right_hip].x, landmarks[right_hip].y]
    left_hip_camera = [landmarks[left_hip].x, landmarks[left_hip].y]

    hip_dist = walkE_math.cal_twoD_dist(right_hip_camera, left_hip_camera)
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
        
#################################################################################################

with mp_pose.Pose(  # Setting up Pose Estimation Model
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        enable_segmentation=True,
        smooth_segmentation=True,
        smooth_landmarks=True,
        static_image_mode=False) as pose:
    
    while cap.isOpened():
        ret, frame = cap.read()  # Reads feed from Webcam

        # Recolour Image feed (from openCV) from BGR to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Save memory by setting writeable attribute as false; improves performance
        image.flags.writeable = False

        # Pass recoloured image feed to Pose Estimation model for processing
        results = pose.process(image)
        image.flags.writeable = True

        # Recolour Image back to BGR for openCV to process, Make Detection
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Draw Pose Estimation landmarks                                       
        mp_drawing.draw_landmarks(image,
                                results.pose_landmarks,
                                mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(245, 66, 230),
                                                        thickness=0,
                                                        circle_radius=0),
                                mp_drawing.DrawingSpec(color=(245, 66, 230),
                                                        thickness=2,
                                                        circle_radius=0)
                                )

        try:
            camera_lm = results.pose_landmarks.landmark
            world_lm = results.pose_world_landmarks.landmark

            detect(image, camera_lm)

        except AttributeError:
            # print("Nothing / Errors detected")
            pass  # Pass if there is no detection or error   
         
        cv2.imshow("Mediapipe Feed", image)  # Render image result on screen

        # TBC when integrated with Walk-E
        if cv2.waitKey(WAIT_TIME) & 0xFF == ord("q"):
            break

###################################################################################################

cap.release()  # Release camera
cv2.destroyAllWindows()  # Destroy all cv2 windows

#.\venv\Scripts\python.exe -m pylint .\Walk-E\main_mediapipe.py