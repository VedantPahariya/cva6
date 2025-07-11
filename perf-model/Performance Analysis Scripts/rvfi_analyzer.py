#!/usr/bin/env python3

"""
RVFI Trace Parser and Analyzer for CVA6 Hello World Program
This script demonstrates how to parse and analyze RVFI traces
"""

import re
import sys
from collections import defaultdict

class RVFITraceAnalyzer:
    def __init__(self, trace_file):
        self.trace_file = trace_file
        self.instructions = []
        self.register_writes = []
        self.memory_accesses = []
        self.pc_sequence = []
        self.statistics = {
            'total_instructions': 0,
            'compressed_instructions': 0,
            'register_writes': 0,
            'memory_reads': 0,
            'memory_writes': 0,
            'branches': 0,
            'jumps': 0,
            'csrs': 0
        }
        self.instruction_types = defaultdict(int)
        
    def parse_trace(self):
        """Parse the RVFI trace file"""
        print(f"Parsing RVFI trace: {self.trace_file}")
        
        with open(self.trace_file, 'r') as f:
            lines = f.readlines()
            
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for instruction lines (format: "core   0: 0x<PC> (0x<encoding>) <instruction>")
            if line.startswith("core   0:"):
                instr_match = re.match(r'core\s+0:\s+0x([0-9a-fA-F]+)\s+\(0x([0-9a-fA-F]+)\)\s+(.+)', line)
                if instr_match:
                    pc = int(instr_match.group(1), 16)
                    encoding = int(instr_match.group(2), 16)
                    instruction = instr_match.group(3).strip()
                    
                    # Check if next line has register write information
                    reg_write_data = None
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        reg_match = re.match(r'(\d+)\s+0x([0-9a-fA-F]+)\s+\(0x([0-9a-fA-F]+)\)\s+x(\d+)\s+0x([0-9a-fA-F]+)', next_line)
                        if reg_match:
                            cycle = int(reg_match.group(1))
                            reg_num = int(reg_match.group(4))
                            reg_value = int(reg_match.group(5), 16)
                            reg_write_data = {'cycle': cycle, 'reg': reg_num, 'value': reg_value}
                            i += 1  # Skip the register write line
                    
                    self.instructions.append({
                        'pc': pc,
                        'encoding': encoding,
                        'instruction': instruction,
                        'reg_write': reg_write_data
                    })
                    
                    self.pc_sequence.append(pc)
                    self.analyze_instruction(instruction, encoding, reg_write_data)
                    
            i += 1
    
    def analyze_instruction(self, instruction, encoding, reg_write_data):
        """Analyze individual instruction and update statistics"""
        self.statistics['total_instructions'] += 1
        
        # Check if compressed instruction (16-bit)
        if encoding <= 0xFFFF:
            self.statistics['compressed_instructions'] += 1
            
        # Categorize instruction types
        instr_parts = instruction.split()
        if instr_parts:
            opcode = instr_parts[0]
            self.instruction_types[opcode] += 1
            
            # Count specific instruction types
            if opcode in ['beq', 'bne', 'blt', 'bge', 'bltu', 'bgeu']:
                self.statistics['branches'] += 1
            elif opcode in ['jal', 'jalr', 'jr']:
                self.statistics['jumps'] += 1
            elif opcode.startswith('csr'):
                self.statistics['csrs'] += 1
            elif opcode in ['lb', 'lh', 'lw', 'ld', 'lbu', 'lhu', 'lwu']:
                self.statistics['memory_reads'] += 1
            elif opcode in ['sb', 'sh', 'sw', 'sd']:
                self.statistics['memory_writes'] += 1
                
        # Count register writes
        if reg_write_data:
            self.statistics['register_writes'] += 1
            self.register_writes.append(reg_write_data)
    
    def print_summary(self):
        """Print analysis summary"""
        print("\n" + "="*60)
        print("RVFI TRACE ANALYSIS SUMMARY")
        print("="*60)
        
        print(f"Total Instructions Executed: {self.statistics['total_instructions']}")
        print(f"Compressed Instructions: {self.statistics['compressed_instructions']}")
        print(f"Register Writes: {self.statistics['register_writes']}")
        print(f"Memory Reads: {self.statistics['memory_reads']}")
        print(f"Memory Writes: {self.statistics['memory_writes']}")
        print(f"Branches: {self.statistics['branches']}")
        print(f"Jumps: {self.statistics['jumps']}")
        print(f"CSR Instructions: {self.statistics['csrs']}")
        
        print(f"\nCompression Ratio: {self.statistics['compressed_instructions']/self.statistics['total_instructions']*100:.1f}%")
        
    def print_instruction_types(self):
        """Print instruction type distribution"""
        print("\n" + "="*60)
        print("INSTRUCTION TYPE DISTRIBUTION")
        print("="*60)
        
        sorted_types = sorted(self.instruction_types.items(), key=lambda x: x[1], reverse=True)
        for instr_type, count in sorted_types[:15]:  # Show top 15
            percentage = (count / self.statistics['total_instructions']) * 100
            print(f"{instr_type:<15} {count:>5} ({percentage:>5.1f}%)")
    
    def print_execution_flow(self, limit=20):
        """Print the first few instructions to show execution flow"""
        print("\n" + "="*60)
        print("EXECUTION FLOW (First {} instructions)".format(limit))
        print("="*60)
        print(f"{'PC':<18} {'Encoding':<10} {'Instruction':<25} {'Reg Write'}")
        print("-" * 80)
        
        for i, instr in enumerate(self.instructions[:limit]):
            reg_info = ""
            if instr['reg_write']:
                reg_info = f"x{instr['reg_write']['reg']} = 0x{instr['reg_write']['value']:x}"
            
            print(f"0x{instr['pc']:016x} 0x{instr['encoding']:08x} {instr['instruction']:<25} {reg_info}")
    
    def detect_program_phases(self):
        """Detect different phases of program execution"""
        print("\n" + "="*60)
        print("PROGRAM EXECUTION PHASES")
        print("="*60)
        
        # Detect boot sequence (typically at low addresses)
        boot_instrs = [instr for instr in self.instructions if instr['pc'] < 0x20000]
        
        # Detect main program (typically at higher addresses)
        main_instrs = [instr for instr in self.instructions if instr['pc'] >= 0x80000000]
        
        print(f"Boot/Setup Phase: {len(boot_instrs)} instructions")
        print(f"Main Program Phase: {len(main_instrs)} instructions")
        
        if boot_instrs:
            print(f"Boot sequence PC range: 0x{boot_instrs[0]['pc']:x} - 0x{boot_instrs[-1]['pc']:x}")
        if main_instrs:
            print(f"Main program PC range: 0x{main_instrs[0]['pc']:x} - 0x{main_instrs[-1]['pc']:x}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 rvfi_analyzer.py <trace_file>")
        sys.exit(1)
    
    trace_file = sys.argv[1]
    analyzer = RVFITraceAnalyzer(trace_file)
    
    try:
        analyzer.parse_trace()
        analyzer.print_summary()
        analyzer.print_instruction_types()
        analyzer.print_execution_flow()
        analyzer.detect_program_phases()
        
        print("\n" + "="*60)
        print("WHAT IS RVFI?")
        print("="*60)
        print("RVFI (RISC-V Formal Interface) provides detailed execution information:")
        print("• Every instruction executed with PC and encoding")
        print("• Register reads/writes with values")
        print("• Memory accesses with addresses and data")
        print("• Exception and interrupt information")
        print("• Performance counter updates")
        print("• Control flow changes (branches, jumps)")
        print("\nThis trace helps in:")
        print("• Performance analysis and optimization")
        print("• Hardware verification")
        print("• Debug and profiling")
        print("• Microarchitecture exploration")
        
    except FileNotFoundError:
        print(f"Error: File '{trace_file}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing trace: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
