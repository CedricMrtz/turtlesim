import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose


class TurtlePoseLogger(Node):
    """
    Subscribes to /turtle1/pose and logs position & heading at a
    configurable interval so the terminal isn't flooded (turtlesim
    publishes pose at ~62 Hz).
    """

    def __init__(self):
        super().__init__('turtle_pose_logger')

        self.declare_parameter('log_rate', 2.0)   # Hz
        rate = self.get_parameter('log_rate').get_parameter_value().double_value

        self._latest_pose: Pose | None = None

        self.create_subscription(Pose, '/turtle1/pose', self._pose_cb, 10)
        self.create_timer(1.0 / rate, self._log_pose)

        self.get_logger().info(
            f'TurtlePoseLogger started — logging at {rate} Hz')

    def _pose_cb(self, msg: Pose):
        self._latest_pose = msg

    def _log_pose(self):
        if self._latest_pose is None:
            self.get_logger().info('Waiting for first pose message…')
            return
        p = self._latest_pose
        self.get_logger().info(
            f'Pose → x={p.x:.3f}  y={p.y:.3f}  θ={p.theta:.3f} rad  '
            f'speed={p.linear_velocity:.3f} m/s')


def main(args=None):
    rclpy.init(args=args)
    node = TurtlePoseLogger()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
