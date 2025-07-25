# CVA6 + ARA Integration Guide

## Overview

This document provides a complete guide for integrating the ARA vector processor with the CVA6 scalar core to enable RISC-V vector extension (RVV) support.

## Current Status

✅ **CVA6 Configuration**: Vector extension support is enabled
✅ **Integration Framework**: Core integration files created
✅ **Test Infrastructure**: Vector test programs ready
❌ **ARA Repository**: Not yet cloned and integrated
❌ **Full Integration**: Hardware integration pending

## Quick Start

### 1. Setup ARA Repository

```bash
# Navigate to your project directory
cd /home/vedant/Desktop/Summer_Project

# Clone ARA repository
git clone https://github.com/pulp-platform/ara.git
cd ara
git submodule update --init --recursive

# Return to CVA6 directory
cd ../cva6
```

### 2. Run Setup Script

```bash
# Make setup script executable and run it
chmod +x setup_ara.sh
./setup_ara.sh
```

### 3. Build CVA6+ARA System

```bash
# Build with ARA integration
make -f Makefile.ara check_ara     # Verify setup
make -f Makefile.ara show_config   # Show configuration
make -f Makefile.ara verilate_ara  # Build system
```

### 4. Compile and Test Vector Programs

```bash
# Build vector test programs
cd tests/vector_tests
make full_build

# Analyze vector instruction generation
make check_vector
```

### 4. Build RISC-V Toolchain with Vector Support

```bash
cd cva6/util/toolchain-builder/
./build-toolchain.sh --with-arch=rv64gcv --with-abi=lp64d
```

### 5. Test Vector Instruction Generation

```bash
cd tests/
make check-toolchain  # Verify toolchain supports vectors
make compile-tests     # Compile vector test programs
make analyze-vector    # Check if vector instructions are generated
```

Expected output should show vector instructions like:
- `vsetvli` - Vector configuration
- `vle32.v` - Vector load
- `vse32.v` - Vector store  
- `vfadd.vv` - Vector floating-point add

### 6. Complete ARA Integration (Future Steps)

To complete the full integration with actual ARA hardware:

1. **Include ARA Sources**: Add ARA SystemVerilog files to the build
2. **Connect Interfaces**: Wire CVA6's accelerator interface to ARA's scalar interface
3. **Memory Interface**: Connect ARA's memory interface to the system bus
4. **Vector Register File**: Integrate ARA's vector register file
5. **Control Integration**: Connect vector CSRs between CVA6 and ARA

### 7. Simulation and Testing

```bash
# Build CVA6 with ARA integration
make -f Makefile.ara build-ara-integrated

# Run vector tests
make -f Makefile.ara test-vector
```

## Current Integration Status

### ✅ Completed
- CVA6 vector configuration enabled
- Vector instruction decoder implemented
- Integration wrapper created
- Test programs with vector intrinsics
- Build system configuration

### 🔄 In Progress / Future Work
- Full ARA hardware integration
- Memory interface connection
- Vector register file integration
- Complete system testing
- Performance optimization

## Vector Instruction Verification

### Method 1: Assembly Analysis
```bash
riscv64-unknown-elf-gcc -march=rv64gcv -S vector_test.c
grep -E "vsetvl|vle|vse|vfadd" vector_test.s
```

### Method 2: Object Code Analysis
```bash
riscv64-unknown-elf-objdump -d vector_test.o | grep -E " 57"  # Vector arithmetic
riscv64-unknown-elf-objdump -d vector_test.o | grep -E " 07"  # Vector loads
riscv64-unknown-elf-objdump -d vector_test.o | grep -E " 27"  # Vector stores
```

### Method 3: Simulation with RVFI
Enable RVFI in CVA6 simulation to trace vector instruction execution.

## Troubleshooting

### Common Issues

1. **No Vector Instructions Generated**
   - Check toolchain supports `rv64gcv`
   - Verify compilation flags include `-march=rv64gcv`
   - Enable optimization (`-O2` or higher)

2. **Vector Instructions Not Decoded**
   - Verify `CVA6ConfigVExtEn = 1` in configuration
   - Check vector decoder implementation
   - Ensure vector status register (vs) is not Off

3. **ARA Integration Issues**
   - Verify ARA repository is properly cloned
   - Check interface compatibility between CVA6 and ARA
   - Ensure memory interfaces are properly connected

## Next Steps

1. **Complete ARA Integration**: Follow ARA documentation to integrate the full vector unit
2. **System Testing**: Run comprehensive vector benchmarks
3. **Performance Analysis**: Compare vector vs scalar performance
4. **Optimization**: Tune the integration for performance and area

## References

- [CVA6 Repository](https://github.com/openhwgroup/cva6)
- [ARA Repository](https://github.com/pulp-platform/ara)
- [RISC-V Vector Extension Specification](https://github.com/riscv/riscv-v-spec)
- [CVA6 Documentation](https://docs.openhwgroup.org/projects/cva6-user-manual/)

## Contact

For questions about this integration, refer to:
- CVA6 documentation and GitHub issues
- ARA documentation and community
- OpenHW Group forums
