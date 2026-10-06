#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from ultralytics import YOLO
import cv2

class YoloDetector(Node):
    def __init__(self):
        super().__init__('yolo_detector')
        
        # In the DFKI example, the camera topic is usually /realsense_d435/image_raw or similar.
        # We will map it based on what their Xacro exports. Let's start with a general guess.
        self.subscription = self.create_subscription(
            Image,
            '/d435/color/image_raw', # Adjusted to RViz2 topic
            self.image_callback,
            10
        )
        self.publisher = self.create_publisher(Image, '/yolo/detections', 10)
        
        self.bridge = CvBridge()
        self.model = YOLO('yolov8n.pt') # Downloads the nano model on first run
        
        self.get_logger().info('YOLO Detector Node Started.')

    def image_callback(self, msg):
        try:
            # Convert ROS Image to OpenCV format (BGR8 for YOLO)
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            
            # Run YOLO inference
            results = self.model(cv_image, verbose=False)
            
            # Draw bounding boxes on the image
            annotated_frame = results[0].plot()
            
            # Publish the annotated image back to ROS so you can view it in RViz2
            annotated_msg = self.bridge.cv2_to_imgmsg(annotated_frame, "bgr8")
            annotated_msg.header = msg.header
            self.publisher.publish(annotated_msg)
            
            # For grasping, you would extract bounding box centers here:
            # for box in results[0].boxes:
            #     x_center = int((box.xyxy[0][0] + box.xyxy[0][2]) / 2)
            #     y_center = int((box.xyxy[0][1] + box.xyxy[0][3]) / 2)
            
        except Exception as e:
            self.get_logger().error(f"Error processing image: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = YoloDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()