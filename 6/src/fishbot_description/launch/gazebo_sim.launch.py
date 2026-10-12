# ============================================================================
# 教程 6.4.2：在 Gazebo 中加载机器人模型
# ============================================================================
#
# 【这一章要解决什么】
#   URDF 是 ROS 用的机器人描述格式，Gazebo 内部用的是 SDF，两者不是一回事，
#   所以不能把 URDF 直接丢给 Gazebo。
#
#   好在 gazebo_ros 提供了 spawn_entity.py：它订阅 /robot_description 话题拿到
#   xacro 展开后的 URDF，在内部完成 URDF -> SDF 的转换，再调用 Gazebo 的
#   /spawn_entity 服务把机器人生成到场景里。
#   这就是"ROS 2 提供的功能包帮我们直接实现转换"的具体落点。
#
# 【本文件一共做三件事】
#   1. robot_state_publisher —— 把 URDF 发布到 /robot_description，同时算 TF
#   2. 启动 Gazebo          —— 加载 custom_room.world 作为仿真场景
#   3. spawn_entity.py      —— 把机器人真正"生成"进 Gazebo
#
# 【运行方式】
#   ros2 launch fishbot_description gazebo_sim.launch.py
#
# 【和 display_robot.launch.py 的区别】
#   display_robot.launch.py 是纯 RViz 可视化：用 joint_state_publisher 手动
#   模拟关节状态，不涉及物理仿真；本文件则把模型交给 Gazebo，并且不再需要
#   joint_state_publisher —— 关节状态由 Gazebo 自己发布。
#
# 【注意】
#   本文件对应教程 6.4.2（把模型加载进来）。
#   教程最新版还额外包含 3 个 ros2_control 控制器的加载动作，那属于 6.5 章
#   （让机器人动起来）的内容，需要 URDF 里有 <ros2_control> 标签、
#   config/ros2_controllers.yaml，以及安装 gazebo_ros2_control。
#   这三样你现在都还没有，照抄那部分会直接报
#   "Loader for controller 'fishbot_diff_drive_controller' not found"。
# ============================================================================

# 导入 launch 核心库，用于构建启动描述
import launch
# 导入 launch_ros，用于启动 ROS 2 节点
import launch_ros
# 用于获取指定功能包的 share 目录路径
from ament_index_python.packages import get_package_share_directory
# 用于在 launch 文件里 include 另一个 python launch 文件
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    # ============ 1. 定位文件路径 ============
    # 生成到 Gazebo 里的实体名，会显示在 Gazebo 左侧 World 面板中
    robot_name_in_model = "fishbot"

    # 功能包安装后的 share 目录
    # 注意：这里读的是 install/ 下的副本，不是 src/ 下的源文件，
    # 所以改了 urdf 或 world 之后要重新 colcon build 才会生效
    urdf_tutorial_path = get_package_share_directory('fishbot_description')

    default_model_path = urdf_tutorial_path + '/urdf/fishbot/fishbot.urdf.xacro'
    default_world_path = urdf_tutorial_path + '/world/custom_room.world'

    # ============ 2. 声明 model 参数 ============
    # 和 display_robot.launch.py 一样，允许用户用 model:=xxx 覆盖默认模型
    action_declare_arg_mode_path = launch.actions.DeclareLaunchArgument(
        name='model', default_value=str(default_model_path),
        description='URDF 的绝对路径')

    # ============ 3. 用 xacro 展开 URDF ============
    # 相当于在终端执行 `xacro <model>`，把展开后的完整 URDF 文本
    # 作为 robot_description 参数的值；value_type=str 是必须的，
    # 否则 Command 的输出会被当成其它类型导致参数设置失败
    robot_description = launch_ros.parameter_descriptions.ParameterValue(
        launch.substitutions.Command(
            ['xacro ', launch.substitutions.LaunchConfiguration('model')]),
        value_type=str)

    # ============ 4. robot_state_publisher 节点 ============
    # 它做两件事：
    #   a) 根据 URDF 和关节状态算出各连杆的 TF 变换
    #   b) 把 URDF 内容发布到 /robot_description 话题 —— 下面的 spawn_entity
    #      就是从这个话题取模型去转换成 SDF 的，所以它必须在 spawn 之前启动
    robot_state_publisher_node = launch_ros.actions.Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}]
    )

    # ============ 5. 启动 Gazebo ============
    # gazebo_ros 自带 gazebo.launch.py（它内部再分别拉起 gzserver 和 gzclient），
    # 直接 IncludeLaunchDescription 进来复用即可，不用自己写 gzserver/gzclient。
    # 通过 launch_arguments 传两件事进去：
    #   world   —— 指定要加载的世界文件，不传会用 Gazebo 自带的空世界
    #   verbose —— 打印详细日志，调试时很有用
    launch_gazebo = launch.actions.IncludeLaunchDescription(
        PythonLaunchDescriptionSource([get_package_share_directory(
            'gazebo_ros'), '/launch', '/gazebo.launch.py']),
        launch_arguments=[('world', default_world_path), ('verbose', 'true')]
    )

    # ============ 6. 把机器人生成到 Gazebo 里 ============
    # spawn_entity.py 的两个关键参数：
    #   -topic  /robot_description  从哪个话题拿 URDF 描述
    #   -entity fishbot             生成后实体的名字
    #
    # 关于启动顺序：它虽然和 Gazebo 几乎同时启动，但内部有
    # client.wait_for_service(timeout_sec=30)，会一直等 Gazebo 的
    # /spawn_entity 服务就绪，所以这里不需要额外加 TimerAction 延时
    spawn_entity_node = launch_ros.actions.Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', '/robot_description',
                   '-entity', robot_name_in_model, ]
    )

    # ============ 7. 组装 LaunchDescription ============
    # 顺序有意义：先发布 robot_description，再起 Gazebo，最后 spawn
    # 才有东西可读、有服务可调
    return launch.LaunchDescription([
        action_declare_arg_mode_path,        # 声明 model 参数
        robot_state_publisher_node,          # 发布 URDF + 算 TF
        launch_gazebo,                       # 启动 gzserver + gzclient
        spawn_entity_node,                   # URDF -> SDF 并生成到场景中
    ])
