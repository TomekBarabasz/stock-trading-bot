cmake_minimum_required(VERSION 3.15)
project(my_cpp_python_module LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Fetch pybind11
include(FetchContent)
FetchContent_Declare(
    pybind11
    GIT_REPOSITORY https://github.com/pybind/pybind11.git
    GIT_TAG v2.12.0  # You can adjust the version
)
FetchContent_MakeAvailable(pybind11)

# Define the Python module target
pybind11_add_module(wis wis_module.cpp)

target_compile_options(wis PRIVATE -O3)

# (Optional) If you have other C++ source files
# target_sources(wis PRIVATE src/other.cpp)

# Link other libraries if needed
# target_link_libraries(wis PRIVATE your_other_library)
