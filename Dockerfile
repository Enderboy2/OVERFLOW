FROM ubuntu:18.04

# Install ROS dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    lsb-release

# Setup ROS repository
RUN apt update &&  apt install -y curl gnupg2 lsb-release && curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc |  apt-key add -urces.list.d/ros-latest.list
RUN sh -c 'echo "deb [arch=$(dpkg --print-architecture)] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" > /etc/apt/sources.list.d/ros2-latest.list'
# Install ROS
RUN apt update    
RUN apt install -y ros-eloquent-desktop
RUN apt install -y python3-pip
RUN pip3 install -U argcomplete
# Install dependencies for your application
RUN apt install -y neovim
RUN source /opt/ros/eloquent/setup.bash
# Set up entrypoint
# ENTRYPOINT ["roslaunch", "your_package", "your_launch_file.launch"]
