CC := x86_64-linux-gnu-gcc-12

# Specify the object files
obj-m += spy.o  # Ensure your source file is named hello.c

# Get the current directory
PWD := $(CURDIR)

# Default target to build the module
all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

# Clean target to remove generated files
clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean

