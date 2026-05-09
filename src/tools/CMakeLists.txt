cmake_minimum_required(VERSION 3.8)
project(tools)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)

add_executable(data_analyzer src/data_analyzer.cpp)
ament_target_dependencies(data_analyzer rclcpp geometry_msgs sensor_msgs)

install(TARGETS
  data_analyzer
  DESTINATION lib/${PROJECT_NAME}
)

install(PROGRAMS
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
