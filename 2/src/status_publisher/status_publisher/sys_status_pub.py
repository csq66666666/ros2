import rclpy
from status_interfaces.msg import SystemStatus
from rclpy.node import Node
import psutil
import platform

class SystemStatusPub(Node):
    def __init__(self, node_name):
        super().__init__(node_name)
        # 创建发布者
        self.status_publisher_ = self.create_publisher(SystemStatus, 'system_status', 10)
        # 创建定时器，1秒触发一次
        self.timer = self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        # 1. 获取系统底层数据
        cpu_percent = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        net_io_counters = psutil.net_io_counters()

        # 2. 填入自定义消息
        msg = SystemStatus()
        msg.stamp = self.get_clock().now().to_msg()       # 记录时间戳
        msg.host_name = platform.node()                   # 主机名
        msg.cpu_percent = float(cpu_percent)              # CPU使用率（转float）
        msg.memory_percent = float(memory_info.percent)   # 内存使用率（转float）
        
        # 内存单位换算为 MB，并转为 float
        msg.memory_total = float(memory_info.total / 1024 / 1024)          
        msg.memory_available = float(memory_info.available / 1024 / 1024)  
        
        # 网络单位换算为 MB，并转为 float
        msg.net_sent = float(net_io_counters.bytes_sent / 1024 / 1024)     
        msg.net_recv = float(net_io_counters.bytes_recv / 1024 / 1024)     

        # 3. 发布消息
        self.status_publisher_.publish(msg)

        # 4. 打印更多详细状态信息
        self.get_logger().info(
            f'\n'
            f'--- 系统状态 ---\n'
            f'主机名: {msg.host_name}\n'
            f'CPU使用率: {msg.cpu_percent}%\n'
            f'内存使用率: {msg.memory_percent}%\n'
            f'内存总量: {msg.memory_total:.2f} MB\n'
            f'可用内存: {msg.memory_available:.2f} MB\n'
            f'网络发送总量: {msg.net_sent:.2f} MB\n'
            f'网络接收总量: {msg.net_recv:.2f} MB\n'
            f'----------------'
        )

def main(args=None):
    rclpy.init(args=args)
    node = SystemStatusPub('system_status_pub')
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass  # 捕获 Ctrl+C，安静地退出
    finally:
        node.destroy_node()
        # ⚠️ 不要写 rclpy.shutdown()，防止二次关闭报错

if __name__ == '__main__':
    main()