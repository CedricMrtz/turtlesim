import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import TeleportAbsolute, SetPen


class TurtleSquare(Node):
    """
    Drives the turtle in a square by commanding velocity then checking pose.

    Strategy: publish Twist commands on /turtle1/cmd_vel in a timed loop.
    Each side: drive forward for a set duration, then turn 90° left.
    """

    # Tuning constants (works well with turtlesim's physics)
    LINEAR_SPEED = 1.0   # m/s
    ANGULAR_SPEED = 0.9  # rad/s  (π/2 ÷ ~1.75 s ≈ 90 °)
    SIDE_DURATION = 2.0  # seconds per straight segment
    TURN_DURATION = math.pi / 2.0 / ANGULAR_SPEED  # ≈1.75 s per 90° turn

    def __init__(self):
        super().__init__('turtle_square')

        self.declare_parameter('side_length', 2.0)
        side = self.get_parameter('side_length').get_parameter_value().double_value
        # Scale drive time by requested side length (reference = 2.0 m at SIDE_DURATION)
        self._side_duration = self.SIDE_DURATION * (side / 2.0)

        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pose_sub = self.create_subscription(
            Pose, '/turtle1/pose', self._pose_cb, 10)

        self._phase = 'drive'   # 'drive' | 'turn'
        self._phase_start: float | None = None
        self._sides_done = 0
        self._current_pose: Pose | None = None

        # Small timer driving the state machine at 20 Hz
        self.create_timer(0.05, self._step)
        self.get_logger().info(
            f'TurtleSquare started — side length ≈ {side} units')

    # ------------------------------------------------------------------
    def _pose_cb(self, msg: Pose):
        self._current_pose = msg

    def _step(self):
        now = self.get_clock().now().nanoseconds * 1e-9

        if self._phase_start is None:
            self._phase_start = now

        elapsed = now - self._phase_start
        twist = Twist()

        if self._phase == 'drive':
            if elapsed < self._side_duration:
                twist.linear.x = self.LINEAR_SPEED
            else:
                self._phase = 'turn'
                self._phase_start = now
                self._sides_done += 1
                self.get_logger().info(
                    f'Side {self._sides_done} done — turning 90°')

        elif self._phase == 'turn':
            if elapsed < self.TURN_DURATION:
                twist.angular.z = self.ANGULAR_SPEED
            else:
                self._phase = 'drive'
                self._phase_start = now
                if self._sides_done % 4 == 0:
                    self.get_logger().info(
                        f'Square #{self._sides_done // 4} complete!')

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


if __name__ == '__main__':
    main()
