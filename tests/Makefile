# Makefile for building and testing vector programs with CVA6+ARA
# This makefile helps compile vector test programs and verify vector instruction generation

# Default configuration
RISCV_PREFIX ?= riscv64-unknown-elf-
CC = $(RISCV_PREFIX)gcc
OBJDUMP = $(RISCV_PREFIX)objdump
READELF = $(RISCV_PREFIX)readelf

# Vector-enabled compilation flags
VECTOR_CFLAGS = -march=rv64gcv -mabi=lp64d
OPTIMIZATION_FLAGS = -O2 -ftree-vectorize -ffast-math
VECTOR_FLAGS = -mrvv-vector-bits=scalable

# All flags combined
CFLAGS = $(VECTOR_CFLAGS) $(OPTIMIZATION_FLAGS) $(VECTOR_FLAGS)
CFLAGS += -static -mcmodel=medany -fvisibility=hidden -nostdlib -nostartfiles

# Test programs
VECTOR_TESTS = vector_test
TEST_SOURCES = vector_test.c

# Build rules
.PHONY: all clean check-toolchain compile-tests analyze-vector help

all: check-toolchain compile-tests analyze-vector

# Check if RISC-V toolchain is available
check-toolchain:
	@which $(CC) > /dev/null || (echo "Error: RISC-V toolchain not found. Please install riscv64-unknown-elf-gcc" && exit 1)
	@echo "RISC-V toolchain found: $(shell $(CC) --version | head -1)"
	@$(CC) -march=rv64gcv -E -dM - < /dev/null | grep -q "__riscv_vector" || \
		(echo "Warning: Toolchain may not support RISC-V vector extensions" && exit 1)
	@echo "Vector extension support detected in toolchain"

# Compile test programs
compile-tests: $(VECTOR_TESTS)

vector_test: vector_test.c
	@echo "Compiling $@ with vector support..."
	$(CC) $(CFLAGS) -o $@ $<
	@echo "Generating assembly listing..."
	$(CC) $(CFLAGS) -S -o $@.s $<
	@echo "Generating object dump..."
	$(OBJDUMP) -d $@ > $@.objdump

# Analyze vector instruction generation
analyze-vector: vector_test
	@echo "=== Vector Instruction Analysis ==="
	@echo "Looking for vector instructions in assembly output:"
	@echo ""
	@echo "Vector configuration instructions:"
	@grep -n "vsetvl" vector_test.s || echo "  No vsetvl instructions found"
	@echo ""
	@echo "Vector load/store instructions:"
	@grep -n -E "vle|vse" vector_test.s || echo "  No vector load/store instructions found"
	@echo ""
	@echo "Vector arithmetic instructions:"
	@grep -n -E "vfadd|vadd|vsub|vmul" vector_test.s || echo "  No vector arithmetic instructions found"
	@echo ""
	@echo "Vector instruction summary:"
	@grep -c -E "vsetvl|vle|vse|vfadd|vadd|vsub|vmul" vector_test.s || echo "0"
	@echo "vector instructions found in total"

# Check specific vector opcodes in object file
check-opcodes: vector_test
	@echo "=== Vector Opcode Analysis ==="
	@echo "Looking for vector instruction opcodes in object file:"
	@echo "Vector arithmetic opcodes (0x57):"
	@$(OBJDUMP) -d vector_test | grep -c " 57" || echo "0 found"
	@echo "Vector load opcodes (0x07):"
	@$(OBJDUMP) -d vector_test | grep -c " 07" || echo "0 found"
	@echo "Vector store opcodes (0x27):"
	@$(OBJDUMP) -d vector_test | grep -c " 27" || echo "0 found"

# Generate detailed analysis report
report: vector_test
	@echo "=== CVA6+ARA Vector Test Report ===" > vector_analysis_report.txt
	@echo "Generated on: $(shell date)" >> vector_analysis_report.txt
	@echo "" >> vector_analysis_report.txt
	@echo "Toolchain Information:" >> vector_analysis_report.txt
	@$(CC) --version >> vector_analysis_report.txt
	@echo "" >> vector_analysis_report.txt
	@echo "Compilation Flags:" >> vector_analysis_report.txt
	@echo "$(CFLAGS)" >> vector_analysis_report.txt
	@echo "" >> vector_analysis_report.txt
	@echo "Vector Instructions Found:" >> vector_analysis_report.txt
	@grep -n -E "vsetvl|vle|vse|vfadd|vadd|vsub|vmul" vector_test.s >> vector_analysis_report.txt || echo "No vector instructions found" >> vector_analysis_report.txt
	@echo "" >> vector_analysis_report.txt
	@echo "Object File Analysis:" >> vector_analysis_report.txt
	@$(OBJDUMP) -d vector_test | grep -E " 57| 07| 27" >> vector_analysis_report.txt || echo "No vector opcodes found" >> vector_analysis_report.txt
	@echo "Report generated: vector_analysis_report.txt"

# Clean build artifacts
clean:
	rm -f $(VECTOR_TESTS) *.s *.objdump *.txt *.o

# Help target
help:
	@echo "CVA6+ARA Vector Test Makefile"
	@echo "=============================="
	@echo ""
	@echo "Targets:"
	@echo "  all              - Build and analyze all vector tests"
	@echo "  check-toolchain  - Verify RISC-V vector toolchain"
	@echo "  compile-tests    - Compile all vector test programs"
	@echo "  analyze-vector   - Analyze generated vector instructions"
	@echo "  check-opcodes    - Check for vector opcodes in object file"
	@echo "  report           - Generate detailed analysis report"
	@echo "  clean            - Clean all build artifacts"
	@echo "  help             - Show this help message"
	@echo ""
	@echo "Variables:"
	@echo "  RISCV_PREFIX     - RISC-V toolchain prefix (default: riscv64-unknown-elf-)"
	@echo ""
	@echo "Example usage:"
	@echo "  make all                           # Build and analyze"
	@echo "  make RISCV_PREFIX=riscv64-linux-  # Use different toolchain"
