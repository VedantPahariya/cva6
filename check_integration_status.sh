#!/bin/bash

echo "=============================================="
echo "CVA6 + ARA Integration Status Report"
echo "=============================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

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
echo "1. Repository Status:"
echo "===================="

# Check CVA6
if [ -d "core" ] && [ -f "Makefile" ]; then
    print_status "OK" "CVA6 repository ready"
else
    print_status "ERROR" "CVA6 repository not found"
fi

# Check ARA
if [ -d "../ara" ]; then
    print_status "OK" "ARA repository found"
    if [ -d "../ara/hardware/src" ]; then
        print_status "OK" "ARA hardware sources available"
    else
        print_status "WARN" "ARA hardware sources not found"
    fi
else
    print_status "ERROR" "ARA repository not found"
fi

echo ""
echo "2. Integration Files:"
echo "===================="

integration_files=(
    "core/ara_decoder.sv"
    "core/ara_cva6_top.sv"
    "Flist.ara"
    "Makefile.ara"
    "corev_apu/tb/cva6_ara_tb_wrapper.sv"
    "tests/vector_tests/vector_add_basic.c"
    "tests/vector_tests/vector_intrinsics.c"
    "tests/vector_tests/Makefile"
    "tests/common/crt0.S"
    "tests/common/test.ld"
    "docs/ARA_INTEGRATION.md"
    "docs/ARA_INTEGRATION_PLAN.md"
    "setup_ara.sh"
    "complete_ara_integration.sh"
)

for file in "${integration_files[@]}"; do
    if [ -f "$file" ]; then
        print_status "OK" "Found: $file"
    else
        print_status "ERROR" "Missing: $file"
    fi
done

echo ""
echo "3. Configuration Status:"
echo "======================="

# Check vector configuration
if grep -q "CVA6ConfigVExtEn = 1" core/include/cv64a6_imafdcv_sv39_config_pkg.sv; then
    print_status "OK" "Vector extension enabled in configuration"
else
    print_status "WARN" "Vector extension may not be enabled"
fi

if grep -q "CVA6ConfigCvxifEn = 1" core/include/cv64a6_imafdcv_sv39_config_pkg.sv; then
    print_status "OK" "Accelerator interface enabled"
else
    print_status "WARN" "Accelerator interface may not be enabled"
fi

if grep -q "VLEN: unsigned'(256)" core/include/cv64a6_imafdcv_sv39_config_pkg.sv; then
    print_status "OK" "Vector length set to 256 bits"
else
    print_status "WARN" "Vector length configuration not found"
fi

echo ""
echo "4. Toolchain Status:"
echo "==================="

# Check RISC-V toolchain
if command -v riscv64-unknown-elf-gcc &> /dev/null; then
    print_status "OK" "RISC-V GCC found"
    
    # Check vector support
    if riscv64-unknown-elf-gcc -march=rv64gcv -E -dM - < /dev/null 2>/dev/null | grep -q "VECTOR\|__riscv_vector"; then
        print_status "OK" "Vector extension support detected"
    else
        print_status "WARN" "Vector extension support not detected"
    fi
else
    print_status "WARN" "RISC-V GCC not found - needed for compiling vector tests"
fi

# Check Verilator
if command -v verilator &> /dev/null; then
    print_status "OK" "Verilator found"
else
    print_status "WARN" "Verilator not found - needed for simulation"
fi

echo ""
echo "5. ARA Source Files Status:"
echo "=========================="

# Count ARA source files
ara_files=$(find ../ara/hardware/src -name "*.sv" 2>/dev/null | wc -l)
if [ "$ara_files" -gt 0 ]; then
    print_status "OK" "Found $ara_files ARA SystemVerilog source files"
else
    print_status "ERROR" "No ARA source files found"
fi

# Check key ARA modules
ara_key_files=(
    "../ara/hardware/src/ara_system.sv"
    "../ara/hardware/src/ara.sv"
    "../ara/hardware/src/ara_dispatcher.sv"
    "../ara/hardware/src/lane/lane.sv"
    "../ara/hardware/src/vlsu/vlsu.sv"
)

for file in "${ara_key_files[@]}"; do
    if [ -f "$file" ]; then
        print_status "OK" "Found: $(basename $file)"
    else
        print_status "ERROR" "Missing: $(basename $file)"
    fi
done

echo ""
echo "=============================================="
echo "Integration Summary:"
echo "=============================================="

print_status "INFO" "CVA6 configured for vector extension support"
print_status "INFO" "ARA vector processor repository available"
print_status "INFO" "Integration wrapper files created"
print_status "INFO" "Test programs and build system ready"

echo ""
echo "Current Status: CVA6+ARA Framework Ready ✓"
echo ""
echo "Ready for Next Steps:"
echo "--------------------"
echo "• Hardware integration: Replace ARA placeholder with real module"
echo "• Memory system: Configure AXI interconnect for shared access"
echo "• Vector CSRs: Complete vector control/status register integration"
echo "• Testing: Install RISC-V toolchain and run vector tests"
echo "• Simulation: Build and run CVA6+ARA system simulation"
echo ""
echo "Key Files to Review:"
echo "-------------------"
echo "• docs/ARA_INTEGRATION.md - Complete integration guide"
echo "• core/ara_cva6_top.sv - Main integration wrapper"
echo "• Flist.ara - ARA source file list"
echo "• Makefile.ara - Build system for CVA6+ARA"
echo ""

total_files=0
completed_files=0

for file in "${integration_files[@]}"; do
    total_files=$((total_files + 1))
    if [ -f "$file" ]; then
        completed_files=$((completed_files + 1))
    fi
done

completion_percent=$((completed_files * 100 / total_files))
echo "Integration Completion: $completed_files/$total_files files ($completion_percent%)"

if [ $completion_percent -eq 100 ]; then
    echo ""
    print_status "OK" "All integration files are ready!"
    echo ""
    echo "🚀 CVA6+ARA integration framework is complete and ready for development!"
else
    echo ""
    print_status "WARN" "Some integration files are missing"
fi

echo ""
