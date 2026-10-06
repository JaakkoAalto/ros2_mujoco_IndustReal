#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint
from builtin_interfaces.msg import Duration

class SimpleMover(Node):
    def __init__(self):
        super().__init__('simple_mover')
        # Create an action client to talk to the trajectory controller
        self._action_client = ActionClient(
            self, 
            FollowJointTrajectory, 
            '/fr3_joint_trajectory_controller/follow_joint_trajectory'
        )

    def send_goal(self):
        self.get_logger().info('Waiting for trajectory controller action server...')
        self._action_client.wait_for_server()

        # Create the trajectory message
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory.joint_names = [
            'fr3_joint1', 'fr3_joint2', 'fr3_joint3', 
            'fr3_joint4', 'fr3_joint5', 'fr3_joint6', 'fr3_joint7'
        ]

        # Define a dramatically different target point
        # J1 (base) swings to 0.8, J2 (shoulder) drops forward to 0.4, J4 (elbow) extends to -1.0
        point = JointTrajectoryPoint()
        point.positions = [0.8, 0.4, 0.0, -1.0, 0.0, 2.0, 0.0]
        
        # Tell the controller to take exactly 8.0 seconds to reach this point
        point.time_from_start = Duration(sec=8, nanosec=0)

        goal_msg.trajectory.points.append(point)

        self.get_logger().info('Sending robot motion command...')
        self._action_client.send_goal_async(goal_msg)

def main(args=None):
    rclpy.init(args=args)
    mover = SimpleMover()
    mover.send_goal()
    
    # Keep the node alive while the action executes
    try:
        rclpy.spin(mover)
    except KeyboardInterrupt:
        pass
    finally:
        mover.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()