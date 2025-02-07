# Compiler and flags
CC=gcc
CXX=g++
CFLAGS=-std=c99 -O0 -g
CXXFLAGS=-g -pthread -O0

# Directories
SRC_DIR=src
BIN_DIR=bin

# Sources and objects
UTILS_SRC=$(SRC_DIR)/utils.c
EVICTION_SRC=$(SRC_DIR)/eviction.c
TEST_SRC=$(SRC_DIR)/test.c
VICTIM_SRC=$(SRC_DIR)/victim.c
L3PP_SRC=$(SRC_DIR)/l3pp.c

UTILS_OBJ=$(BIN_DIR)/utils.o
EVICTION_OBJ=$(BIN_DIR)/eviction.o
TEST_OBJ=$(BIN_DIR)/test.o
VICTIM_OBJ=$(BIN_DIR)/victim.o
L3PP_OBJ=$(BIN_DIR)/l3pp.o

# Targets
TEST_OUT=$(BIN_DIR)/test.out
VICTIM_OUT=$(BIN_DIR)/victim.out

# Default target
all: $(TEST_OUT) $(VICTIM_OUT)

# Rules for object files
$(UTILS_OBJ): $(UTILS_SRC)
	$(CC) $(CFLAGS) -c $< -o $@

$(EVICTION_OBJ): $(EVICTION_SRC)
	$(CC) $(CFLAGS) -pthread -c $< -o $@

$(TEST_OBJ): $(TEST_SRC)
	$(CC) $(CFLAGS) -c $< -o $@

$(VICTIM_OBJ): $(VICTIM_SRC)
	$(CC) $(CFLAGS) -c $< -o $@

$(L3PP_OBJ): $(L3PP_SRC)
	$(CC) $(CFLAGS) -c $< -o $@


# Rules for executables
$(TEST_OUT): $(TEST_OBJ) $(EVICTION_OBJ) $(UTILS_OBJ) $(L3PP_OBJ)
	$(CXX) $(CXXFLAGS) $^ -o $@

$(VICTIM_OUT): $(VICTIM_OBJ) $(EVICTION_OBJ) $(UTILS_OBJ) $(L3PP_OBJ)
	$(CXX) $(CXXFLAGS) $^ -o $@

# Clean rule
clean:
	rm -f $(BIN_DIR)/*.o $(BIN_DIR)/*.out

