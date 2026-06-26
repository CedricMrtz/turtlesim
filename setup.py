from setuptools import find_packages, setup
import os
from glob import glob

package_name = "ros2_tutorial_pkg"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        # Required for ament to find the package
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        # package.xml
        ("share/" + package_name, ["package.xml"]),
        # Launch files
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Your Name",
    maintainer_email="you@example.com",
    description="Beginner ROS 2 Humble tutorial package",
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "talker            = ros2_tutorial_pkg.talker:main",
            "listener          = ros2_tutorial_pkg.listener:main",
            "turtle_square     = ros2_tutorial_pkg.turtle_square:main",
            "turtle_pose_logger= ros2_tutorial_pkg.turtle_pose_logger:main",
            "coords_pub        = ros2_tutorial_pkg.coords_pub:main",
            "move_robot        = ros2_tutorial_pkg.gazebo.move:main",
        ],
    },
)
