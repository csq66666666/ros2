# 导入 launch 核心库，用于构建启动描述
import launch
# 导入 launch_ros，用于启动 ROS 2 节点
import launch_ros
# 用于获取指定功能包的 share 目录路径
from ament_index_python.packages import get_package_share_directory
# 导入 os 模块，用于拼接文件路径
import os


def generate_launch_description():
    # ============ 1. 定位 URDF 模型文件 ============
    # 获取 fishbot_description 功能包的 share 目录路径
    urdf_package_path = get_package_share_directory('fishbot_description')
    # 拼接出 fishbot.urdf 文件的完整路径
    urdf_path = os.path.join(urdf_package_path, 'urdf', 'first_robot.urdf')
    default_rviz_config_path= os.path.join(urdf_package_path, 'config', 'display_robot_model.rviz')
    # ============ 2. 声明启动参数 ============
    # 声明一个名为 "model" 的启动参数，默认值为上面拼好的 urdf 路径
    # 这样用户可以在启动时通过 model:=xxx 覆盖默认模型文件
    action_declear_arg_mode_path = launch.actions.DeclareLaunchArgument(
        name='model',
        default_value=urdf_path,
        description='加载的模型文件路径'
    )

    # ============ 3. 读取 URDF 文件内容 ============
    # 使用 Command 替代执行 shell 命令 "cat <model路径>"
    # 目的是把 URDF 文件内容读出来作为 robot_description 参数的值
    substitutions_command_result = launch.substitutions.Command(
        ['xacro ', launch.substitutions.LaunchConfiguration('model')]
    )
    # 将命令输出包装为参数值，并指定类型为字符串（str）
    # 因为 Command 的输出默认是文本，但需要显式声明类型供 ROS 参数使用
    robot_description_value = launch_ros.parameter_descriptions.ParameterValue(
        substitutions_command_result, value_type=str
    )

    # ============ 4. 启动 robot_state_publisher 节点 ============
    # 该节点根据 robot_description（URDF）和关节状态，发布各个连杆的 TF 变换
    action_robot_state_publisher = launch_ros.actions.Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description_value}]
    )

    # ============ 5. 启动 joint_state_publisher 节点 ============
    # 该节点发布关节状态（joint_states），让 robot_state_publisher 能计算出 TF
    # 在这里没有额外参数，默认会从 URDF 中读取关节并发布（无 GUI 版本）
    action_joint_state_publisher = launch_ros.actions.Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
    )

    # ============ 6. 启动 RViz2 可视化节点 ============
    # 用于可视化机器人模型、TF、传感器数据等
    action_rviz_node = launch_ros.actions.Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', default_rviz_config_path]
    )

    # ============ 7. 返回 LaunchDescription ============
    # 将上面声明的参数、各个动作按顺序放入启动描述中
    # launch 系统会依次执行它们
    return launch.LaunchDescription([
        action_declear_arg_mode_path,      # 声明 model 参数
        action_robot_state_publisher,       # 启动 robot_state_publisher
        action_joint_state_publisher,       # 启动 joint_state_publisher
        action_rviz_node                   # 启动 rviz2
    ])