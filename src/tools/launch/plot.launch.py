from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess, DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression

def generate_launch_description():

    output_dir = LaunchConfiguration('output_dir')

    return LaunchDescription([

        DeclareLaunchArgument(
            'output_dir',
            default_value='.',
            description='Directorio donde guardar los CSV.'
        ),

        Node(
            package='tools',
            executable='data_analyzer',
            output='screen',
            parameters=[
                {'output_dir': output_dir},
                {"use_sim_time": True},
            ],
        ),

    ])
