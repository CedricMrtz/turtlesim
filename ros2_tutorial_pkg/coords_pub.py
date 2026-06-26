import re
import threading
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray


class CoordsPub(Node):
    def __init__(self):
        super().__init__("coords_pub")
        self.publisher_ = self.create_publisher(Float32MultiArray, "/coords", 10)

        self._input_thread = threading.Thread(target=self._input_loop, daemon=True)
        self._input_thread.start()

    def _input_loop(self):
        pattern = re.compile(r"x:\s*([-\d.]+)\s+y:\s*([-\d.]+)")

        while rclpy.ok():
            try:
                raw = input("Coordinates: ").strip()
            except EOFError:
                break

            match = pattern.match(raw)
            if not match:
                print("Invalid format: x:1.5 y:2.3")
                continue

            x = float(match.group(1))
            y = float(match.group(2))

            msg = Float32MultiArray()
            msg.data = [x, y]
            self.publisher_.publish(msg)
            self.get_logger().info(f"Published → x={x}, y={y}")


def main(args=None):
    rclpy.init(args=args)
    node = CoordsPub()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
