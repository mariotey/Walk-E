# BN4101: Walking Buddy for Prehabilitation #

## Description ##
Prehabilitation is an intervention that is introduced prior to surgery to raise a patient’s functional capacity and reduce their risk of post-surgical complications. To evaluate a patient’s recovery and the effectiveness of the prehabilitative programme, gait analysis is often employed, particularly for patients undergoing lower limb surgery.

Unfortunately, conventional gait analysis methods such as motion capture system, EMG sensors and force plates require specialized environment and significant investment of both finances and human resources to set up, maintain and analyze. As not all hospitals have dedicated gait labs, it may be challenging for patients with mobility issues to travel to these specialized labs for gait analysis. Moreover, the placement of reflective markers can be uncomfortable for patients and their sweat could render the markers useless. It can also be a time-consuming and arduous process for healthcare providers that need to perform gait analysis on large numbers of patients.

Hence, this project seeks to address these challenges by exploring the feasibility of integrating MediaPipe’s 3D human pose estimation into a wheeled robot for gait analysis. The wheeled robot will be equipped with a Raspberry Pi, web camera, and optical encoders to physically guide patients along a curated route and provide quick analytics of patient’s lower limb performance.  This approach not only minimizes the amount of specialized equipment needed for analysis but also make gait analysis more accessible, comfortable and efficient for patients and healthcare providers. Unlike conventional methods of analysis, the wheeled robot is unique in that it can be self-administered which further reduces the need for large number of healthcare providers.
Given the diverse range of patients receiving lower limb surgeries and the increasing aging population, this robot may have the potential to benefit a larger population besides prehabilitative patients and advance innovation in the field of gait analysis.
 
## Getting Started ##
### Dependencies ###
- MediaPipe
- Flask
- opencv-python
- redis
- scipy
- scikit-learn

### Installing ###
- Fork project from this repository
- Install all dependencies that were stated above
- Install redis server on local device (Raspberry Pi / Computer)

### Executing Program ###
- Run redis servers on Raspberry Pi
- If the codes are on Raspberry Pi, run main_rasp.py
- If the codes are on Computer, run main_com.py

### Demonstration ###
- https://drive.google.com/file/d/1KwERTNXW4ly4oGkfd7G8EUDZwm02rYaV/view?usp=share_link

## Author ##
Tey Ming Chuan

## Acknowledgement ##
Dr. Yeow Chen Hua, Raye
