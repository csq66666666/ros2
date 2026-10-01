import face_recognition
import cv2
from ament_index_python.packages import get_package_share_directory
import os
def main():
    # 获取图片的真实路径 /home/fishros/chapt4/chapt4_ws/install/demo_python_service/share/
    # demo_python_service
    default_image_path = os.path.join(get_package_share_directory('demo_python_service'), 'resource', 'default.jpg')
    print(f"图片的真实路径: {default_image_path}")
    image = cv2.imread(default_image_path)
    face_locations = face_recognition.face_locations(image,number_of_times_to_upsample=1, model="hog")
    for top, right, bottom, left in face_locations:
        cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 4)
    cv2.imshow("Face Detection Result", image)
    cv2.waitKey(0)