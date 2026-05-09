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
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
import os
def generate_launch_description():
    description_file = LaunchConfiguration("description_file", default="robot.urdf.xacro")
    use_sim_time = LaunchConfiguration("use_sim_time", default="false")

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


    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            # Clock
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",

            # Cámaras FRONT
            #"/front_camera/image@sensor_msgs/msg/Image@gz.msgs.Image",
            #"/front_camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo",

            # Cámaras ARM
            #"/arm_camera/image@sensor_msgs/msg/Image@gz.msgs.Image",
            #"/arm_camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo",

            # IMU
            "/imu@sensor_msgs/msg/Imu@gz.msgs.IMU",

            # Pose global (muy útil para debug / odometría)
            "/world/urjc_excavation_world/pose/info@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V",
        ],
        output="screen"
    )

    gz_image_bridge_node = Node(
        package='ros_gz_image',
        executable='image_bridge',
        arguments=[
            '/front_camera/image',
            '/arm_camera/image'
        ],
        output='screen',
        parameters=[
            {
                'use_sim_time': True,
                'camera.image.compressed.jpeg_quality': 75,
            },
        ],
    )


    robot_description = {
        "robot_description": ParameterValue(robot_description_content, value_type=str),
        "use_sim_time": use_sim_time,
    }

    joint_state_publisher_node = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        name="joint_state_publisher_gui",
        output="screen",
        parameters=[robot_description],
    )
    
    robot_description_launcher = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("rover_moveit_config"),
                "launch",
                "rsp.launch.py"
            ])
        )
    )
    
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[robot_description],
    )
    # Spawning robot
    gazebo_spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=[
            "-model", "rover",
            "-topic", "robot_description",
            "-use_sim_time", "True",
        ],
    )
    urjc_excavation = launch.actions.IncludeLaunchDescription(
        launch.launch_description_sources.PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('urjc_excavation_world'),
                'launch',
                'urjc_excavation_msr.launch.py')))
    
    rviz_config = PathJoinSubstitution([
        FindPackageShare("rover_description"),
        "rviz",
        "robot.rviz"
    ])

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_config],
        parameters=[{"use_sim_time": True}] 
    )

        # Twist stamped
    twist_stamped = Node(
        package="twist_stamper",
        executable="twist_stamper",
        name="twist_stamper",
        output="screen",
        parameters=[
            {
                "use_sim_time": True,
            }
        ],
        remappings=[
            ("cmd_vel_out", "/rover_base_control/cmd_vel"),
            ("cmd_vel_in", "/cmd_vel"),
        ],
    )


    return LaunchDescription([
        #joint_state_publisher_node,
        robot_state_publisher_node,
        rviz_node,
        gazebo_spawn_robot,
        urjc_excavation,
        bridge,
        twist_stamped,
        robot_description_launcher,
        gz_image_bridge_node,
    ])