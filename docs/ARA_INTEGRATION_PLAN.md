# CVA6 + ARA Vector Extension Integration Guide

## Overview
This guide provides step-by-step instructions to integrate ARA (Arithmetic Research Unit) vector processor with CVA6 scalar core to enable RISC-V vector extension support.

## Prerequisites
- CVA6 repository already cloned and configured
- RISC-V toolchain installed
- Verilator or ModelSim/QuestaSim for simulation
- Basic understanding of RISC-V vector extensions

## Current Status
✅ CVA6 vector extension support is **ENABLED** in configuration
✅ Vector instruction decoder infrastructure exists
✅ Accelerator interface is available
❌ ARA vector unit is **NOT INTEGRATED**

## Step-by-Step Integration Plan

### Step 1: Clone and Setup ARA Repository

```bash
# Navigate to your project directory
cd /home/vedant/Desktop/Summer_Project/

# Clone ARA repository
git clone https://github.com/pulp-platform/ara.git
cd ara

# Initialize submodules
git submodule update --init --recursive

# Check ARA structure
ls -la
```

### Step 2: Verify CVA6 Vector Configuration

The CVA6 configuration already has vector support enabled:
- `CVA6ConfigVExtEn = 1` ✅
- `RVV: bit'(CVA6ConfigVExtEn)` ✅
- Vector Length (VLEN): 64 bits (configurable)

### Step 3: Update CVA6 Configuration for ARA

Edit `/home/vedant/Desktop/Summer_Project/cva6/core/include/cv64a6_imafdcv_sv39_config_pkg.sv`:

```systemverilog
// Update VLEN to match ARA's vector length (typically 128, 256, or 512)
VLEN: unsigned'(256),  // Change from 64 to match ARA configuration

// Enable accelerator interface
CvxifEn: bit'(1),  // Change from 0 to 1
CoproType: config_pkg::COPRO_CVXIF,  // Change from COPRO_NONE
```

### Step 4: Create ARA-CVA6 Integration Wrapper

Create a new file: `/home/vedant/Desktop/Summer_Project/cva6/core/ara_cva6_top.sv`

### Step 5: Update CVA6 Filelist

Add ARA sources to CVA6 build:
- Create `Flist.ara` containing all ARA source files
- Update main CVA6 Makefile to include ARA sources
- Set up proper include paths

### Step 6: Modify CVA6 Decoder

Replace the vector instruction decoder stub with actual ARA integration:
- Update `cva6_accel_first_pass_decoder_stub.sv`
- Connect vector instructions to ARA unit
- Handle vector CSR operations

### Step 7: Memory System Integration

Configure shared memory between CVA6 and ARA:
- Set up AXI interconnect for vector memory operations
- Configure cache coherency
- Set up vector load/store unit interface

### Step 8: Vector Register File Integration

Connect ARA's vector register file:
- Set up vector register file interface
- Handle vector-scalar register file interactions
- Configure vector CSR registers

### Step 9: Create Build System

Set up compilation flow:
- Create Makefile for CVA6+ARA
- Set up simulation targets
- Configure synthesis flow (if needed)

### Step 10: Testing and Validation

Create test programs:
- Simple vector arithmetic tests
- Vector memory operation tests
- Mixed scalar-vector programs
- Performance benchmarks

## Directory Structure After Integration

```
/home/vedant/Desktop/Summer_Project/
├── cva6/                           # CVA6 scalar core
│   ├── core/
│   │   ├── ara_cva6_top.sv        # Integration wrapper
│   │   ├── ara_decoder.sv          # Vector instruction decoder
│   │   └── ...
│   ├── Flist.ara                   # ARA source files list
│   ├── Makefile.ara               # CVA6+ARA build system
│   └── ...
├── ara/                            # ARA vector processor
│   ├── hardware/
│   ├── apps/
│   └── ...
└── tests/                          # Integration tests
    ├── vector_basic/
    ├── vector_memory/
    └── benchmarks/
```

## Next Steps

1. Start with Step 1 (Clone ARA)
2. Follow steps sequentially
3. Test each integration step
4. Run validation tests
5. Optimize performance

## Troubleshooting

- **Compilation errors**: Check include paths and file lists
- **Simulation hangs**: Verify clock and reset connections
- **Vector instructions fail**: Check decoder and CSR setup
- **Memory errors**: Verify AXI interconnect configuration

## Performance Optimization

- Configure optimal VLEN for your workload
- Tune cache parameters
- Optimize interconnect bandwidth
- Profile vector instruction performance

## Additional Resources

- ARA Documentation: https://github.com/pulp-platform/ara
- RISC-V Vector Specification: https://github.com/riscv/riscv-v-spec
- CVA6 Documentation: In `docs/` directory
