#!/usr/bin/env python3

"""
Simplified demonstration of issue_commit_graph functionality
This script shows how the issue/commit width analysis works step by step
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model import Model, count_cycles

def demo_issue_commit_analysis(input_file, max_width=2):
    """
    Simplified demonstration of issue/commit width analysis
    
    Args:
        input_file: Path to the trace log file
        max_width: Maximum issue/commit width to test
    """
    print("=" * 60)
    print("DEMO: Issue/Commit Width Analysis")
    print("=" * 60)
    
    results = {}
    
    print(f"Testing combinations from 1x1 to {max_width}x{max_width}")
    print("Format: Issue=X, Commit=Y")
    print()
    
    for issue in range(1, max_width + 1):
        for commit in range(1, max_width + 1):
            print(f"Testing Issue={issue}, Commit={commit}...", end=" ")
            
            # Create model with specific configuration
            model = Model(
                debug=False,
                issue=issue,
                commit=commit,
                sb_len=8,
                has_forwarding=True,
                has_renaming=True
            )
            
            # Load the trace file
            model.load_file(input_file)
            
            # Run simulation
            total_cycles = model.run()
            
            # Calculate metrics
            n_cycles = count_cycles(model.retired)
            n_instructions = len(model.retired)
            ipc = n_instructions / n_cycles if n_cycles > 0 else 0
            performance = 1000000 / n_cycles if n_cycles > 0 else 0
            
            # Store results
            results[(issue, commit)] = {
                'cycles': n_cycles,
                'instructions': n_instructions,
                'ipc': ipc,
                'performance': performance
            }
            
            print(f"Performance: {performance:.2f}")
    
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    
    # Display detailed results
    print(f"{'Config':<12} {'Cycles':<8} {'Instrs':<8} {'IPC':<6} {'Perf':<8}")
    print("-" * 50)
    
    for (issue, commit), data in sorted(results.items()):
        config = f"{issue}x{commit}"
        print(f"{config:<12} {data['cycles']:<8} {data['instructions']:<8} "
              f"{data['ipc']:<6.2f} {data['performance']:<8.2f}")
    
    # Find best configuration
    best_config = max(results.items(), key=lambda x: x[1]['performance'])
    best_issue, best_commit = best_config[0]
    best_perf = best_config[1]['performance']
    
    print(f"\nBest Configuration: Issue={best_issue}, Commit={best_commit}")
    print(f"Best Performance: {best_perf:.2f}")
    
    # Show improvement analysis
    print("\n" + "=" * 60)
    print("IMPROVEMENT ANALYSIS")
    print("=" * 60)
    
    baseline = results[(1, 1)]['performance']
    
    print(f"Baseline (1x1): {baseline:.2f}")
    print()
    
    for (issue, commit), data in sorted(results.items()):
        if issue == 1 and commit == 1:
            continue
        
        improvement = (data['performance'] / baseline - 1) * 100
        print(f"Issue={issue}, Commit={commit}: {improvement:+.1f}% improvement")
    
    return results

def demo_hazard_analysis(input_file):
    """
    Demonstrate hazard analysis for different configurations
    """
    print("\n" + "=" * 60)
    print("DEMO: Hazard Analysis")
    print("=" * 60)
    
    configs = [(1, 1), (2, 2), (3, 3)]
    
    for issue, commit in configs:
        print(f"\nConfiguration: Issue={issue}, Commit={commit}")
        print("-" * 40)
        
        model = Model(debug=False, issue=issue, commit=commit)
        model.load_file(input_file)
        model.run()
        
        # Count different types of events
        event_counts = {}
        total_instructions = len(model.retired)
        
        for instr in model.retired:
            for event in instr.events:
                event_type = event.kind.name
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        # Display hazard statistics
        hazard_types = ['RAW', 'WAW', 'STRUCT', 'BMISS', 'BHIT']
        
        for hazard_type in hazard_types:
            count = event_counts.get(hazard_type, 0)
            percentage = (count / total_instructions * 100) if total_instructions > 0 else 0
            print(f"  {hazard_type:<8}: {count:>4} ({percentage:>5.1f}%)")

def main():
    """Main demonstration function"""
    if len(sys.argv) != 2:
        print("Usage: python3 demo_issue_commit.py <trace_file>")
        print("Example: python3 demo_issue_commit.py ../verif/sim/out_2025-07-06/veri-testharness_sim/multiply.cv64a6_imafdc_sv39.log")
        return
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found")
        return
    
    print("CVA6 Performance Model - Issue/Commit Width Analysis Demo")
    print(f"Input file: {input_file}")
    
    # Run the demonstrations
    results = demo_issue_commit_analysis(input_file, max_width=3)
    demo_hazard_analysis(input_file)
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print("This demo shows how the issue_commit_graph function works.")
    print("You can modify the max_width parameter to test more configurations.")
    print("The full model.py includes 3D visualization when matplotlib is available.")

if __name__ == "__main__":
    main()
