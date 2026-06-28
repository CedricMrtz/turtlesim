from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # side_length_arg = DeclareLaunchArgument(
    #     "side_length",
    #     default_value="2.0",
    #     description="Approximate side length of the square (turtlesim units)",
    # )
    #
    # log_rate_arg = DeclareLaunchArgument(
    #     "log_rate",
    #     default_value="2.0",
    #     description="How often (Hz) the pose logger prints turtle position",
    # )
    #
    # turtlesim_node = Node(
    #     package="turtlesim",
    #     executable="turtlesim_node",
    #     name="turtlesim",
    #     output="screen",
    # )

    turtle_square_node = Node(
        package="ros2_tutorial_pkg",
        executable="turtle_square_gazebo",
        name="turtle_square_gazebo",
        output="screen",
    )

    # pose_logger_node = Node(
    #     package="ros2_tutorial_pkg",
    #     executable="turtle_pose_logger",
    #     name="turtle_pose_logger",
    #     parameters=[{"log_rate": LaunchConfiguration("log_rate")}],
    #     output="screen",
    # )
    #
    return LaunchDescription(
        [
            # side_length_arg,
            # log_rate_arg,
            # turtlesim_node,
            turtle_square_node,
            # pose_logger_node,
        ]
    )
