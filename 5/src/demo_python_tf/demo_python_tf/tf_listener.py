import rclpy
from rclpy.node import Node
from tf2_ros import TransformListener, Buffer
from tf_transformations import euler_from_quaternion
import math


class TFListener(Node):
    def __init__(self):
        super().__init__('tf_listener')
        self.buffer_ = Buffer()
        self.listener_ = TransformListener(self.buffer_, self)
        self.timer_ = self.create_timer(1.0, self.lookup_tf)

    def lookup_tf(self):
        try:
            # ✅ 只传 3 个参数
            result = self.buffer_.lookup_transform(
                'base_link',
                'bottle_link',
                rclpy.time.Time()          # 最新可用
            )
            transform = result.transform

            self.get_logger().info(f'平移:{transform.translation}')
            self.get_logger().info(f'旋转:{transform.rotation}')

            # ✅ 传一个列表
            rotation_euler = euler_from_quaternion([
                transform.rotation.x,
                transform.rotation.y,
                transform.rotation.z,
                transform.rotation.w
            ])
            self.get_logger().info(f'旋转RPY:{rotation_euler}')

        except Exception as e:
            self.get_logger().warn(f'获取坐标变换失败:原因{str(e)}')


def main(args=None):
    rclpy.init(args=args)
    node = TFListener()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()