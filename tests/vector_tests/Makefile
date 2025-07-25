# Makefile for CVA6+ARA Vector Tests
# Compiles and runs vector extension tests

# Toolchain configuration
RISCV_PREFIX ?= /home/vedant/riscv/bin/riscv-none-elf-
CC = $(RISCV_PREFIX)gcc
OBJDUMP = $(RISCV_PREFIX)objdump
OBJCOPY = $(RISCV_PREFIX)objcopy

# Compilation flags for vector extension
CFLAGS = -march=rv64gcv
CFLAGS += -mabi=lp64d
CFLAGS += -static
CFLAGS += -mcmodel=medany
CFLAGS += -fvisibility=hidden
CFLAGS += -nostdlib
CFLAGS += -nostartfiles
CFLAGS += -O2
CFLAGS += -g

# Include directories
INCLUDES = -I$(CURDIR)/../common
INCLUDES += -I$(RISCV_PREFIX)/../include

# Linker script and startup
LDSCRIPT = $(CURDIR)/../common/test.ld
STARTUP = $(CURDIR)/../common/crt0.S

# Test programs
TESTS = vector_add_basic
TESTS += vector_intrinsics

# Generated files
ELFS = $(TESTS:%=%.elf)
DUMPS = $(TESTS:%=%.dump)
BINS = $(TESTS:%=%.bin)

# Default target
.PHONY: all clean dump analyze help

all: $(ELFS)

help:
	@echo "CVA6+ARA Vector Tests"
	@echo "===================="
	@echo ""
	@echo "Available targets:"
	@echo "  all       - Build all test programs"
	@echo "  dump      - Generate disassembly dumps"
	@echo "  analyze   - Analyze vector instruction usage"
	@echo "  clean     - Clean build artifacts"
	@echo ""
	@echo "Test programs:"
	@$(foreach test,$(TESTS),echo "  $(test)";)

# Build individual test programs
%.elf: %.c $(STARTUP) $(LDSCRIPT)
	@echo "Building vector test: $@"
	$(CC) $(CFLAGS) $(INCLUDES) -T$(LDSCRIPT) -o $@ $(STARTUP) $<

# Generate disassembly
%.dump: %.elf
	@echo "Generating disassembly: $@"
	$(OBJDUMP) -D $< > $@

# Generate binary
%.bin: %.elf
	@echo "Generating binary: $@"
	$(OBJCOPY) -O binary $< $@

# Generate all disassemblies
dump: $(DUMPS)

# Analyze vector instruction usage in compiled code
analyze: $(DUMPS)
	@echo "Analyzing vector instruction usage..."
	@echo "====================================="
	@for dump in $(DUMPS); do \
		echo ""; \
		echo "File: $$dump"; \
		echo "Vector load instructions:"; \
		grep -c "vl[0-9].*\.v" $$dump || echo "  None found"; \
		echo "Vector store instructions:"; \
		grep -c "vs[0-9].*\.v" $$dump || echo "  None found"; \
		echo "Vector arithmetic instructions:"; \
		grep -c "v[a-z]*\.v[vxi]" $$dump || echo "  None found"; \
		echo "Vector configuration instructions:"; \
		grep -c "vset[vl]" $$dump || echo "  None found"; \
	done

# Check if vector instructions are present
check_vector: $(DUMPS)
	@echo "Checking for vector instructions in compiled code..."
	@found=0; \
	for dump in $(DUMPS); do \
		if grep -q "vl.*\.v\|vs.*\.v\|v[a-z]*\.v[vxi]\|vset" $$dump; then \
			echo "✓ Vector instructions found in $$dump"; \
			found=1; \
		else \
			echo "✗ No vector instructions found in $$dump"; \
		fi; \
	done; \
	if [ $$found -eq 1 ]; then \
		echo "Vector compilation successful!"; \
	else \
		echo "Warning: No vector instructions found. Check toolchain and flags."; \
	fi

# Show compilation info
info:
	@echo "Vector Test Compilation Info"
	@echo "============================"
	@echo "Compiler: $(CC)"
	@echo "Flags: $(CFLAGS)"
	@echo "Target arch: rv64gcv (RISC-V 64-bit with vector extension)"
	@echo "ABI: lp64d (64-bit long and pointer, double precision float)"
	@echo ""
	@$(CC) --version 2>/dev/null || echo "Compiler not found"
	@echo ""
	@echo "Vector extension support:"
	@$(CC) -march=rv64gcv -E -dM - < /dev/null 2>/dev/null | grep -i vector || echo "  No vector macros found"

# Clean build artifacts
clean:
	@echo "Cleaning vector test artifacts..."
	@rm -f $(ELFS) $(DUMPS) $(BINS)
	@rm -f *.o *.a

# Install test dependencies (startup code and linker script)
install_deps:
	@echo "Installing test dependencies..."
	@mkdir -p ../common
	@if [ ! -f "../common/crt0.S" ]; then \
		echo "Creating basic startup code..."; \
		echo "# Basic startup code for RISC-V tests" > ../common/crt0.S; \
		echo ".global _start" >> ../common/crt0.S; \
		echo "_start:" >> ../common/crt0.S; \
		echo "    la sp, _stack_top" >> ../common/crt0.S; \
		echo "    call main" >> ../common/crt0.S; \
		echo "    li a0, 0" >> ../common/crt0.S; \
		echo "    li a7, 93  # exit syscall" >> ../common/crt0.S; \
		echo "    ecall" >> ../common/crt0.S; \
	fi
	@if [ ! -f "../common/test.ld" ]; then \
		echo "Creating basic linker script..."; \
		cat > ../common/test.ld << 'EOF' ;\
OUTPUT_ARCH(riscv) ;\
ENTRY(_start) ;\
MEMORY { \
  RAM : ORIGIN = 0x80000000, LENGTH = 64M \
} ;\
SECTIONS { \
  .text : { *(.text*) } > RAM ;\
  .data : { *(.data*) } > RAM ;\
  .bss  : { *(.bss*) } > RAM ;\
  _stack_top = ORIGIN(RAM) + LENGTH(RAM) ;\
} ;\
EOF \
	fi

# Build everything including dependencies
full_build: install_deps all dump analyze check_vector

# Test individual programs (for simulation)
test_%: %.elf
	@echo "Test program ready: $<"
	@echo "Load this ELF file in your CVA6+ARA simulation"
	@echo "Entry point: $$($(OBJDUMP) -f $< | grep 'start address' | cut -d' ' -f3)"
