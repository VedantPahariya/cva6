# CVA6 Performance Analysis Tools Guide

This guide explains how to use the advanced performance analysis tools (`debug_model.py` and `perf_analysis.py`) to analyze CVA6 processor performance and obtain detailed execution metrics.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Tool 1: debug_model.py - Detailed Scoreboard Analysis](#tool-1-debug_modelpy---detailed-scoreboard-analysis)
- [Tool 2: perf_analysis.py - Complete Execution Flow Analysis](#tool-2-perf_analysispy---complete-execution-flow-analysis)
- [Understanding the Output](#understanding-the-output)
- [Performance Metrics Explained](#performance-metrics-explained)
- [Example Workflows](#example-workflows)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The CVA6 performance analysis suite provides two powerful tools for analyzing processor traces:

| Tool | Purpose | Best Used For |
|------|---------|---------------|
| `debug_model.py` | Detailed cycle-by-cycle scoreboard analysis | Understanding pipeline stalls, dependency tracking |
| `perf_analysis.py` | Complete execution flow with performance metrics | Overall performance analysis, issue/commit width optimization |

Both tools work with **RVFI (RISC-V Formal Interface) trace files** generated from CVA6 simulations.

---

## 🔧 Prerequisites

### Required Files
- Python 3.6+ installed
- RVFI trace file (`.log` format) from CVA6 simulation
- `model.py` (core performance model)
- `debug_model.py` (detailed analysis tool)
- `perf_analysis.py` (comprehensive analysis tool)

### Optional Dependencies
```bash
# For enhanced visualization (optional)
pip install matplotlib
```

### Generating RVFI Traces
Follow the CVA6 documentation to generate trace files. Traces are typically found at:
```
verif/sim/out_<date>/<simulator>/<test-name>.log
```

---

## 🚀 Quick Start

### Basic Analysis 
```bash
# 1. Run basic performance analysis
python3 perf_analysis.py your_trace.log

# 2. Save results to file for later review
python3 perf_analysis.py your_trace.log --output analysis_results.txt
```

### Advanced Analysis
```bash
# 1. Generate detailed scoreboard trace
python3 debug_model.py your_trace.log

# 2. Run comprehensive performance analysis with all features
python3 perf_analysis.py your_trace.log --performance --stats --colors
```

---

## 🔍 Tool 1: debug_model.py - Detailed Scoreboard Analysis

### Purpose
Provides cycle-by-cycle visibility into the processor's scoreboard, showing exactly what happens during each clock cycle.

### Usage
```bash
python3 debug_model.py <trace_file.log>
```

### What It Does
1. **Loads your trace file** and simulates the CVA6 pipeline
2. **Enables debug mode** to show complete scoreboard state for each cycle
3. **Saves detailed output** to `scoreboard_<filename>.log`
4. **Shows pipeline behavior** including:
   - Instruction issue/execute/commit timing
   - Functional unit allocation
   - Data dependencies and hazards
   - Scoreboard entry details

### Example Usage
```bash
# Analyze a CoreMark trace
python3 debug_model.py coremark_trace.log

# Output will be saved to: scoreboard_coremark_trace.log
```

### Sample Output Structure
```
CVA6 PERFORMANCE MODEL - DEBUG MODE
================================================================================
Input file: coremark_trace.log
This shows complete scoreboard state for each cycle
================================================================================

Starting simulation with debug output...

addi a0, zero, 20: issue
Scoreboard @0
    PC:0x80000000 addi a0,zero,20 [ALU] issue:0 exec:-- commit:-- (not done)
iqlen = 3

addi a0, zero, 20: done
add t0, a0, zero: issue
Scoreboard @1
    PC:0x80000000 addi a0,zero,20 [ALU] issue:0 exec:1 commit:-- (done)
    PC:0x80000004 add t0,a0,zero [ALU] issue:1 exec:-- commit:-- (not done)
...
```

### Key Information Shown
- **Instruction details**: PC, opcode, operands
- **Functional unit assignment**: ALU, MUL, BRANCH, LDU, STU
- **Timing information**: Issue, execute, commit cycles
- **Pipeline state**: Queue length, scoreboard contents
- **Hazard detection**: RAW, WAW, structural hazards

---

## 📊 Tool 2: perf_analysis.py - Complete Execution Flow Analysis

### Purpose
Comprehensive performance analysis with execution flow, statistics, and issue/commit width optimization.

### Basic Usage
```bash
python3 perf_analysis.py <trace_file.log> [options]
```

### Command Line Options
```bash
# Basic execution flow analysis
python3 perf_analysis.py trace.log

# Save execution flow to file
python3 perf_analysis.py trace.log --output execution_flow.txt

# Run performance model analysis (most comprehensive)
python3 perf_analysis.py trace.log --performance

# Include detailed statistics
python3 perf_analysis.py trace.log --stats

# Use colored output (terminal only)
python3 perf_analysis.py trace.log --colors

# Save all terminal output to file
python3 perf_analysis.py trace.log --save-terminal-output terminal_log.txt

# Complete analysis with all features
python3 perf_analysis.py trace.log --performance --stats --save-terminal-output complete_analysis.txt
```

### What Each Option Does

| Option | Description |
|--------|-------------|
| `--performance` | Runs CVA6 performance model analysis with issue/commit optimization |
| `--stats` | Shows instruction type distribution and execution statistics |
| `--output FILE` | Saves execution flow to specified file |
| `--save-terminal-output FILE` | Captures all console output to file |
| `--colors` | Enables colored terminal output |
| `--debug` | Shows additional debugging information |

### Performance Analysis Features

When using `--performance`, you get:

1. **Single Configuration Analysis** (issue=2, commit=2)
   - Cycle count and instruction count
   - IPC (Instructions Per Cycle)
   - CoreMark/MHz performance metric
   - Event statistics (hazards, branch predictions)

2. **Issue/Commit Width Optimization**
   - Tests all combinations from 1×1 to 3×3
   - Performance matrix showing optimal configurations
   - Improvement analysis compared to baseline
   - Hazard analysis for different configurations

3. **Detailed Event Analysis**
   - RAW (Read After Write) hazards
   - WAW (Write After Write) hazards  
   - Structural hazards
   - Branch hit/miss statistics

---

## 📈 Understanding the Output

### Key Performance Metrics

#### 1. **Cycle Count**
- Total number of clock cycles required to execute the trace
- Lower is better

#### 2. **IPC (Instructions Per Cycle)**
- Average number of instructions executed per cycle
- Higher is better
- Formula: `IPC = Total Instructions ÷ Total Cycles`

#### 3. **CoreMark/MHz**
- Normalized performance metric
- Higher is better
- Formula: `CoreMark/MHz = 1,000,000 ÷ Cycle Count`

#### 4. **Event Statistics**
- **RAW Hazards**: Data dependencies causing stalls
- **Structural Hazards**: Resource conflicts
- **Branch Hits/Misses**: Branch prediction accuracy

### Sample Performance Output
```
====================================================================
CVA6 PERFORMANCE MODEL ANALYSIS
====================================================================
Running single configuration (issue=2, commit=2):
============================================================

cycle number         = 45234
Coremark/MHz         = 22.11
instruction number   = 18456
RAW/instr           = 12.34%
STRUCT/instr        = 5.67%
BHIT/instr          = 8.90%
BMISS/instr         = 1.23%

============================================================
Generating Issue/Commit Performance Analysis...
Testing issue/commit combinations from 1 to 3...

Issue/Commit Performance Matrix:
==================================================
Issue\Commit    0       1       2       3
        0       0.00    0.00    0.00    0.00
        1       0.00    2.65    2.65    2.65
        2       0.00    3.21    3.63    3.63
        3       0.00    3.26    3.90    3.91

Best Configuration: Issue=3, Commit=3
Best Performance: 3.91
```

### Execution Flow Output
```
COMPLETE EXECUTION FLOW - ALL INSTRUCTIONS
====================================================================================================
📁 Trace file: coremark_trace.log
🔢 Total instructions: 18456

#      Cycle    PC                 Encoding     Instruction                    Register Write      
----------------------------------------------------------------------------------------------------
1      0        0x0000000080000000 0x01450513   addi a0,zero,20               x10 <- 0x00000014
2      1        0x0000000080000004 0x00050293   add t0,a0,zero                x5 <- 0x00000014
3      2        0x0000000080000008 0x00a2f463   bgeu t0,a0,8                  -
4      4        0x0000000080000010 0x00150513   addi a0,a0,1                  x10 <- 0x00000015
...
```

---

## 📋 Example Workflows

### Workflow 1: Basic Performance Check
```bash
# Quick performance overview
python3 perf_analysis.py my_trace.log --performance
```
**Use Case**: Get overall performance metrics and find optimal issue/commit configuration.

### Workflow 2: Deep Pipeline Analysis
```bash
# Step 1: Generate detailed scoreboard trace
python3 debug_model.py my_trace.log

# Step 2: Review scoreboard_my_trace.log for pipeline details
# Step 3: Run comprehensive analysis
python3 perf_analysis.py my_trace.log --performance --stats
```
**Use Case**: Understand pipeline stalls and optimize microarchitecture.

### Workflow 3: Complete Documentation
```bash
# Generate comprehensive analysis report
python3 perf_analysis.py my_trace.log \
    --performance \
    --stats \
    --output detailed_flow.txt \
    --save-terminal-output complete_analysis.txt
```
**Use Case**: Create detailed documentation for design reviews or optimization reports.

### Workflow 4: Comparing Multiple Configurations
```bash
# Analyze baseline
python3 debug_model.py baseline_trace.log
python3 perf_analysis.py baseline_trace.log --performance > baseline_results.txt

# Analyze optimized version
python3 debug_model.py optimized_trace.log  
python3 perf_analysis.py optimized_trace.log --performance > optimized_results.txt

# Compare results
diff baseline_results.txt optimized_results.txt
```
**Use Case**: Compare performance before and after microarchitecture changes.

---

## 🔧 Performance Metrics Explained

### Issue/Commit Width Analysis

The tools test different processor configurations:

- **Issue Width**: Number of instructions that can be issued per cycle
- **Commit Width**: Number of instructions that can be committed per cycle

#### Configuration Matrix Example:
```
Issue Width = 2, Commit Width = 2: Performance = 3.63
Issue Width = 3, Commit Width = 3: Performance = 3.91
```

**Interpretation**: Increasing both issue and commit width from 2 to 3 improves performance by 7.7%.

### Hazard Analysis

#### 1. **RAW (Read After Write) Hazards**
- Occur when an instruction needs data from a previous instruction that hasn't completed
- **Example**: `add x1, x2, x3` followed by `sub x4, x1, x5`
- **Impact**: Causes pipeline stalls

#### 2. **Structural Hazards**
- Occur when multiple instructions need the same functional unit
- **Example**: Two ALU instructions trying to execute simultaneously with only one ALU
- **Impact**: Forces instruction to wait for resource availability

#### 3. **Branch Prediction**
- **BHIT**: Branch prediction was correct
- **BMISS**: Branch prediction was wrong (causes pipeline flush)
- **Impact**: Misses significantly hurt performance

---

## ❗ Troubleshooting

### Common Issues and Solutions

#### Issue: "ImportError: No module named 'model'"
**Solution**: Ensure `model.py` is in the same directory as the analysis tools.

#### Issue: "File not found" error
**Solution**: 
- Check that the trace file path is correct
- Ensure the trace file has read permissions
- Use absolute paths if needed

#### Issue: "Empty or invalid trace file"
**Solution**:
- Verify the trace file is a valid RVFI trace
- Check that the file contains instruction data
- Ensure the trace follows the expected format

#### Issue: Performance analysis shows all zeros
**Solution**:
- Check that the trace file contains valid instruction data
- Verify the RVFI trace format matches the expected pattern
- Try with `--debug` flag to see detailed parsing information

#### Issue: Long execution time
**Solution**:
- Large traces can take time to process
- Consider filtering the trace to focus on specific sections
- Use `debug_model.py` for detailed analysis only on smaller traces

### Getting Help

1. **Check file formats**: Ensure your RVFI trace follows the expected format
2. **Use debug mode**: Add `--debug` flag to see detailed processing information  
3. **Start small**: Test with a small trace file first
4. **Check dependencies**: Ensure Python 3.6+ and required modules are available

---

## 📝 Output File Summary

| Tool | Output File | Contains |
|------|-------------|----------|
| `debug_model.py` | `scoreboard_<filename>.log` | Cycle-by-cycle scoreboard state |
| `perf_analysis.py` | (console output) | Performance metrics and analysis |
| `perf_analysis.py --output` | User-specified file | Complete execution flow |
| `perf_analysis.py --save-terminal-output` | User-specified file | All console output |

<!-- ---

## 🎯 Best Practices

1. **Start with basic analysis** before diving into detailed debugging
2. **Use performance analysis** to identify optimization opportunities
3. **Generate documentation** by saving terminal output for reports
4. **Compare configurations** using the issue/commit matrix
5. **Focus on hot spots** revealed by hazard analysis
6. **Validate results** by comparing model predictions with actual RTL simulation -->

---

*This guide covers the essential usage of CVA6 performance analysis tools. For advanced customization, refer to the source code comments in `model.py`, `debug_model.py`, and `perf_analysis.py`.*
