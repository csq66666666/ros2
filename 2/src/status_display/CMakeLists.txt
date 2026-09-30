cmake_minimum_required(VERSION 3.8)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
project(status_display)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(status_interfaces REQUIRED)
find_package(Qt5 REQUIRED COMPONENTS Widgets)

# hello_qt 只用 Qt，不用 ROS 2
add_executable(hello_qt src/hello_qt.cpp)
target_link_libraries(hello_qt Qt5::Widgets)
target_include_directories(hello_qt PRIVATE ${Qt5Widgets_INCLUDE_DIRS})

# sys_status_display 同时用 Qt 和 ROS 2
add_executable(sys_status_display src/sys_status_display.cpp)

# 顺序很关键：先让 ament 设置 ROS 2 依赖，再追加 Qt
ament_target_dependencies(sys_status_display rclcpp status_interfaces)
target_link_libraries(sys_status_display Qt5::Widgets)
target_include_directories(sys_status_display PRIVATE ${Qt5Widgets_INCLUDE_DIRS})

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

install(TARGETS hello_qt sys_status_display DESTINATION lib/${PROJECT_NAME})
ament_package()