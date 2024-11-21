# Compiler and flags
CC = gcc
CFLAGS = -std=gnu99 -O0 -g -Wall -Wextra
LDFLAGS = -lm -pthread

# Directories
BIN_DIR = bin
LIB_DIR = lib
SRC_DIR = src

# Source and object files
SRC = $(wildcard $(LIB_DIR)/*.c) $(wildcard $(SRC_DIR)/*.c)
OBJ = $(patsubst %.c, $(BIN_DIR)/%.o, $(notdir $(SRC)))

# Target executable
TARGET = $(BIN_DIR)/spy_pp.out

# Default rule
all: $(BIN_DIR) $(TARGET)

# Ensure bin directory exists
$(BIN_DIR):
	mkdir -p $(BIN_DIR)

# Build the target executable
$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)

# Compile source files
$(BIN_DIR)/%.o: $(LIB_DIR)/%.c | $(BIN_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(BIN_DIR)/%.o: $(SRC_DIR)/%.c | $(BIN_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

# Clean up build artifacts
clean:
	rm -rf $(BIN_DIR)

# Run the executable
run: all
	./$(TARGET)

# Phony targets
.PHONY: all clean run

