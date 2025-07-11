#!/usr/bin/env python3

"""
Debug version of the performance model that shows complete scoreboard results
This version enables debug output to show detailed scoreboard information for each cycle
"""

import sys
import os
from contextlib import redirect_stdout
from model import Model

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 debug_model.py <trace_file.log>")
        print("This will show complete scoreboard results for each instruction when run with debug enabled")
        print("Output will be saved to 'scoreboard_debug.log'")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    
    # Generate output filename based on input filename
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = f"scoreboard_{base_name}.log"
    
    print(f"Running CVA6 Performance Model in Debug Mode...")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    print("Processing... (this may take a moment)")
    
    # Redirect all output to file
    with open(output_file, 'w') as f:
        with redirect_stdout(f):
            print("=" * 80)
            print("CVA6 PERFORMANCE MODEL - DEBUG MODE")
            print("=" * 80)
            print(f"Input file: {input_file}")
            print("This shows complete scoreboard state for each cycle")
            print("Each entry shows: instruction details, functional unit, timing info")
            print("=" * 80)
            print()
            
            # Create model with debug enabled
            model = Model(
                debug=True,  # This is the key - enables detailed scoreboard output
                issue=2,
                commit=2,
                sb_len=8,
                has_forwarding=True,
                has_renaming=True
            )
            
            # Load the trace file
            model.load_file(input_file)
            
            print("Starting simulation with debug output...")
            print()
            
            # Run simulation - this will print detailed scoreboard info for each cycle
            total_cycles = model.run()
            
            # Fix cycle count (model.run() returns cycle+1, so subtract 1)
            actual_cycles = total_cycles - 1
            
            print("=" * 80)
            print("SIMULATION COMPLETE")
            print("=" * 80)
            print(f"Total cycles: {actual_cycles}")
            print(f"Total instructions: {len(model.retired)}")
            print(f"IPC: {len(model.retired) / actual_cycles:.3f}")
            print()
            print("Debug output above shows the complete scoreboard state for each cycle.")
            print("Each scoreboard entry contains:")
            print("- Instruction details (PC, opcode, operands)")
            print("- Functional unit assignment")
            print("- Timing information")
            print("- Dependency information")
    
    # Print summary to console
    actual_cycles = total_cycles - 1
    print(f"✅ Debug output saved to: {output_file}")
    print(f"📊 Summary:")
    print(f"   - Total cycles: {actual_cycles}")
    print(f"   - Total instructions: {len(model.retired)}")
    print(f"   - IPC: {len(model.retired) / actual_cycles:.3f}")
    print(f"   - Check {output_file} for detailed scoreboard trace")

if __name__ == "__main__":
    main()
