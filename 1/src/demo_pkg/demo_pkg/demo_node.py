#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 上面两行：声明用系统环境里的 python3 执行；声明源码为 UTF-8（因为有中文注释）

import rclpy                                              # 导入 ROS 2 的 Python 客户端库（整个框架的入口）
from rclpy.node import Node                               # 导入 Node 基类，我们自己的节点要继承它
from rclpy.executors import ExternalShutdownException     # 导入异常类：外部（Ctrl+C / kill）触发关机时 spin 会抛它
from std_msgs.msg import String                           # 导入标准消息类型 String（只有 data 一个字符串字段）


class DemoNode(Node):                                     # 定义节点类，继承 rclpy 的 Node，获得创建发布/订阅/定时器的能力

    def __init__(self):                                   # 构造函数：节点被创建时执行一次
        super().__init__('demo_node')                     # 调用父类构造，注册节点名 'demo_node'（ros2 node list 里显示的名字）

        # ---------------- 1. 参数（Parameter）：外部可在启动时或运行时配置 ------------------
        self.declare_parameter('publish_period', 1.0)     # 声明一个浮点参数，默认 1.0 秒（定时器周期）
        self.declare_parameter('message_prefix', 'hello') # 声明一个字符串参数，默认 'hello'（消息前缀）

        self.period = self.get_parameter('publish_period').value   # 读取参数的当前值，存到成员变量方便使用
        self.prefix = self.get_parameter('message_prefix').value   # 读取字符串参数的值

        self.count = 0                                    # 计数器：记录已经发布过多少条消息（用于拼消息内容）

        # ---------------- 2. 发布者（Publisher）：向话题 'chatter' 发 String 消息 -------------
        self.pub = self.create_publisher(String, 'chatter', 10)    # 创建发布者：消息类型 String、话题名 'chatter'、队列深度 10
        
        # ---------------- 3. 订阅者（Subscription）：接收话题上的消息并回调 ----------------
        self.sub = self.create_subscription(                        # 创建订阅者
            String,                                                 # 订阅的消息类型
            'chatter',                                              # 订阅的话题名（和发布者同名，形成自发自收的回环）
            self.on_chatter,                                        # 收到消息时自动调用的回调函数
            10)                                                     # 队列深度 10

        self.cmd_sub = self.create_subscription(                     # 再建一个订阅者，演示“接收外部指令”
            String,                                                  # 消息类型同为 String
            'cmd',                                                    # 话题名 'cmd'
            self.on_cmd,                                              # 回调函数
            10)                                                       # 队列深度 10

        # ---------------- 4. 参数变更回调：运行时 ros2 param set 时触发 ----------------
        self.add_on_set_parameters_callback(self.on_param_change)    # 注册回调，参数被修改时先经过它

        # ---------------- 5. 定时器（Timer）：周期性执行任务 ----------------------------
        self.timer = self.create_timer(self.period, self.on_timer)   # 每 period 秒调用一次 on_timer

        self.get_logger().info(                                      # 打印一条 info 级日志（带时间戳和节点名）
            f'demo_node 已启动: period={self.period}s, prefix={self.prefix}')   # f-string 拼接实际参数值

    def on_timer(self):                                   # 定时器回调：到点就被执行
        self.count += 1                                   # 计数加一
        msg = String()                                    # 实例化一条 String 消息
        msg.data = f'{self.prefix} #{self.count}'         # 填充消息内容，例如 'hello #3'
        self.pub.publish(msg)                             # 通过发布者把消息发到 'chatter' 话题
        self.get_logger().info(f'发布: {msg.data}')       # 日志确认已发送

    def on_chatter(self, msg):                            # 订阅 'chatter' 的回调，msg 是收到的 String 对象
        self.get_logger().info(f'收到 chatter: {msg.data}')   # 把收到的内容打印出来

    def on_cmd(self, msg):                                # 订阅 'cmd' 的回调
        self.get_logger().warn(f'收到指令: {msg.data}')   # 用 warn 级别打印，便于在终端里区分

    def on_param_change(self, params):                    # 参数修改回调，params 是本轮被修改的参数列表
        for p in params:                                  # 逐个检查被修改的参数
            if p.name == 'publish_period':                # 如果改的是定时器周期
                self.period = float(p.value)              # 更新本地记录的周期值
                self.destroy_timer(self.timer)            # 销毁旧的定时器
                self.timer = self.create_timer(           # 用新周期重建定时器
                    self.period, self.on_timer)           # 仍绑定同一个回调
                self.get_logger().info(f'定时器周期已改为 {self.period}s')  # 日志提示生效
            elif p.name == 'message_prefix':              # 如果改的是消息前缀
                self.prefix = str(p.value)                # 直接更新，下一条消息就会用新前缀
        return rclpy.node.SetParametersResult(successful=True)   # 返回“接受修改”，值为 False 时参数会被拒绝


def main(args=None):                                      # 程序主入口
    rclpy.init(args=args)                                 # 初始化 rclpy 上下文（必须在建节点之前）
    node = DemoNode()                                     # 实例化我们的节点对象
    try:                                                  # 用 try 包住 spin，便于捕获中断信号
        rclpy.spin(node)                                  # 阻塞式事件循环：持续处理回调，直到被中断或关机
    except (KeyboardInterrupt, ExternalShutdownException):  # Ctrl+C 或外部 kill 导致的正常退出
        pass                                              # 属于预期退出，忽略异常继续清理
    finally:                                              # 无论是否异常，都要执行清理
        node.destroy_node()                               # 销毁节点，释放发布者/订阅者/定时器资源
        if rclpy.ok():                                    # 仅当上下文还没被关机时才关（否则重复 shutdown 会报 RCLError）
            rclpy.shutdown()                              # 关闭 rclpy 上下文（与 init 配对）


if __name__ == '__main__':                                # 只有“直接 python3 node_test.py”时才执行下面一行
    main()                                                # 调用主入口；被 import 时不会自动运行

# 定义类 = 往工具箱里放工具（on_timer、on_chatter、on_cmd...）
# _init__ = 说明书，告诉你"该怎么用这些工具"