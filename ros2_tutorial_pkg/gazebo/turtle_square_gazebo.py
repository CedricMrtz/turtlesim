import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32MultiArray
from nav_msgs.msg import Odometry


class TurtleSquare(Node):
    # Tuning constants (works well with turtlesim's physics)
    LINEAR_SPEED = 1.0  # m/s
    ANGULAR_SPEED = 0.9  # rad/s  (π/2 ÷ ~1.75 s ≈ 90 °)
    SIDE_DURATION = 2.0  # seconds per straight segment
    TURN_DURATION = math.pi / 2.0 / ANGULAR_SPEED  # ≈1.75 s per 90° turn

    def __init__(self):
        super().__init__("turtle_square_gazebo")

        # Scale drive time by requested side length (reference = 2.0 m at SIDE_DURATION)

        self.pose = self.create_subscription(Odometry, "/odom", self._pose_cb, 10)

        self.cmd_pub = self.create_publisher(Twist, "/cmd_vel", 10)

        self.sub = self.create_subscription(
            Float32MultiArray, "/coords", self._calculate_distance_callback, 10
        )

        self._phase = "drive"  # 'drive' | 'turn'
        self._phase_start: float | None = None
        self._sides_done = 0
        self._current_pose = Odometry()

        # Small timer driving the state machine at 20 Hz
        self.create_timer(0.05, self._step)

        # Variables to calculate the trajectory to another point
        self._target_x = 0
        self._target_y = 0
        self._target_distance = None
        self._target_angle = 0

    # ------------------------------------------------------------------
    def _pose_cb(self, msg: Odometry):
        self._current_pose = msg

    def _calculate_distance_callback(self, msg: Float32MultiArray):
        self.get_logger().info(
            f"Received target coordinates: x={msg.data[0]}, y={msg.data[1]}"
        )
        self._target_x = msg.data[0]
        self._target_y = msg.data[1]
        dif_x = self._target_x - self._current_pose.pose.pose.position.x
        dif_y = self._target_y - self._current_pose.pose.pose.position.y
        self._target_distance = math.sqrt(dif_x**2 + dif_y**2)
        self._target_angle = math.atan2(dif_y, dif_x)
        self._phase = "rotate"

    def _step(self):
        if self._target_distance is None:
            return

        now = self.get_clock().now().nanoseconds * 1e-9
        if self._phase_start is None:
            self._phase_start = now

        twist = Twist()

        if self._phase == "rotate":
            current_yaw = self._get_yaw()
            angle_diff = self._target_angle - current_yaw

            angle_diff = math.atan2(math.sin(angle_diff), math.cos(angle_diff))

            if abs(angle_diff) > 0.05:
                twist.angular.z = self.ANGULAR_SPEED * (1.0 if angle_diff > 0 else -1.0)
            else:
                dif_x = self._target_x - self._current_pose.pose.pose.position.x
                dif_y = self._target_y - self._current_pose.pose.pose.position.y
                self._target_distance = math.sqrt(dif_x**2 + dif_y**2)
                self._phase = "drive"
                self._phase_start = now

        elif self._phase == "drive":
            drive_duration = self._target_distance / self.LINEAR_SPEED
            elapsed = now - self._phase_start

            if elapsed < drive_duration:
                twist.linear.x = self.LINEAR_SPEED
            else:
                twist.linear.x = 0.0
                self._phase = "idle"

        elif self._phase == "idle":
            pass

        self.get_logger().info(
            f"Phase: {self._phase}, Target: ({self._target_x:.2f}, {self._target_y:.2f}), "
            f"Current: ({self._current_pose.pose.pose.position.x:.2f}, {self._current_pose.pose.pose.position.y:.2f}), "
            f"Distance to target: {self._target_distance:.2f}"
        )
        self.cmd_pub.publish(twist)

    def _get_yaw(self) -> float:
        q = self._current_pose.pose.pose.orientation
        return math.atan2(2.0 * q.w * q.z, 1.0 - 2.0 * q.z**2)


def main(args=None):
    rclpy.init(args=args)
    node = TurtleSquare()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
