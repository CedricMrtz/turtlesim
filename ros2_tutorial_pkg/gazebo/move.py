import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class MoveRobot(Node):
    def __init__(self):
        super().__init__("move_robot")
        self.pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.timer = self.create_timer(0.1, self.loop)

    def loop(self):
        msg = Twist()
        msg.linear.x = 0.2
        msg.angular.z = 0.0
        self.pub.publish(msg)


rclpy.init()
node = MoveRobot()
rclpy.spin(node)
