CXX ?= g++
CXXFLAGS ?= -std=c++17 -Wall -Wextra -O3 -Iinclude
LDFLAGS ?= -lcrypto

# Directories
SRC_DIR = src
INC_DIR = include
BUILD_DIR = build
BIN_DIR = bin
TESTS_DIR = tests

# Sources
CORE_SRCS = $(SRC_DIR)/core/file_scanner.cpp \
            $(SRC_DIR)/core/hash_engine.cpp \
            $(SRC_DIR)/core/byte_verifier.cpp \
            $(SRC_DIR)/core/storage_optimizer.cpp \
            $(SRC_DIR)/core/pipeline.cpp

DS_SRCS = $(SRC_DIR)/ds/murmur3.cpp \
          $(SRC_DIR)/ds/bloom_filter.cpp \
          $(SRC_DIR)/ds/hash_table.cpp

UTILS_SRCS = $(SRC_DIR)/utils/logger.cpp \
             $(SRC_DIR)/utils/metrics.cpp \
             $(SRC_DIR)/utils/reporter.cpp

LIB_SRCS = $(CORE_SRCS) $(DS_SRCS) $(UTILS_SRCS)
LIB_OBJS = $(patsubst $(SRC_DIR)/%.cpp, $(BUILD_DIR)/%.o, $(LIB_SRCS))

MAIN_SRC = $(SRC_DIR)/main.cpp
MAIN_OBJ = $(BUILD_DIR)/main.o

TEST_SRCS = $(TESTS_DIR)/test_bloom_filter.cpp \
            $(TESTS_DIR)/test_hash_table.cpp \
            $(TESTS_DIR)/test_verifier_optimizer.cpp \
            $(TESTS_DIR)/test_pipeline.cpp \
            $(TESTS_DIR)/test_runner.cpp
TEST_OBJS = $(patsubst $(TESTS_DIR)/%.cpp, $(BUILD_DIR)/tests/%.o, $(TEST_SRCS))

# Targets
TARGET = $(BIN_DIR)/dedupfs
TEST_TARGET = $(BIN_DIR)/test_runner

.PHONY: all clean test dirs help

all: dirs $(TARGET) $(TEST_TARGET)

help:
	@echo "DedupFS High-Performance Build System"
	@echo "Usage:"
	@echo "  make all       Compile bin/dedupfs and bin/test_runner"
	@echo "  make test      Compile and execute automated test suite"
	@echo "  make clean     Remove build and bin directories"
	@echo "  make help      Show this help message"

dirs:
	@mkdir -p $(BUILD_DIR)/core $(BUILD_DIR)/ds $(BUILD_DIR)/utils $(BUILD_DIR)/tests $(BIN_DIR)

# Compile library objects
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cpp
	@mkdir -p $(dir $@)
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Compile test objects
$(BUILD_DIR)/tests/%.o: $(TESTS_DIR)/%.cpp
	@mkdir -p $(dir $@)
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Link main executable
$(TARGET): dirs $(MAIN_OBJ) $(LIB_OBJS)
	@mkdir -p $(BIN_DIR)
	$(CXX) $(CXXFLAGS) $(MAIN_OBJ) $(LIB_OBJS) -o $@ $(LDFLAGS)
	@echo "\033[1;32m[BUILD SUCCESS] Compiled dedupfs binary -> $(TARGET)\033[0m"

# Link test executable
$(TEST_TARGET): dirs $(TEST_OBJS) $(LIB_OBJS)
	@mkdir -p $(BIN_DIR)
	$(CXX) $(CXXFLAGS) $(TEST_OBJS) $(LIB_OBJS) -o $@ $(LDFLAGS)
	@echo "\033[1;32m[BUILD SUCCESS] Compiled test runner -> $(TEST_TARGET)\033[0m"

test: dirs $(TEST_TARGET)
	@echo "\033[1;34m=== Running DedupFS Automated Test Suite ===\033[0m"
	@$(TEST_TARGET)

clean:
	rm -rf $(BUILD_DIR) $(BIN_DIR)
	@echo "Cleaned build artifacts."
