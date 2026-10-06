# Franka Vision-Based Grasping Simulation

This project provides a production-grade, containerized grasping simulation for the Franka Emika Panda arm. It integrates the MuJoCo physics engine with ROS 2 Jazzy, utilizing MoveIt 2 for motion planning and YOLOv8 for object detection and pose estimation. The simulation environment features the official NVIDIA IndustReal gears task board, sourced directly from the DFKI-RIC **[mujoco_ros2_control](https://github.com/dfki-ric/mujoco_ros2_control):** repository.

## Motivation and scope
The core objective of this project is to bridge the gap between simulation and physical deployment. By developing and testing machine vision pipelines in a high-fidelity physics environment, this repository serves as a proving ground for algorithms intended for real-world industrial applications. The architecture is deliberately designed to be hardware-agnostic, ensuring the vision and planning pipelines can be deployed to both Franka and Universal Robots (UR) platforms with minimal configuration changes.

The entire environment is fully Dockerized to make the project transferable and easily deployable with minimal dependency issues, while retaining native GPU passthrough and X11 GUI forwarding for RViz2 and MuJoCo.

## 🛠️ Tech Stack
* **OS:** Ubuntu 24.04 (via Docker)
* **Middleware:** ROS 2 Jazzy Jalisco
* **Physics:** MuJoCo (`mujoco_ros2_control`)
* **Vision:** YOLOv8, OpenCV
* **Planning:** MoveIt 2

## 🚀 Quick Start

### 1. Clone the Repository
Because this project relies on submodules, clone it recursively:

```bash
git clone --recursive [https://github.com/JaakkoAalto/franka_mujoco_gears.git](https://github.com/JaakkoAalto/franka_mujoco_gears.git)
cd franka_mujoco_gears
```

### 2. Pull Git LFS Meshes
The MuJoCo simulation relies on high-quality .stl meshes stored via Git Large File System (LFS). You must pull these to prevent MuJoCo from crashing on startup:

```bash
cd src/dfki_mujoco
git lfs install
git lfs pull
cd ../..
```


### 3. Build and Start the Docker container
Ensure Docker is running and allow local GUI connections:
```bash
xhost +local:docker
docker compose up -d --build
```

### 4. Build the ROS 2 workspace
Enter the container and build the custom packages:
```bash
docker exec -it franka_grasp_sim bash
cd /ros2_ws
rosdep update
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
```

### 5. Run the Simulation
In the container, launch the MuJoCo physics engine and RViz2:
```bash
source install/setup.bash
ros2 launch franka_grasp_bringup headless_sim.launch.py
```

In a separate terminal, test the arm's motion:
```bash
source install/setup.bash
ros2 run franka_grasp_bringup simple_mover
```

## 📜 Acknowledgments
This project is built upon the work of the open-source robotics community. Special credits to:

* **[DFKI-RIC](https://github.com/dfki-ric/mujoco_ros2_control):** For their robust `mujoco_ros2_control` framework and `mujoco_ros2_control_examples` which power the core physics integration.
* **[Franka Robotics](https://github.com/frankarobotics/franka_description):** For the official URDFs and kinematic descriptions of the Franka Emika Panda arm.
* **[Universal Robots](https://github.com/UniversalRobots/Universal_Robots_ROS2_Description):** For future integration paths built into this repository structure.