cmake_minimum_required(VERSION 3.16)
project(DedupFS VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Compiler flags
add_compile_options(-Wall -Wextra -Wpedantic -O3)

# OpenSSL dependency
find_package(OpenSSL REQUIRED)

include_directories(include)

# Library sources
set(LIB_SOURCES
    src/core/file_scanner.cpp
    src/core/hash_engine.cpp
    src/core/byte_verifier.cpp
    src/core/storage_optimizer.cpp
    src/core/pipeline.cpp
    src/ds/murmur3.cpp
    src/ds/bloom_filter.cpp
    src/ds/hash_table.cpp
    src/utils/logger.cpp
    src/utils/metrics.cpp
    src/utils/reporter.cpp
)

add_library(dedupfs_core STATIC ${LIB_SOURCES})
target_link_libraries(dedupfs_core PUBLIC OpenSSL::Crypto)

# Main executable
add_executable(dedupfs src/main.cpp)
target_link_libraries(dedupfs PRIVATE dedupfs_core)

# Test executable
set(TEST_SOURCES
    tests/test_bloom_filter.cpp
    tests/test_hash_table.cpp
    tests/test_verifier_optimizer.cpp
    tests/test_pipeline.cpp
    tests/test_runner.cpp
)

add_executable(test_runner ${TEST_SOURCES})
target_link_libraries(test_runner PRIVATE dedupfs_core)

enable_testing()
add_test(NAME DedupFSTests COMMAND test_runner)
