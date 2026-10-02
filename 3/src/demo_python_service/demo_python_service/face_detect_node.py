import rclpy                                              # ROS 2 Python 客户端库
from rclpy.node import Node                               # 节点基类
from chapt4_interfaces.srv import FaceDetector            # 自定义服务类型（请求图像，返回人脸信息）
import face_recognition                                   # 人脸识别库（底层 dlib，用于定位人脸）
import cv2                                                # OpenCV，用于读图等图像操作
from ament_index_python.packages import get_package_share_directory  # 获取包在 install 下的 share 路径
import os                                                 # 用于安全拼接路径
from cv_bridge import CvBridge                            # ROS 图像消息 <-> OpenCV 图像 转换
import time                                               # 用于计时
from rcl_interfaces.msg import SetParametersResult        # 参数回调的返回类型


class FaceDetectNode(Node):
    """人脸检测服务端节点"""

    def __init__(self):
        super().__init__('face_detect_node')              # 初始化节点，节点名 face_detect_node
        # 创建服务：类型 FaceDetector，服务名 face_detect，回调 face_detect_callback
        self.srv = self.create_service(FaceDetector, 'face_detect', self.face_detect_callback)
        self.bridge = CvBridge()                          # 创建图像转换器
        self.declare_parameter('number_of_times_to_upsample', 1)  # 声明参数：上采样次数，越大越能检小脸但越慢
        self.declare_parameter('model', 'hog')            # 声明参数：检测模型
        self.number_of_times_to_upsample = self.get_parameter('number_of_times_to_upsample').value  # 读取上采样次数
        self.model = self.get_parameter('model').value    # 读取检测模型：hog 快(CPU)，cnn 慢(需 GPU)
        self.get_logger().info('Face Detect Service is ready.')  # 日志：服务就绪
        # 拼接默认图片的绝对路径：包share目录/resource/default.jpg
        self.default_image_path = os.path.join(
            get_package_share_directory('demo_python_service'),  # 包安装路径
            'resource',                                          # 子目录
            'default.jpg'                                        # 图片文件名
        )
        self.add_on_set_parameters_callback(self.parameter_callback)  # 注册参数回调函数

    def parameter_callback(self, params):
        """参数回调：当参数被修改时触发"""
        for param in params:
            if param.name == 'number_of_times_to_upsample':
                self.number_of_times_to_upsample = param.value  # 更新上采样次数
                self.get_logger().info(f'Updated number_of_times_to_upsample: {param.value}')
            elif param.name == 'model':
                self.model = param.value                          # 更新检测模型
                self.get_logger().info(f'Updated model: {param.value}')
        return SetParametersResult(successful=True)          # 返回成功（正确的类型）

    def face_detect_callback(self, request, response):
        """服务回调：收到请求后执行人脸检测并填充响应"""
        # 请求里带了图像数据就用请求的图，否则用默认图
        if request.image.data:
            cv_image = self.bridge.imgmsg_to_cv2(request.image, desired_encoding='bgr8')  # ROS图像转OpenCV(BGR)
        else:
            cv_image = cv2.imread(self.default_image_path)    # 读取默认图片

        start_time = time.time()                              # 记录开始时间
        self.get_logger().info('Starting face detection...')  # 日志：开始检测
        # 调用人脸检测，返回每张脸的 (top, right, bottom, left) 坐标列表
        face_locations = face_recognition.face_locations(
            cv_image,
            number_of_times_to_upsample=self.number_of_times_to_upsample,
            model=self.model
        )
        response.use_time = time.time() - start_time          # 响应：处理耗时（对应 srv 的 use_time）
        response.number = len(face_locations)                 # 响应：人脸数量（对应 srv 的 number）
        # 把每张脸的位置分别填入响应数组
        for top, right, bottom, left in face_locations:
            response.top.append(top)                          # 上边界
            response.right.append(right)                      # 右边界
            response.bottom.append(bottom)                    # 下边界
            response.left.append(left)                        # 左边界
        return response                                       # 返回响应给客户端


def main(args=None):
    rclpy.init(args=args)                                     # 初始化 rclpy
    node = FaceDetectNode()                                   # 创建节点实例
    try:
        rclpy.spin(node)                                      # 一直运行，等待服务请求
    except KeyboardInterrupt:
        pass                                                  # 捕获 Ctrl+C，不打印回溯
    finally:
        node.destroy_node()                                   # 销毁节点，释放资源
        if rclpy.ok():
            rclpy.shutdown()                                  # 关闭 rclpy（若还开着）


if __name__ == '__main__':
    main()                                                    # 作为脚本运行入口