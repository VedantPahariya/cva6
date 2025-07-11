# CVA6 Performance Modeling - Complete Guide

## Quick Summary of Your Results

### Your Performance Model Output Analysis
When you ran: `python3 model.py ../verif/sim/out_2025-07-06/veri-testharness_sim/multiply.cv64a6_imafdc_sv39.log`

**Key Results:**
- **Execution Time**: 2338 cycles for 2021 instructions
- **Performance Score**: 427.72 CoreMark/MHz (higher is better)
- **IPC (Instructions Per Cycle)**: 0.86 (2021÷2338)
- **Major Bottleneck**: RAW hazards (106.83% per instruction)

### What This Means
Your CVA6 processor configuration (Issue=2, Commit=2) is performing reasonably well, but data dependencies (RAW hazards) are the main performance limiter.

## Understanding the Output

### 1. Performance Metrics
```
cycle number             = 2338        # Total execution cycles
Coremark/MHz             = 427.72      # Performance score
instruction number       = 2021        # Total instructions
```

### 2. Hazard Analysis
```
EventKind.RAW/instr      = 106.83%     # Data dependency stalls
EventKind.STRUCT/instr   = 24.39%      # Resource conflicts
EventKind.BMISS/instr    = 0.69%       # Branch mispredictions
EventKind.BHIT/instr     = 7.97%       # Branch prediction hits
```

### 3. Issue/Commit Analysis Results
```
Issue\Commit     1.0      2.0      3.0
    1          363.11   363.24   363.24
    2          419.64   427.72   427.90
    3          420.34   429.18   429.37
```

## How issue_commit_graph Works

### 1. Basic Concept
The function tests different processor configurations by varying:
- **Issue Width**: How many instructions can be issued per cycle
- **Commit Width**: How many instructions can be committed per cycle

### 2. Implementation Steps
```python
def issue_commit_graph(input_file, n=3):
    scores = [[0 for _ in range(n + 1)] for _ in range(n + 1)]
    
    for issue in range(1, n + 1):
        for commit in range(1, n + 1):
            # Create model with specific configuration
            model = Model(issue=issue, commit=commit)
            model.load_file(input_file)
            model.run()
            
            # Calculate performance
            cycles = count_cycles(model.retired)
            score = 1000000 / cycles
            scores[issue][commit] = score
    
    display_scores(scores)
```

### 3. Key Insights from Your Results

#### Issue Width Impact
- **1→2**: +15.6% to +17.8% improvement (significant)
- **2→3**: +0.4% to +0.6% improvement (diminishing returns)

#### Commit Width Impact
- **1→2**: +0.0% to +2.2% improvement (moderate)
- **2→3**: +0.0% to +0.2% improvement (minimal)

#### Why These Results?
1. **Issue Width 1→2**: Big improvement because you can issue more instructions
2. **Issue Width 2→3**: Small improvement due to data dependencies (RAW hazards)
3. **Commit Width**: Less impact because issue width is the main bottleneck

## Practical Usage

### 1. Running Your Own Analysis
```bash
# Basic analysis
python3 model.py your_trace_file.log

# Run the demo for step-by-step explanation
python3 demo_issue_commit.py your_trace_file.log
```

### 2. Interpreting Results

#### Performance Optimization Priority
1. **Fix RAW hazards** (106.83% - highest impact)
   - Implement better data forwarding
   - Improve register renaming
   
2. **Reduce structural hazards** (24.39% - moderate impact)
   - Add more functional units
   - Better resource scheduling

3. **Branch prediction** (0.69% misses - already good)
   - Current branch predictor is working well

#### Configuration Recommendations
- **Issue Width**: 2 is optimal (good performance/complexity ratio)
- **Commit Width**: 2 is sufficient (diminishing returns beyond this)
- **Focus Areas**: Data forwarding and functional unit resources

### 3. Files Generated

#### annotated.log
Shows when each instruction was committed:
```
core 0: 0x0000000000010000 (0x00100413) @ 2 li s0, 1
core 0: 0x0000000000010004 (0x01f41413) @ 3 slli s0, s0, 31
```

## Implementation Details

### 1. Model Architecture
```python
class Model:
    def __init__(self, issue=1, commit=2, ...):
        self.issue_width = issue      # Instructions issued per cycle
        self.commit_width = commit    # Instructions committed per cycle
        self.scoreboard = []          # Track in-flight instructions
        self.fus = FusBusy()         # Functional unit status
```

### 2. Simulation Loop
```python
def run_cycle(self, cycle):
    self.fus.cycle()                 # Update functional units
    for i in range(self.commit_width):
        self.try_commit(cycle, i)    # Try to commit instructions
    self.try_execute(cycle)          # Execute instructions
    for i in range(self.issue_width):
        self.try_issue(cycle)        # Try to issue instructions
```

### 3. Hazard Detection
```python
def find_data_hazards(self, instr, cycle):
    for entry in self.scoreboard:
        if instr.has_RAW_from(entry.instr):
            self.log_event_on(instr, EventKind.RAW, cycle)
            return True
    return False
```

## Advanced Features

### 1. Custom Analysis
You can modify the model to test:
- Different cache configurations
- Various branch predictors
- Alternative forwarding schemes
- Different functional unit configurations

### 2. Visualization
With matplotlib installed, you get 3D bar charts showing:
- Issue width (X-axis)
- Commit width (Y-axis)
- Performance score (Z-axis)

### 3. Trace Analysis
The model can analyze any CVA6 trace file to:
- Identify performance bottlenecks
- Test architectural changes
- Optimize processor configuration

## Conclusion

Your CVA6 performance model shows that:
1. **Current configuration** (Issue=2, Commit=2) is well-balanced
2. **Main bottleneck** is data dependencies (RAW hazards)
3. **Optimization focus** should be on data forwarding and register renaming
4. **Issue width** has more impact than commit width for this workload

The issue_commit_graph function is a powerful tool for architectural exploration and optimization of the CVA6 processor design.
