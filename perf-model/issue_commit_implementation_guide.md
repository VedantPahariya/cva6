# Issue/Commit Graph Implementation Guide

## Overview
The `issue_commit_graph` function tests different combinations of issue and commit widths to find the optimal processor configuration for performance.

## How It Works

### 1. Function Signature
```python
def issue_commit_graph(input_file, n = 3):
    """Plot the issue/commit graph"""
```

### 2. Core Algorithm
The function systematically tests all combinations of:
- Issue width: 1 to n
- Commit width: 1 to n

For each combination, it:
1. Creates a new model with specific issue/commit widths
2. Loads the instruction trace
3. Runs the simulation
4. Calculates performance score
5. Stores results in a matrix

### 3. Step-by-Step Implementation

```python
# Initialize scores matrix (n+1 x n+1 to include 0 index)
scores = [[0 for _ in range(n + 1)] for _ in range(n + 1)]

total_combinations = n * n
current = 0

for issue in range(1, n + 1):
    for commit in range(1, n + 1):
        current += 1
        print(f"[{current}/{total_combinations}] Testing issue={issue}, commit={commit}...")
        
        # Create model with specific configuration
        model = Model(debug=False, issue=issue, commit=commit)
        
        # Load trace file
        model.load_file(input_file)
        
        # Run simulation
        model.run()
        
        # Calculate performance score
        n_cycles = count_cycles(model.retired)
        score = 1000000 / n_cycles
        
        # Store in matrix
        scores[issue][commit] = score
```

### 4. Performance Calculation
```python
def count_cycles(retired):
    start = min(e.cycle for e in retired[0].events)
    end = max(e.cycle for e in retired[-1].events)
    return end - start

score = 1000000 / n_cycles  # CoreMark/MHz approximation
```

### 5. Results Display
The function displays results in two ways:

#### A. Text Matrix
```
Issue\Commit	     0.0	     1.0	     2.0	     3.0
        0	    0.00	    0.00	    0.00	    0.00
        1	    0.00	  363.11	  363.24	  363.24
        2	    0.00	  419.64	  427.72	  427.90
        3	    0.00	  420.34	  429.18	  429.37
```

#### B. 3D Bar Chart (if matplotlib available)
```python
if HAS_MATPLOTLIB:
    bars = []
    for x, l in enumerate(scores):
        for y, z in enumerate(l):
            if z > 0:
                bars.append((x, y, z))
    
    fig = plt.figure(figsize=(10, 8))
    ax1 = fig.add_subplot(111, projection='3d')
    ax1.bar3d(x, y, z, dx, dy, dz)
    ax1.set_xlabel("Issue Width")
    ax1.set_ylabel("Commit Width")
    ax1.set_zlabel("CoreMark/MHz")
    plt.show()
```

## Key Components in the Model

### 1. Model Class Constructor
```python
def __init__(self, debug=False, issue=1, commit=2, ...):
    self.issue_width = issue
    self.commit_width = commit
    self.fus = FusBusy(issue > 1)  # Enable second ALU if issue > 1
```

### 2. Issue Logic
```python
def try_issue(self, cycle):
    # Try to issue multiple instructions per cycle
    for _ in range(self.issue_width):
        if can_issue_instruction():
            issue_instruction()
```

### 3. Commit Logic
```python
def try_commit(self, cycle, commit_port):
    # Try to commit multiple instructions per cycle
    for commit_port in range(self.commit_width):
        if can_commit_instruction():
            commit_instruction()
```

## Implementing Your Own Issue/Commit Graph

### 1. Simple Version
```python
def simple_issue_commit_test(input_file, max_width=3):
    """Simple version focusing on key metrics"""
    results = {}
    
    for issue in range(1, max_width + 1):
        for commit in range(1, max_width + 1):
            model = Model(issue=issue, commit=commit)
            model.load_file(input_file)
            cycles = model.run()
            
            performance = 1000000 / cycles
            results[(issue, commit)] = performance
            
            print(f"Issue={issue}, Commit={commit}: {performance:.2f}")
    
    return results
```

### 2. Advanced Version with Analysis
```python
def advanced_issue_commit_analysis(input_file, max_width=4):
    """Advanced version with detailed analysis"""
    results = {}
    
    for issue in range(1, max_width + 1):
        for commit in range(1, max_width + 1):
            model = Model(issue=issue, commit=commit)
            model.load_file(input_file)
            model.run()
            
            # Calculate various metrics
            cycles = count_cycles(model.retired)
            instructions = len(model.retired)
            ipc = instructions / cycles
            performance = 1000000 / cycles
            
            # Analyze hazards
            hazards = analyze_hazards(model.retired)
            
            results[(issue, commit)] = {
                'performance': performance,
                'ipc': ipc,
                'cycles': cycles,
                'hazards': hazards
            }
    
    return results
```

### 3. Custom Metrics
```python
def analyze_hazards(instructions):
    """Analyze different types of hazards"""
    hazards = {
        'RAW': 0,
        'WAW': 0,
        'STRUCT': 0,
        'BMISS': 0
    }
    
    for instr in instructions:
        for event in instr.events:
            if event.kind.name in hazards:
                hazards[event.kind.name] += 1
    
    return hazards
```

## Understanding the Results

### 1. Performance Trends
- **Issue Width 1→2**: Usually significant improvement
- **Issue Width 2→3**: Diminishing returns due to dependencies
- **Commit Width**: Usually less impact than issue width

### 2. Bottleneck Identification
- **RAW hazards**: Data dependencies limiting parallelism
- **Structural hazards**: Functional unit conflicts
- **Branch mispredictions**: Control flow penalties

### 3. Optimal Configuration
The matrix helps identify:
- **Sweet spot**: Best performance/complexity ratio
- **Bottlenecks**: Where additional resources don't help
- **Scalability**: How performance scales with resources

## Practical Usage

### 1. Running the Analysis
```bash
python3 model.py trace_file.log
```

### 2. Interpreting Results
Look for:
- **Highest scores**: Best absolute performance
- **Diminishing returns**: Where additional resources don't help
- **Bottlenecks**: Configurations where one dimension limits the other

### 3. Design Decisions
Use results to:
- **Set issue width**: Balance performance vs. complexity
- **Set commit width**: Usually 2 is sufficient
- **Identify bottlenecks**: Focus optimization efforts
- **Validate design**: Compare against expectations
