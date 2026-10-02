import rclpy                                              # ROS 2 Python 客户端库
from rclpy.node import Node                               # 节点基类
from chapt4_interfaces.srv import FaceDetector            # 自定义服务类型（请求图像，返回人脸信息）
import cv2                                                # OpenCV，用于读图、画框、显示
from ament_index_python.packages import get_package_share_directory  # 获取包在 install 下的 share 路径
import os                                                 # 用于安全拼接路径
from cv_bridge import CvBridge                            # ROS 图像消息 <-> OpenCV 图像 转换


class FaceDetectClientNode(Node):
    """人脸检测客户端节点"""

    def __init__(self):
        super().__init__('face_detect_client_node')       # 初始化节点，节点名 face_detect_client_node
        # 创建客户端：类型 FaceDetector，服务名 face_detect
        self.client = self.create_client(FaceDetector, 'face_detect')
        self.bridge = CvBridge()                          # 创建图像转换器
        # 拼接要发送的图片的绝对路径：包share目录/resource/xxx.png
        self.default_image_path = os.path.join(
            get_package_share_directory('demo_python_service'),  # 包安装路径
            'resource',                                          # 子目录
            '2026-10-02_14-13.png'                               # 图片文件名
        )
        self.image = cv2.imread(self.default_image_path)  # 读取图片到内存（OpenCV BGR 格式）
        self.get_logger().info('客户端启动')               # 日志：客户端已启动

    def send_request(self):
        """构造请求、发送给服务端、等待结果、调用画框"""
        # 等待服务端上线，每 1 秒检查一次，没上线就打日志继续等
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('服务未就绪，等待中...')

        request = FaceDetector.Request()                  # 创建请求对象
        # 把 OpenCV 图像转成 ROS 图像消息，填入请求
        request.image = self.bridge.cv2_to_imgmsg(self.image, encoding='bgr8')
        future = self.client.call_async(request)          # 异步发送请求，返回 future
        # 阻塞等待 future 完成（必须传 self 和 future）
        rclpy.spin_until_future_complete(self, future)
        response = future.result()                        # 取出服务端返回的响应
        # 日志：打印人脸数量和耗时
        self.get_logger().info(
            f'人脸检测结果: {response.number} 张人脸，耗时 {response.use_time:.4f} 秒'
        )
        self.show_response(response)                      # 调用画框函数

    def show_response(self, response):
        """根据响应里每张脸的坐标，在图像上画矩形框并显示"""
        for i in range(response.number):                  # 遍历每一张脸
            top = response.top[i]                         # 第 i 张脸的上边界
            right = response.right[i]                     # 第 i 张脸的右边界
            bottom = response.bottom[i]                   # 第 i 张脸的下边界
            left = response.left[i]                       # 第 i 张脸的左边界
            # 在图像上画矩形框：左上角(left, top)，右下角(right, bottom)，蓝色(255,0,0)，线宽4
            cv2.rectangle(self.image, (left, top), (right, bottom), (255, 0, 0), 4)
        cv2.imshow('Face Detection Result', self.image)   # 弹窗显示画好框的图像
        cv2.waitKey(0)                                    # 等待按键，按任意键关闭窗口


def main(args=None):
    rclpy.init(args=args)                                 # 初始化 rclpy
    node = FaceDetectClientNode()                         # 创建客户端节点实例
    node.send_request()                                   # 发请求、等结果、画框，全在里面
    node.destroy_node()                                   # 销毁节点，释放资源
    rclpy.shutdown()                                      # 关闭 rclpy


if __name__ == '__main__':
    main()                                                # 作为脚本运行入口