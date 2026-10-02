import launch
import launch_ros

def generate_launch_description():
    action_node_turtlesim_node=launch_ros.actions.Node(
        package='turtlesim',
        executable='turtlesim_node',
        output='screen',
    )
   
    return launch.LaunchDescription(
        [action_node_turtlesim_node]
    )
