#!/usr/bin/env python3

"""
Simple RVFI Trace Analyzer for CVA6 Hello World Program
"""

import sys
import re

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 simple_rvfi_analyzer.py <trace_file>")
        sys.exit(1)
    
    trace_file = sys.argv[1]
    
    try:
        with open(trace_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{trace_file}' not found")
        sys.exit(1)
    
    print(f"Analyzing RVFI trace: {trace_file}")
    print(f"Total lines in file: {len(lines)}")
    
    instructions = []
    register_writes = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Look for instruction lines
        if line.startswith("core   0:"):
            # Extract PC, encoding, and instruction
            parts = line.split()
            if len(parts) >= 4:
                pc = parts[2]  # 0x0000000000010000
                encoding = parts[3]  # (0x00100413)
                instruction = ' '.join(parts[4:])  # li s0, 1
                
                instructions.append({
                    'line': i,
                    'pc': pc,
                    'encoding': encoding,
                    'instruction': instruction
                })
        
        # Look for register write lines (format: "3 0x... (0x...) x 8 0x...")
        elif line and line[0].isdigit():
            parts = line.split()
            if len(parts) >= 5 and parts[3] == 'x':
                cycle = parts[0]
                reg_num = parts[4]
                reg_value = parts[5] if len(parts) > 5 else "0x0"
                
                register_writes.append({
                    'line': i,
                    'cycle': cycle,
                    'register': reg_num,
                    'value': reg_value
                })
    
    # Print analysis
    print("\n" + "="*60)
    print("RVFI TRACE ANALYSIS")
    print("="*60)
    
    print(f"Instructions found: {len(instructions)}")
    print(f"Register writes found: {len(register_writes)}")
    
    # Show first 10 instructions
    print("\nFirst 10 instructions:")
    print("-" * 80)
    for i, instr in enumerate(instructions[:10]):
        print(f"{i+1:2d}. PC: {instr['pc']} | {instr['encoding']} | {instr['instruction']}")
    
    # Show first 10 register writes
    print("\nFirst 10 register writes:")
    print("-" * 80)
    for i, reg in enumerate(register_writes[:10]):
        print(f"{i+1:2d}. Cycle {reg['cycle']}: x{reg['register']} = {reg['value']}")
    
    # Count instruction types
    instr_types = {}
    compressed_count = 0
    
    for instr in instructions:
        # Extract opcode (first word of instruction)
        opcode = instr['instruction'].split()[0]
        instr_types[opcode] = instr_types.get(opcode, 0) + 1
        
        # Count compressed instructions (c.* opcodes)
        if opcode.startswith('c.'):
            compressed_count += 1
    
    print(f"\nCompressed instructions: {compressed_count} ({compressed_count/len(instructions)*100:.1f}%)")
    
    print("\nTop 10 instruction types:")
    print("-" * 40)
    sorted_types = sorted(instr_types.items(), key=lambda x: x[1], reverse=True)
    for opcode, count in sorted_types[:10]:
        percentage = (count / len(instructions)) * 100
        print(f"{opcode:<15} {count:>5} ({percentage:>5.1f}%)")
    
    print("\n" + "="*60)
    print("WHAT IS RVFI?")
    print("="*60)
    print("RVFI (RISC-V Formal Interface) captures detailed execution information:")
    print("• Every instruction executed with PC and encoding")
    print("• Register reads/writes with values")
    print("• Memory accesses with addresses and data")
    print("• Exception and interrupt information")
    print("\nThis trace helps in:")
    print("• Performance analysis and optimization")
    print("• Hardware verification and debugging")
    print("• Microarchitecture exploration")
    print("• Instruction-level profiling")

if __name__ == "__main__":
    main()
