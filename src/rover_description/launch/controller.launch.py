from launch import LaunchDescription
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.descriptions import ParameterValue
import launch
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import LaunchConfiguration
from launch.actions import ExecuteProcess
from launch.actions import SetEnvironmentVariable
from launch_ros.actions import Node

from launch_ros.actions import Node
from launch.actions import TimerAction

from os.path import join
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import GroupAction, DeclareLaunchArgument
from controller_manager.launch_utils import generate_load_controller_launch_description

import os
def generate_launch_description():
    description_file = LaunchConfiguration("description_file", default="suyo.urdf.xacro")
    use_sim_time = LaunchConfiguration("use_sim_time", default="true")

    robot_description_content = Command([
        PathJoinSubstitution([FindExecutable(name="xacro")]),
        " ",
        PathJoinSubstitution([
            FindPackageShare("rover_description"),
            "robots",
            description_file
        ]),
    ])
    pkg_share_folder = get_package_share_directory('rover_description')

    os.environ["GZ_SIM_SYSTEM_PLUGIN_PATH"] = (
        os.environ.get("GZ_SIM_SYSTEM_PLUGIN_PATH", "") +
        ":/opt/ros/jazzy/lib"
    )

    # Load joint state broadcaster controller
    joint_state_broadcaster = GroupAction(
        [
            generate_load_controller_launch_description(
            controller_name='joint_state_broadcaster',
            controller_params_file=join(
            pkg_share_folder, 'config', 'rover_controllers.yaml'))
        ],
    )
    # Load rover controller
    base_controller = GroupAction(
        [
        generate_load_controller_launch_description(
            controller_name='rover_base_control',
            controller_params_file=join(
            pkg_share_folder, 'config', 'rover_controllers.yaml')
        )
        ],
    )
    arm_pkg_share_folder = get_package_share_directory('rover_moveit_config')

    # Load arm controller
    arm_controller = GroupAction(
        [
            generate_load_controller_launch_description(
                controller_name='scara_controller',
                controller_params_file=join(
                    arm_pkg_share_folder, 'config', 'ros2_controllers.yaml'
                )
            ),
        ],
    )

    # Load gripper controller
    gripper_controller = GroupAction(
        [
            generate_load_controller_launch_description(
                controller_name='gripper_controller',
                controller_params_file=join(
                    arm_pkg_share_folder, 'config', 'ros2_controllers.yaml'
                )
            ),
        ],
    )


    return LaunchDescription([

        base_controller,
        joint_state_broadcaster,
        arm_controller,
        gripper_controller,
    ])