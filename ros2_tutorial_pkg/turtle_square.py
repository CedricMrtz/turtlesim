import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import TeleportAbsolute, SetPen
from std_msgs.msg import Float32MultiArray


class TurtleSquare(Node):
    """
    Drives the turtle in a square by commanding velocity then checking pose.

    Strategy: publish Twist commands on /turtle1/cmd_vel in a timed loop.
    Each side: drive forward for a set duration, then turn 90° left.
    """

    # Tuning constants (works well with turtlesim's physics)
    LINEAR_SPEED = 1.0  # m/s
    ANGULAR_SPEED = 0.0  # rad/s  (π/2 ÷ ~1.75 s ≈ 90 °)
    SIDE_DURATION = 2.0  # seconds per straight segment
    TURN_DURATION = math.pi / 2.0 / ANGULAR_SPEED  # ≈1.75 s per 90° turn

    def __init__(self):
        super().__init__("turtle_square")

        self.declare_parameter("side_length", 2.0)
        side = self.get_parameter("side_length").get_parameter_value().double_value
        # Scale drive time by requested side length (reference = 2.0 m at SIDE_DURATION)
        self._side_duration = self.SIDE_DURATION * (side / 2.0)

        self.cmd_pub = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        self.pose_sub = self.create_subscription(
            Pose, "/turtle1/pose", self._pose_cb, 10
        )
        self.sub = self.create_subscription(
            Float32MultiArray, "/coords", self._calculate_distance_callback, 10
        )

        self._phase = "drive"  # 'drive' | 'turn'
        self._phase_start: float | None = None
        self._sides_done = 0
        self._current_pose: Pose

        # Small timer driving the state machine at 20 Hz
        self.create_timer(0.05, self._step)
        self.get_logger().info(f"TurtleSquare started — side length ≈ {side} units")

        # Variables to calculate the trajectory to another point
        self._target_x = None
        self._target_y = None
        self._target_distance = None
        self._target_angle = None

    # ------------------------------------------------------------------
    def _pose_cb(self, msg: Pose):
        self._current_pose = msg

    def _calculate_distance_callback(self, msg: Float32MultiArray):
        self._target_x = msg.data[0]
        self._target_y = msg.data[1]
        p = self._current_pose
        dif_x = self._target_x - p.x
        dif_y = self._target_y - p.y
        self._target_distance = math.sqrt(dif_x**2 + dif_y**2)
        self._target_angle = math.atan2(dif_y, dif_x)

    def _step(self):
        if self._target_distance is None:
            return

        now = self.get_clock().now().nanoseconds * 1e-9

        if self._phase_start is None:
            self._phase_start = now

        elapsed = now - self._phase_start
        twist = Twist()

        drive_duration = self._target_distance / self.LINEAR_SPEED

        if self._phase == "drive":
            if elapsed < drive_duration:
                twist.linear.x = self.LINEAR_SPEED
            else:
                self._phase = "turn"
                self._phase_start = now
                self._sides_done += 1
                self.get_logger().info(f"Side {self._sides_done} done — turning 90°")

        elif self._phase == "turn":
            if elapsed < self.TURN_DURATION:
                twist.angular.z = self.ANGULAR_SPEED
            else:
                self._phase = "drive"
                self._phase_start = now

        self.cmd_pub.publish(twist)


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
