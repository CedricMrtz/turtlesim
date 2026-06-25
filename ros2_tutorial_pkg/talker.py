import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Talker(Node):
    """A simple publisher node that sends 'Hello World' messages."""

    def __init__(self):
        super().__init__('talker')

        # Declare a parameter for the publish rate (Hz)
        self.declare_parameter('publish_rate', 1.0)
        rate = self.get_parameter('publish_rate').get_parameter_value().double_value

        self.publisher_ = self.create_publisher(String, 'chatter', 10)
        self.timer = self.create_timer(1.0 / rate, self.timer_callback)
        self.count = 0
        self.get_logger().info(f'Talker started, publishing at {rate} Hz on /chatter')

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello World: {self.count}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.count += 1


def main(args=None):
    rclpy.init(args=args)
    node = Talker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
