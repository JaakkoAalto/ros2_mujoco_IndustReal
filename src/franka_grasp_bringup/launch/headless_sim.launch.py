import os
import xacro
from launch import LaunchDescription
from launch.actions import OpaqueFunction, LogInfo, RegisterEventHandler
from launch.event_handlers import OnProcessExit, OnProcessStart
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def create_nodes(context):
    # 1. Define paths to the DFKI assets
    mujoco_model_path = "/tmp/mujoco"
    mujoco_model_file = os.path.join(mujoco_model_path, "main.xml")
    
    examples_dir = get_package_share_directory("mujoco_ros2_control_examples")
    core_dir = get_package_share_directory("mujoco_ros2_control")
    
    franka_xacro_filepath = os.path.join(examples_dir, "urdf", "franka", "franka.urdf.xacro")
    ros2_control_params_file = os.path.join(examples_dir, "config", "franka", "franka_controllers.yaml")
    rviz_config_file = os.path.join(examples_dir, "config", "franka", "default.rviz")
    
    # 2. Process the Franka URDF/Xacro
    robot_description_content = xacro.process_file(
        franka_xacro_filepath, 
        mappings={
            "name": "franka", 
            "mujoco": "true",
            "arm_id": "fr3",
            "ee_id": "franka_hand",
            "load_realsense": "true",
            "render_realsense": "true",
            "base_xyz": "-0.308 0 0.875",  # Puts robot ON the table
            "base_rpy": "0 0 0"
        }
    ).toprettyxml(indent=" ")
    
    robot_description = {"robot_description": robot_description_content}

    # Add the table and gears (static assets)
    additional_files = [
        os.path.join(core_dir, "mjcf", "scene.xml"),
        os.path.join(examples_dir, "urdf", "imrk_table", "imrk_table.urdf.xacro"),
        os.path.join(examples_dir, "urdf", "industreal", "industreal_task_board.urdf.xacro")
    ]

    # 3. Define the ROS 2 Nodes
    
    # A. Robot State Publisher (Publishes TF data for RViz)
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[robot_description]
    )

    # B. DFKI URDF to MJCF Converter
    xacro2mjcf = Node(
        package="mujoco_ros2_control",
        executable="xacro2mjcf.py",
        parameters=[
            {"robot_descriptions": [robot_description_content]},
            {"input_files": additional_files},
            {"output_file": mujoco_model_file},
            {"mujoco_files_path": mujoco_model_path},
            {"floating": False},
        ],
    )

    # 3. MuJoCo engine 
    ros2_control_params_file = os.path.join(examples_dir, "config", "franka", "franka_controllers.yaml")
    realsense_params_file = os.path.join(examples_dir, "config", "franka", "realsense_d435.yaml")

    mujoco_node = Node(
        package="mujoco_ros2_control",
        executable="mujoco_ros2_control",
        parameters=[
            robot_description,
            ros2_control_params_file,
            realsense_params_file, # <-- Added Realsense config
            {"simulation_frequency": 500.0},
            {"realtime_factor": 1.0},
            {"robot_model_path": mujoco_model_file},
            {"show_gui": True}, # <-- Keep GUI ON to see physics
        ],
        remappings=[('/controller_manager/robot_description', '/robot_description')]
    )

    # D. Controller Spawners
    load_jsb = Node(
        package="controller_manager", executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )
    load_arm_ctrl = Node(
        package="controller_manager", executable="spawner",
        arguments=[
            "fr3_joint_trajectory_controller", 
            "--controller-manager", "/controller_manager",
            "--param-file", ros2_control_params_file
        ],
    )
    load_hand_ctrl = Node(
        package="controller_manager", executable="spawner",
        arguments=[
            "fr3_franka_hand_joint_trajectory_controller", 
            "--controller-manager", "/controller_manager",
            "--param-file", ros2_control_params_file
        ],
    )

    # E. RViz2 Node
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        output="screen",
        arguments=["-d", rviz_config_file],
    )

    # 4. Define Execution Order (Event Handlers)
    # Don't start MuJoCo until the XML converter is finished
    start_mujoco = RegisterEventHandler(
        OnProcessExit(target_action=xacro2mjcf, on_exit=[LogInfo(msg="XML Created. Starting MuJoCo..."), mujoco_node])
    )
    
    # Don't start controllers until MuJoCo is running
    load_controllers = RegisterEventHandler(
        OnProcessStart(target_action=mujoco_node, on_start=[LogInfo(msg="MuJoCo started. Spawning controllers..."), load_jsb, load_arm_ctrl, load_hand_ctrl])
    )

    return [robot_state_publisher, rviz_node, xacro2mjcf, start_mujoco, load_controllers]

def generate_launch_description():
    return LaunchDescription([OpaqueFunction(function=create_nodes)])