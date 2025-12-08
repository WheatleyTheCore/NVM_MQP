# Define the C compiler
CC = gcc

# Define compiler flags (e.g., -Wall for all warnings, -g for debugging info)
CFLAGS = -Wall -g

# Define the name of the executable
TARGET = main

# Define the source files
SRCS = main.c tinywav.c conv.c

# Automatically generate object file names from source files
OBJS = $(SRCS:.c=.o)

# Default target: builds the executable
all: $(TARGET)

# Rule to link object files into the executable
$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) $(OBJS) -o $(TARGET)

# Rule to compile individual C source files into object files
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Rule for cleaning up generated files
clean:
	rm -f $(OBJS) $(TARGET)