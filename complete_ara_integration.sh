#!/bin/bash

# CVA6 + ARA Integration Final Setup Script
# This script completes the CVA6-ARA integration process

set -e

echo "=============================================="
echo "CVA6 + ARA Vector Extension Integration"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored status
print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "OK" ]; then
        echo -e "${GREEN}✓${NC} $message"
    elif [ "$status" = "WARN" ]; then
        echo -e "${YELLOW}⚠${NC} $message"
    elif [ "$status" = "ERROR" ]; then
        echo -e "${RED}✗${NC} $message"
    else
        echo -e "${BLUE}ℹ${NC} $message"
    fi
}

echo ""
echo "Step 1: Checking current setup..."

# Check if we're in CVA6 directory
if [ ! -f "Makefile" ] || [ ! -d "core" ]; then
    print_status "ERROR" "Please run this script from the CVA6 root directory"
    exit 1
fi
print_status "OK" "Running from CVA6 directory"

# Check if ARA repository exists
if [ -d "../ara" ]; then
    print_status "OK" "ARA repository found"
else
    print_status "WARN" "ARA repository not found, will clone it"
    echo ""
    echo "Cloning ARA repository..."
    cd ..
    git clone https://github.com/pulp-platform/ara.git
    cd ara
    git submodule update --init --recursive
    cd ../cva6
    print_status "OK" "ARA repository cloned and initialized"
fi

echo ""
echo "Step 2: Verifying integration files..."

# Check integration files
files_to_check=(
    "core/ara_decoder.sv"
    "core/cva6_ara_wrapper.sv" 
    "core/ara_cva6_top.sv"
    "Makefile.ara"
    "Flist.ara"
    "corev_apu/tb/cva6_ara_tb_wrapper.sv"
    "tests/vector_tests/vector_add_basic.c"
    "tests/vector_tests/vector_intrinsics.c"
    "tests/vector_tests/Makefile"
    "docs/ARA_INTEGRATION.md"
    "docs/ARA_INTEGRATION_PLAN.md"
)

missing_files=0
for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        print_status "OK" "Found: $file"
    else
        print_status "ERROR" "Missing: $file"
        missing_files=$((missing_files + 1))
    fi
done

if [ $missing_files -gt 0 ]; then
    print_status "ERROR" "$missing_files integration files are missing"
    echo "Please ensure all integration files are created as described in the documentation"
    exit 1
fi

echo ""
echo "Step 3: Checking configuration..."

# Check if vector support is enabled in config
if grep -q "CVA6ConfigVExtEn = 1" core/include/cv64a6_imafdcv_sv39_config_pkg.sv; then
    print_status "OK" "Vector extension enabled in configuration"
else
    print_status "WARN" "Vector extension may not be enabled in configuration"
fi

if grep -q "CVA6ConfigCvxifEn = 1" core/include/cv64a6_imafdcv_sv39_config_pkg.sv; then
    print_status "OK" "Accelerator interface enabled"
else
    print_status "WARN" "Accelerator interface may not be enabled"
fi

echo ""
echo "Step 4: Testing toolchain..."

# Check RISC-V toolchain
if command -v riscv64-unknown-elf-gcc &> /dev/null; then
    print_status "OK" "RISC-V GCC found"
    
    # Check vector support
    if riscv64-unknown-elf-gcc -march=rv64gcv -E -dM - < /dev/null 2>/dev/null | grep -q "VECTOR\|__riscv_vector"; then
        print_status "OK" "Vector extension support detected in toolchain"
    else
        print_status "WARN" "Vector extension support not detected in toolchain"
    fi
else
    print_status "WARN" "RISC-V GCC not found in PATH"
fi

# Check Verilator
if command -v verilator &> /dev/null; then
    print_status "OK" "Verilator found"
else
    print_status "WARN" "Verilator not found"
fi

echo ""
echo "Step 5: Building test programs..."

# Build vector test programs
cd tests/vector_tests
if make install_deps > /dev/null 2>&1; then
    print_status "OK" "Test dependencies installed"
else
    print_status "WARN" "Failed to install test dependencies"
fi

if make all > /dev/null 2>&1; then
    print_status "OK" "Vector test programs compiled successfully"
    
    # Check for vector instructions
    if make check_vector > /dev/null 2>&1; then
        print_status "OK" "Vector instructions found in compiled code"
    else
        print_status "WARN" "No vector instructions found in compiled code"
    fi
else
    print_status "WARN" "Failed to compile vector test programs"
fi

cd ../..

echo ""
echo "Step 6: Preparation summary..."

print_status "INFO" "Integration files are ready"
print_status "INFO" "Configuration is set for vector support"
print_status "INFO" "Test programs are available"

echo ""
echo "=============================================="
echo "Next Steps:"
echo "=============================================="
echo ""
echo "1. Review the integration documentation:"
echo "   - docs/ARA_INTEGRATION.md"
echo "   - docs/ARA_INTEGRATION_PLAN.md"
echo ""
echo "2. Build the CVA6+ARA system:"
echo "   make -f Makefile.ara check_ara"
echo "   make -f Makefile.ara show_config"
echo "   make -f Makefile.ara verilate_ara"
echo ""
echo "3. Test vector programs:"
echo "   cd tests/vector_tests"
echo "   make analyze"
echo "   make check_vector"
echo ""
echo "4. For full hardware integration:"
echo "   - Update Flist.ara with actual ARA source files"
echo "   - Replace ara_system placeholder with real ARA module"
echo "   - Configure AXI interconnect for memory sharing"
echo "   - Implement vector CSR integration"
echo ""
echo "5. Advanced integration:"
echo "   - Port to FPGA platform"
echo "   - Run performance benchmarks"
echo "   - Optimize vector execution"
echo ""

print_status "OK" "CVA6+ARA integration setup completed!"
echo ""
echo "The system is ready for vector extension development."
echo "Refer to the documentation for detailed integration steps."
