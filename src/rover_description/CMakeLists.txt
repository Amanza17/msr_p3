cmake_minimum_required(VERSION 3.8)
project(rover_description)

# Buscar dependencias de ROS 2
find_package(ament_cmake REQUIRED)

# Instalar directorios de recursos
install(
  DIRECTORY
    config
    launch
    meshes
    robots
    rviz
    urdf
  DESTINATION share/${PROJECT_NAME}
)

# En ROS 2 es vital registrar el paquete en el index para que comandos como 
# 'ros2 launch' o 'ros2 run' encuentren los archivos.
ament_package()