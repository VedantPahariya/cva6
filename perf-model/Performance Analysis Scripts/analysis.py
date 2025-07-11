#!/usr/bin/env python3
"""
CVA6 Performance Analysis Utility

This script provides easy access to different performance analysis modes.
"""

import sys
import argparse
from model import Model, issue_commit_graph, print_stats, filter_timed_part, count_cycles

def run_single_config(input_file, issue=2, commit=2, debug=False):
    """Run a single configuration analysis"""
    print(f"Running configuration: issue={issue}, commit={commit}")
    print("=" * 60)
    
    model = Model(debug=debug, issue=issue, commit=commit)
    model.load_file(input_file)
    model.run()
    
    print_stats(model.retired)
    return model

def run_sweep_analysis(input_file, max_width=4):
    """Run a sweep analysis across different issue/commit widths"""
    print(f"Running sweep analysis up to width {max_width}")
    print("=" * 60)
    
    issue_commit_graph(input_file, max_width)

def compare_configs(input_file, configs):
    """Compare specific configurations"""
    print("Comparing configurations:")
    print("=" * 60)
    
    results = []
    for issue, commit in configs:
        print(f"\nTesting issue={issue}, commit={commit}:")
        model = Model(debug=False, issue=issue, commit=commit)
        model.load_file(input_file)
        model.run()
        
        n_cycles = count_cycles(model.retired)
        score = 1000000 / n_cycles
        results.append((issue, commit, score, n_cycles))
        print(f"  Score: {score:.2f} Coremark/MHz ({n_cycles} cycles)")
    
    print("\nSummary:")
    print("Issue\tCommit\tScore\t\tCycles")
    print("-" * 40)
    for issue, commit, score, cycles in results:
        print(f"{issue}\t{commit}\t{score:.2f}\t\t{cycles}")

def main():
    parser = argparse.ArgumentParser(description='CVA6 Performance Analysis Tool')
    parser.add_argument('input_file', help='Input trace file')
    parser.add_argument('--mode', choices=['single', 'sweep', 'compare'], 
                       default='single', help='Analysis mode')
    parser.add_argument('--issue', type=int, default=2, 
                       help='Issue width for single mode')
    parser.add_argument('--commit', type=int, default=2, 
                       help='Commit width for single mode')
    parser.add_argument('--max-width', type=int, default=4, 
                       help='Maximum width for sweep analysis')
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug output')
    parser.add_argument('--configs', nargs='+', type=str,
                       help='Configurations to compare (format: "issue,commit")')
    
    args = parser.parse_args()
    
    if args.mode == 'single':
        run_single_config(args.input_file, args.issue, args.commit, args.debug)
    
    elif args.mode == 'sweep':
        run_sweep_analysis(args.input_file, args.max_width)
    
    elif args.mode == 'compare':
        if not args.configs:
            # Default configurations to compare
            configs = [(1, 1), (2, 2), (3, 3), (4, 4)]
        else:
            configs = []
            for config in args.configs:
                try:
                    issue, commit = map(int, config.split(','))
                    configs.append((issue, commit))
                except ValueError:
                    print(f"Invalid config format: {config}. Use 'issue,commit'")
                    sys.exit(1)
        
        compare_configs(args.input_file, configs)

if __name__ == "__main__":
    main()
