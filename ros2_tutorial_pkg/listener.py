import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Listener(Node):
    """A simple subscriber node that receives messages from the talker."""

    def __init__(self):
        super().__init__('listener')
        self.subscription = self.create_subscription(
            String,
            'chatter',
            self.listener_callback,
            10,
        )
        self.get_logger().info('Listener started, waiting for messages on /chatter...')

    def listener_callback(self, msg: String):
        self.get_logger().info(f'I heard: "{msg.data}"')


def main(args=None):
    rclpy.init(args=args)
    node = Listener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
