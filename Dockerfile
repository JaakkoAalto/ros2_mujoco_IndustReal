FROM osrf/ros:jazzy-desktop

# Install core system and graphical dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3-pip \
    libglfw3-dev \
    libx11-dev \
    xorg-dev \
    libwayland-dev \
    libxkbcommon-dev \
    wayland-protocols \
    extra-cmake-modules \
    libopencv-dev \
    # ROS 2 Jazzy Packages, MoveIt2, Control and RealSense camera
    ros-jazzy-urdf \
    ros-jazzy-xacro \
    ros-jazzy-rviz2 \
    ros-jazzy-ros2-control \
    ros-jazzy-ros2-controllers \
    ros-jazzy-controller-manager \
    ros-jazzy-moveit \
    ros-jazzy-pcl-ros \
    ros-jazzy-perception-pcl \
    ros-jazzy-urdfdom-py \
    ros-jazzy-cv-bridge \
    ros-jazzy-realsense2-description \
    && rm -rf /var/lib/apt/lists/*

# NOTE: Franka assets are managed in the git repo and added as volume mounts!
# RUN git clone -b jazzy https://github.com/frankarobotics/franka_description.git /ros2_ws/src/franka_description

# Python dependencies for YOLO with fast uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
# Issue with ROS2 (Ubuntu/apt) and PIP with numpy: ROS2 needs np 1.26.4 but YOLO wants newest, use ROS2 req.
RUN uv pip install --system --break-system-packages "numpy==1.26.4" ultralytics opencv-python

WORKDIR /ros2_ws

# Automatic ROS sourcing in the container
RUN echo "source /opt/ros/jazzy/setup.bash" >> /root/.bashrc
RUN echo "if [ -f /ros2_ws/install/setup.bash ]; then source /ros2_ws/install/setup.bash; fi" >> /root/.bashrc