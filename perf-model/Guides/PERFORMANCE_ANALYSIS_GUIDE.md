# Enhanced Complete Execution Flow Analyzer - Performance Analysis Guide

## Overview

The `complete_execution_flow.py` script has been enhanced to include comprehensive performance analysis capabilities from `model.py`. This provides the same detailed CVA6 performance modeling that you see in your note.txt output.

## New Features

### 1. Performance Model Analysis (--performance)

When you use the `--performance` flag, the analyzer will run the same analysis as `model.py` and output:

```
Running single configuration (issue=2, commit=2):
============================================================
cycle number             = 2338
Coremark/MHz             = 427.71599657827204
instruction number       = 2021
EventKind.issue/instr    = 100.00%
EventKind.done/instr     = 100.00%
EventKind.commit/instr   = 100.00%
EventKind.RAW/instr      = 106.83%
EventKind.BMISS/instr    = 0.69%
EventKind.BHIT/instr     = 7.97%
EventKind.STRUCT/instr   = 24.39%

============================================================
Generating Issue/Commit Performance Analysis...
Testing issue/commit combinations from 1 to 3...
[1/9] Testing issue=1, commit=1... Score: 363.11
[2/9] Testing issue=1, commit=2... Score: 363.24
...
Issue/Commit Performance Matrix:
==================================================
Issue\Commit         0.0             1.0             2.0             3.0
        0           0.00            0.00            0.00            0.00
        1           0.00          363.11          363.24          363.24
        2           0.00          419.64          427.72          427.90
        3           0.00          420.34          429.18          429.37
```

## Usage Examples

### Basic Analysis
```bash
python3 complete_execution_flow.py trace.log
```

### Performance Analysis Only
```bash
python3 complete_execution_flow.py trace.log --performance
```

### Full Analysis with Terminal Output Saved
```bash
python3 complete_execution_flow.py trace.log --performance --save-terminal-output analysis_results.txt
```

### Performance Analysis + Execution Flow to Separate Files
```bash
python3 complete_execution_flow.py trace.log --performance --output execution_flow.txt --save-terminal-output performance_analysis.txt
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `--performance` | Run CVA6 performance model analysis (requires model.py) |
| `--output FILE` | Save execution flow to file |
| `--save-terminal-output FILE` | Save all console output to file |
| `--stats` | Print instruction type statistics |
| `--colors` | Use colored output (console only) |
| `--debug` | Enable debug output |

## What the Performance Analysis Includes

### 1. Single Configuration Analysis (issue=2, commit=2)
- **Cycle count**: Total execution cycles
- **Coremark/MHz**: Performance metric (higher is better)
- **Instruction count**: Total instructions executed
- **Event statistics**: Hazard and prediction statistics
  - RAW (Read-After-Write) hazards
  - Structural hazards
  - Branch misses (BMISS) and hits (BHIT)

### 2. Issue/Commit Width Analysis
Tests all combinations from 1x1 to 3x3:
- **Issue width**: Number of instructions that can be issued per cycle
- **Commit width**: Number of instructions that can be committed per cycle
- **Performance scores**: Coremark/MHz for each configuration
- **Performance matrix**: Visual representation of results

## Understanding the Results

### Key Metrics
- **Higher Coremark/MHz = Better performance**
- **Lower cycle count = Faster execution**
- **RAW hazards**: Data dependencies that stall the pipeline
- **Structural hazards**: Resource conflicts (functional units busy)
- **Branch prediction**: Accuracy affects performance significantly

### Optimal Configurations
From your example results:
- **Best**: Issue=3, Commit=3 (429.37 Coremark/MHz)
- **Good**: Issue=2, Commit=2 (427.72 Coremark/MHz)
- **Baseline**: Issue=1, Commit=1 (363.11 Coremark/MHz)

## Requirements

- **model.py**: Must be in the same directory
- **Python 3.6+**: For f-string support and other modern features
- **RVFI trace file**: Generated from CVA6 simulation

## Example Workflow

1. **Generate trace file** (from CVA6 simulation):
   ```bash
   # Run your simulation to generate the trace
   make sim
   ```

2. **Run basic analysis**:
   ```bash
   python3 complete_execution_flow.py trace.log --save-terminal-output basic_analysis.txt
   ```

3. **Run performance analysis**:
   ```bash
   python3 complete_execution_flow.py trace.log --performance --save-terminal-output perf_analysis.txt
   ```

4. **Analyze results**:
   - Check `perf_analysis.txt` for complete performance data
   - Compare different configurations
   - Identify performance bottlenecks

## Troubleshooting

### "Performance analysis requires model.py" Error
- Ensure `model.py` is in the same directory
- Check that all required imports work

### Analysis Takes Too Long
- Performance analysis runs 9 different configurations
- Use `--save-terminal-output` to capture results
- Consider reducing the analysis range if needed

### Large Output Files
- Use `--output` to save execution flow separately
- Terminal output capture includes all console messages
- Performance analysis generates detailed statistics

## Integration with Existing Workflow

This enhanced analyzer maintains all existing functionality while adding performance modeling. You can:

1. **Replace model.py calls** with `complete_execution_flow.py --performance`
2. **Get both execution flow AND performance analysis** in one command
3. **Save all results** to files for documentation and sharing
4. **Use existing trace files** without modification

The output format matches `model.py` exactly, so existing scripts and analysis workflows will continue to work.
