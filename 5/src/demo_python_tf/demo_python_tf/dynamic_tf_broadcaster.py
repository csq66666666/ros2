import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster          # 动态坐标发布器
from geometry_msgs.msg import TransformStamped
from tf_transformations import quaternion_from_euler
import math


class DynamicTFBroadcaster(Node):
    def __init__(self):
        super().__init__('dynamic_tf_broadcaster')
        self.tf_broadcaster_ = TransformBroadcaster(self)

        # 定时器：每 0.1 秒发布一次（10 Hz）
        self.timer_ = self.create_timer(0.1, self.publish_dynamic_tf)

        # 一个随时间累加的计数器，用来让坐标动起来
        self.t_ = 0.0

    def publish_dynamic_tf(self):
        """
        发布动态TF
        """
        transform = TransformStamped()
        transform.header.frame_id = 'camera_link'
        transform.child_frame_id = 'bottle_link'
        # 每次发布都更新为当前时间
        transform.header.stamp = self.get_clock().now().to_msg()

        # 让相机随时间做圆周运动（也可以做别的）
        
        transform.transform.translation.x = 0.2
        transform.transform.translation.y = 0.3
        transform.transform.translation.z = 0.5

        # 旋转：绕 Z 轴随时间转动
        q = quaternion_from_euler(0, 0, 0)
        transform.transform.rotation.x = q[0]
        transform.transform.rotation.y = q[1]
        transform.transform.rotation.z = q[2]
        transform.transform.rotation.w = q[3]

        # 动态坐标关系发布出去
        self.tf_broadcaster_.sendTransform(transform)
        self.get_logger().info(f'发布动态TF: {transform}')


def main(args=None):
    rclpy.init(args=args)
    node = DynamicTFBroadcaster()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()