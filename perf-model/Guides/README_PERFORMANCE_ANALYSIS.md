# CVA6 Performance Model Analysis

## Overview

The CVA6 performance model simulates the out-of-order execution pipeline to predict performance characteristics. It models key components like instruction queues, scoreboards, hazard detection, and branch prediction.

## Performance Model Output Explanation

### 1. Single Configuration Results

When running with `issue=2, commit=2`:
```
cycle number             = 2338
Coremark/MHz             = 427.72
instruction number       = 2021
EventKind.issue/instr    = 100.00%
EventKind.done/instr     = 100.00%
EventKind.commit/instr   = 100.00%
EventKind.RAW/instr      = 106.83%
EventKind.BMISS/instr    = 0.69%
EventKind.BHIT/instr     = 7.97%
EventKind.STRUCT/instr   = 24.39%
```

**Key Metrics:**
- **Coremark/MHz = 427.72**: Performance score (higher is better)
- **RAW/instr = 106.83%**: Read-After-Write hazards per instruction (indicates data dependencies)
- **BMISS/instr = 0.69%**: Branch misprediction rate (very low, good branch prediction)
- **BHIT/instr = 7.97%**: Branch hit rate
- **STRUCT/instr = 24.39%**: Structural hazards (resource conflicts)

### 2. Issue/Commit Width Analysis

The model tests different combinations of issue width (instructions issued per cycle) and commit width (instructions committed per cycle):

```
Issue/Commit Performance Matrix:
Issue\Commit         0.0             1.0             2.0             3.0
        0           0.00            0.00            0.00            0.00
        1           0.00          363.11          363.24          363.24
        2           0.00          419.64          427.72          427.90
        3           0.00          420.34          429.18          429.37
```

**Key Insights:**

1. **Issue Width Impact**: 
   - Going from issue=1 to issue=2 provides significant improvement (~15-17%)
   - Going from issue=2 to issue=3 provides minimal improvement (~0.3-0.4%)

2. **Commit Width Impact**:
   - With issue=1: Commit width has minimal impact (363.11 → 363.24)
   - With issue=2: Commit width provides good improvement (419.64 → 427.90)
   - With issue=3: Similar pattern (420.34 → 429.37)

3. **Optimal Configuration**:
   - Best performance: issue=3, commit=3 (429.37 Coremark/MHz)
   - Diminishing returns beyond issue=2, commit=2

## Understanding the Pipeline Model

### Pipeline Stages Simulated

1. **Fetch**: Instructions are fetched and added to instruction queue
2. **Issue**: Instructions are issued when dependencies are resolved
3. **Execute**: Instructions complete execution
4. **Commit**: Instructions are retired in-order

### Hazard Types

- **RAW (Read-After-Write)**: Data dependency hazards
- **STRUCT (Structural)**: Resource conflicts
- **BMISS (Branch Miss)**: Branch mispredictions requiring pipeline flush
- **BHIT (Branch Hit)**: Correct branch predictions

### Advanced Features

- **Scoreboard**: Tracks instruction dependencies and resource availability
- **Return Address Stack (RAS)**: Predicts function return addresses
- **Branch Prediction**: Models branch prediction accuracy
- **Out-of-Order Execution**: Instructions can complete out of program order

## Usage Examples

### Basic Performance Analysis
```bash
python3 model.py trace_file.log
```

### Custom Issue/Commit Configuration
```python
model = Model(debug=False, issue=4, commit=2)
```

### Generate Issue/Commit Performance Graph
```python
issue_commit_graph(input_file, 5)  # Test up to 5-wide
```

## Interpreting Results for Design Decisions

1. **For High Performance**: Use issue=3, commit=3
2. **For Area Efficiency**: Use issue=2, commit=2 (good performance/area ratio)
3. **For Low Power**: Use issue=1, commit=2

The model helps architects understand the performance implications of different pipeline configurations before RTL implementation.

## Installation Requirements

```bash
# Optional: For graphical visualization
pip install matplotlib
```

## Files Generated

- `annotated.log`: Detailed trace with cycle annotations
- Performance matrices in console output
- 3D performance graphs (if matplotlib available)
