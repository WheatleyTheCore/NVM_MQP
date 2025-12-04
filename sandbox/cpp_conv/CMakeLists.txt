cmake_minimum_required(VERSION 3.10)
project(convolutionHell)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

file (COPY src/c2.wav DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
file (COPY src/ir.wav DESTINATION ${CMAKE_CURRENT_BINARY_DIR})

# ---------------------------------------------------------
# Header-only library: AudioFile
# ---------------------------------------------------------
add_library(AudioFile INTERFACE)
target_include_directories(AudioFile INTERFACE
    ${CMAKE_SOURCE_DIR}/external_libs/AudioFile
)

# ---------------------------------------------------------
# Static library: FFTConvolver
# ---------------------------------------------------------
add_library(FFTConvolver
    external_libs/FFTConvolver/FFTConvolver.cpp
    external_libs/FFTConvolver/AudioFFT.cpp
    external_libs/FFTConvolver/TwoStageFFTConvolver.cpp
    external_libs/FFTConvolver/Utilities.cpp
)

target_include_directories(FFTConvolver PUBLIC
    ${CMAKE_SOURCE_DIR}/external_libs/FFTConvolver
)

# Optional: enable SSE optimizations
# target_compile_definitions(FFTConvolver PUBLIC FFTCONVOLVER_USE_SSE)

# ---------------------------------------------------------
# Your executable
# ---------------------------------------------------------
add_executable(convolutionHell src/main.cpp)

target_link_libraries(convolutionHell
    PRIVATE
        AudioFile
        FFTConvolver
)
