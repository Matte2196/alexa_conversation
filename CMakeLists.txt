cmake_minimum_required(VERSION 3.0.2)
project(alexa_conversation)

add_compile_options(-std=c++17)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  sensor_msgs
  tf2
  tf2_ros
)

## Generate messages in the 'msg' folder
# add_message_files(
#   FILES
#   Message1.msg
#   Message2.msg
# )

## Generate services in the 'srv' folder
# add_service_files(
#   FILES
#   Service1.srv
#   Service2.srv
# )

## Generate actions in the 'action' folder
# add_action_files(
#   FILES
#   Action1.action
#   Action2.action
# )

## Generate added messages and services with any dependencies listed here
# generate_messages(
#   DEPENDENCIES
#   std_msgs  # Or other packages containing msgs
# )

catkin_package(
#  INCLUDE_DIRS include
#  LIBRARIES alexa_conversation
 CATKIN_DEPENDS 
  rospy
  std_msgs
  sensor_msgs
  tf2
  tf2_ros
  ur_speed_control
#  DEPENDS system_lib
)

###########
## Build ##
###########

include_directories(
# include
  ${catkin_INCLUDE_DIRS}
)

#############
## Install ##
#############

install(
  PROGRAMS
	script/postreq.py
	script/conversation.py
  DESTINATION
  	${CATKIN_PACKAGE_PYTHON_DESTINATION}
)
