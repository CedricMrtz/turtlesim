"""
launch/talker_listener.launch.py
---------------------------------
Launches both the talker and listener nodes together.

Usage:
  ros2 launch ros2_tutorial_pkg talker_listener.launch.py
  ros2 launch ros2_tutorial_pkg talker_listener.launch.py publish_rate:=2.0
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    publish_rate_arg = DeclareLaunchArgument(
        'publish_rate',
        default_value='1.0',
        description='Rate (Hz) at which the talker publishes messages',
    )

    talker_node = Node(
        package='ros2_tutorial_pkg',
        executable='talker',
        name='talker',
        parameters=[{'publish_rate': LaunchConfiguration('publish_rate')}],
        output='screen',
    )

    listener_node = Node(
        package='ros2_tutorial_pkg',
        executable='listener',
        name='listener',
        output='screen',
    )

    return LaunchDescription([
        publish_rate_arg,
        talker_node,
        listener_node,
    ])
