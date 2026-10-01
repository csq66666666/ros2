# 导入人脸识别库（底层基于 dlib，用于检测人脸位置）
import face_recognition

# 导入 OpenCV，用于图像读取、绘制矩形框、显示图像
import cv2

# 从 ament_index_python 导入工具函数，用于获取 ROS 2 包在 install/ 下的 share 路径
from ament_index_python.packages import get_package_share_directory

# 导入 os，用于安全地拼接路径（自动处理斜杠）
import os


def main():
    # 获取图片的真实路径
    # 说明：ROS 2 运行时代码用的是 install/ 下的文件，不是 src/ 下的
    # get_package_share_directory('demo_python_service') 返回：
    #   /home/xxx/ros2/3/install/demo_python_service/share/demo_python_service
    # 用 os.path.join 拼接后得到完整图片路径
    default_image_path = os.path.join(
        get_package_share_directory('demo_python_service'),  # 包安装路径
        'resource',                                          # 子目录
        'default.jpg'                                        # 图片文件名
    )

    # 打印路径，便于调试确认是否正确
    print(f"图片的真实路径: {default_image_path}")

    # 用 OpenCV 读取图片，返回 numpy 数组（像素矩阵）
    # 注意：如果路径错误或文件不存在，cv2.imread 不会报错，而是返回 None
    image = cv2.imread(default_image_path)

    # 使用 face_recognition 检测图中所有人脸
    # 返回值是一个列表，每个元素是 (top, right, bottom, left) 坐标
    # number_of_times_to_upsample=1：上采样次数，值越大越容易检测到小人脸，但更慢
    # model="hog"：使用 HOG 模型（CPU 友好、速度快）；也可选 "cnn"（更准，需 GPU）
    face_locations = face_recognition.face_locations(
        image,
        number_of_times_to_upsample=1,
        model="hog"
    )

    # 遍历检测到的每张人脸，在原图上画绿色矩形框
    # cv2.rectangle(图像, 左上角坐标, 右下角坐标, 颜色(BGR), 线宽)
    # 注意 OpenCV 坐标是 (x, y)，所以左上角是 (left, top)，右下角是 (right, bottom)
    for top, right, bottom, left in face_locations:
        cv2.rectangle(
            image,
            (left, top),      # 左上角
            (right, bottom),  # 右下角
            (0, 255, 0),      # 绿色（BGR）
            4                 # 线宽 4 像素
        )

    # 弹窗显示画好框的图片
    cv2.imshow("Face Detection Result", image)

    # 等待按键，参数 0 表示无限等待，按任意键关闭窗口
    # 如果不加这句，窗口会一闪而过
    cv2.waitKey(0)