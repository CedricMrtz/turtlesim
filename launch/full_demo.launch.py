"""
launch/full_demo.launch.py
---------------------------
Launches everything at once: talker/listener pub-sub demo
AND the turtlesim square-driving demo.

Usage:
  ros2 launch ros2_tutorial_pkg full_demo.launch.py
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, LogInfo
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        # ── Arguments ──────────────────────────────────────────────────────
        DeclareLaunchArgument('publish_rate', default_value='1.0',
                              description='Talker publish rate (Hz)'),
        DeclareLaunchArgument('side_length',  default_value='2.0',
                              description='Square side length (turtlesim units)'),
        DeclareLaunchArgument('log_rate',     default_value='2.0',
                              description='Pose logger rate (Hz)'),

        LogInfo(msg='=== ROS 2 Tutorial — Full Demo ==='),

        # ── Pub/Sub demo ───────────────────────────────────────────────────
        Node(
            package='ros2_tutorial_pkg',
            executable='talker',
            name='talker',
            parameters=[{'publish_rate': LaunchConfiguration('publish_rate')}],
            output='screen',
        ),
        Node(
            package='ros2_tutorial_pkg',
            executable='listener',
            name='listener',
            output='screen',
        ),

        # ── TurtleSim demo ─────────────────────────────────────────────────
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim',
            output='screen',
        ),
        Node(
            package='ros2_tutorial_pkg',
            executable='turtle_square',
            name='turtle_square',
            parameters=[{'side_length': LaunchConfiguration('side_length')}],
            output='screen',
        ),
        Node(
            package='ros2_tutorial_pkg',
            executable='turtle_pose_logger',
            name='turtle_pose_logger',
            parameters=[{'log_rate': LaunchConfiguration('log_rate')}],
            output='screen',
        ),
    ])
