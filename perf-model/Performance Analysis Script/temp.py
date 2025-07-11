#!/usr/bin/env python3

"""
Unified RVFI Trace Analyzer for CVA6
=====================================

This comprehensive tool combines functionality from multiple analysis scripts:
- rvfi_analyzer.py: Detailed instruction parsing and statistics
- simple_rvfi_analyzer.py: Basic analysis and instruction type breakdown
- demo_issue_commit.py: Issue/commit width analysis demonstration
- model.py: Performance modeling infrastructure
- perf_analysis.py: Performance analysis utilities

Features:
- Comprehensive instruction statistics
- Instruction type breakdown and analysis
- Execution flow visualization
- Program phase detection
- Performance modeling (optional)
- Optimization recommendations
- Export capabilities

Usage:
    python3 unified_analyzer.py <trace_file> [options]
"""

import sys
import os
import re
import argparse
from collections import defaultdict, Counter
from datetime import datetime

# Add current directory to path for model imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from model import Model, count_cycles, filter_timed_part
    HAS_MODEL = True
except ImportError:
    HAS_MODEL = False
    print("Warning: model.py not available. Performance modeling disabled.")

class UnifiedRVFIAnalyzer:
    """Unified analyzer that combines all RVFI analysis capabilities"""
    
    def __init__(self, trace_file, debug=False):
        self.trace_file = trace_file
        self.debug = debug
        self.instructions = []
        self.register_writes = []
        self.pc_sequence = []
        
        # Statistics tracking
        self.statistics = {
            'total_instructions': 0,
            'compressed_instructions': 0,
            'register_writes': 0,
            'memory_reads': 0,
            'memory_writes': 0,
            'branches': 0,
            'jumps': 0,
            'arithmetic': 0,
            'loads': 0,
            'stores': 0,
            'csrs': 0,
            'system': 0,
            'total_lines': 0
        }
        
        self.instruction_types = defaultdict(int)
        self.instruction_categories = defaultdict(int)
        
    def parse_trace(self):
        """Parse the RVFI trace file with comprehensive analysis"""
        print(f"📊 Parsing RVFI trace: {self.trace_file}")
        
        try:
            with open(self.trace_file, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"❌ Error: File '{self.trace_file}' not found")
            return False
        
        self.statistics['total_lines'] = len(lines)
        
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
                            self.register_writes.append(reg_write_data)
                            i += 1  # Skip the register write line
                    
                    self.instructions.append({
                        'pc': pc,
                        'encoding': encoding,
                        'instruction': instruction,
                        'reg_write': reg_write_data
                    })
                    
                    self.pc_sequence.append(pc)
                    self.analyze_instruction(instruction, encoding, reg_write_data)
                    
            # Look for standalone register write lines
            elif line and line[0].isdigit():
                reg_match = re.match(r'(\d+)\s+0x([0-9a-fA-F]+)\s+\(0x([0-9a-fA-F]+)\)\s+x(\d+)\s+0x([0-9a-fA-F]+)', line)
                if reg_match:
                    cycle = int(reg_match.group(1))
                    reg_num = int(reg_match.group(4))
                    reg_value = int(reg_match.group(5), 16)
                    self.register_writes.append({
                        'cycle': cycle, 
                        'reg': reg_num, 
                        'value': reg_value
                    })
                    
            i += 1
        
        return True
    
    def analyze_instruction(self, instruction, encoding, reg_write_data):
        """Analyze individual instruction and update statistics"""
        self.statistics['total_instructions'] += 1
        
        # Check if compressed instruction (16-bit)
        if encoding <= 0xFFFF:
            self.statistics['compressed_instructions'] += 1
        
        # Count register writes
        if reg_write_data:
            self.statistics['register_writes'] += 1
            
        # Categorize instruction types
        instr_parts = instruction.split()
        if instr_parts:
            opcode = instr_parts[0]
            self.instruction_types[opcode] += 1
            
            # Detailed categorization
            self.categorize_instruction(opcode, instruction)
    
    def categorize_instruction(self, opcode, full_instruction):
        """Categorize instructions into functional groups"""
        
        # Branch instructions
        if opcode in ['beq', 'bne', 'blt', 'bge', 'bltu', 'bgeu', 'c.beqz', 'c.bnez']:
            self.statistics['branches'] += 1
            self.instruction_categories['branches'] += 1
            
        # Jump instructions
        elif opcode in ['jal', 'jalr', 'jr', 'j', 'c.j', 'c.jr', 'c.jal', 'c.jalr']:
            self.statistics['jumps'] += 1
            self.instruction_categories['jumps'] += 1
            
        # Load instructions
        elif opcode in ['lb', 'lh', 'lw', 'ld', 'lbu', 'lhu', 'lwu', 'c.lw', 'c.ld', 'c.lwsp', 'c.ldsp']:
            self.statistics['loads'] += 1
            self.statistics['memory_reads'] += 1
            self.instruction_categories['loads'] += 1
            
        # Store instructions
        elif opcode in ['sb', 'sh', 'sw', 'sd', 'c.sw', 'c.sd', 'c.swsp', 'c.sdsp']:
            self.statistics['stores'] += 1
            self.statistics['memory_writes'] += 1
            self.instruction_categories['stores'] += 1
            
        # Arithmetic and logical instructions
        elif opcode in ['add', 'sub', 'addi', 'and', 'or', 'xor', 'andi', 'ori', 'xori', 
                       'sll', 'srl', 'sra', 'slli', 'srli', 'srai', 'slt', 'slti', 
                       'sltu', 'sltiu', 'addw', 'subw', 'addiw', 'sllw', 'srlw', 'sraw',
                       'slliw', 'srliw', 'sraiw', 'c.add', 'c.sub', 'c.addi', 'c.and',
                       'c.or', 'c.xor', 'c.andi', 'c.slli', 'c.srli', 'c.srai', 'c.addi4spn',
                       'c.addi16sp', 'c.li', 'c.lui', 'c.mv', 'c.addiw', 'c.addw', 'c.subw']:
            self.statistics['arithmetic'] += 1
            self.instruction_categories['arithmetic'] += 1
            
        # CSR instructions
        elif opcode.startswith('csr') or opcode in ['csrr', 'csrw', 'csrs', 'csrc']:
            self.statistics['csrs'] += 1
            self.instruction_categories['csr'] += 1
            
        # System instructions
        elif opcode in ['ecall', 'ebreak', 'mret', 'sret', 'uret', 'wfi', 'sfence.vma']:
            self.statistics['system'] += 1
            self.instruction_categories['system'] += 1
            
        # Load upper immediate and PC-relative
        elif opcode in ['lui', 'auipc']:
            self.instruction_categories['immediate'] += 1
            
        # Multiplication and division
        elif opcode in ['mul', 'mulh', 'mulhsu', 'mulhu', 'div', 'divu', 'rem', 'remu',
                       'mulw', 'divw', 'divuw', 'remw', 'remuw']:
            self.instruction_categories['multiply_divide'] += 1
            
        # Atomic instructions
        elif opcode.startswith('amo') or opcode in ['lr.w', 'sc.w', 'lr.d', 'sc.d']:
            self.instruction_categories['atomic'] += 1
            
        # Floating point
        elif opcode.startswith('f'):
            self.instruction_categories['floating_point'] += 1
            
        # Default category
        else:
            self.instruction_categories['other'] += 1
    
    def detect_program_phases(self):
        """Detect different phases of program execution"""
        if not self.instructions:
            return {}
        
        phases = {
            'boot_setup': 0,
            'main_execution': 0,
            'cleanup': 0
        }
        
        # Simple heuristic: first 20% is boot/setup, last 10% is cleanup
        total_instrs = len(self.instructions)
        boot_threshold = int(total_instrs * 0.2)
        cleanup_threshold = int(total_instrs * 0.9)
        
        for i, instr in enumerate(self.instructions):
            if i < boot_threshold:
                phases['boot_setup'] += 1
            elif i >= cleanup_threshold:
                phases['cleanup'] += 1
            else:
                phases['main_execution'] += 1
        
        return phases
    
    def print_comprehensive_analysis(self):
        """Print comprehensive analysis results"""
        print("\n" + "="*80)
        print("🎯 COMPREHENSIVE RVFI TRACE ANALYSIS")
        print("="*80)
        
        # Basic statistics
        print(f"📁 File: {self.trace_file}")
        print(f"📄 Total lines processed: {self.statistics['total_lines']}")
        print(f"🔢 Instructions found: {self.statistics['total_instructions']}")
        print(f"📝 Register writes: {self.statistics['register_writes']}")
        
        if self.statistics['total_instructions'] > 0:
            comp_percent = (self.statistics['compressed_instructions'] / self.statistics['total_instructions']) * 100
            print(f"📦 Compressed instructions: {self.statistics['compressed_instructions']} ({comp_percent:.1f}%)")
        
        # Instruction type breakdown
        print("\n" + "="*60)
        print("📊 INSTRUCTION TYPE BREAKDOWN")
        print("="*60)
        
        categories = [
            ('branches', 'Branch Instructions'),
            ('jumps', 'Jump Instructions'),
            ('loads', 'Load Instructions'),
            ('stores', 'Store Instructions'),
            ('arithmetic', 'Arithmetic/Logic'),
            ('csr', 'CSR Instructions'),
            ('system', 'System Instructions'),
            ('multiply_divide', 'Multiply/Divide'),
            ('atomic', 'Atomic Instructions'),
            ('floating_point', 'Floating Point'),
            ('immediate', 'Immediate Instructions'),
            ('other', 'Other Instructions')
        ]
        
        for cat_key, cat_name in categories:
            count = self.instruction_categories[cat_key]
            if count > 0:
                percent = (count / self.statistics['total_instructions']) * 100
                print(f"  {cat_name:<20}: {count:>6} ({percent:>5.1f}%)")
        
        # Top instruction types
        print("\n" + "="*60)
        print("🏆 TOP 15 INSTRUCTION TYPES")
        print("="*60)
        
        sorted_types = sorted(self.instruction_types.items(), key=lambda x: x[1], reverse=True)
        for i, (opcode, count) in enumerate(sorted_types[:15]):
            percent = (count / self.statistics['total_instructions']) * 100
            print(f"{i+1:2d}. {opcode:<15} {count:>6} ({percent:>5.1f}%)")
        
        # Execution flow
        print("\n" + "="*60)
        print("🔄 EXECUTION FLOW (First 10 Instructions)")
        print("="*60)
        
        for i, instr in enumerate(self.instructions[:10]):
            pc_str = f"0x{instr['pc']:016x}"
            encoding_str = f"0x{instr['encoding']:08x}"
            reg_info = ""
            if instr['reg_write']:
                reg_info = f" -> x{instr['reg_write']['reg']}=0x{instr['reg_write']['value']:x}"
            print(f"{i+1:2d}. {pc_str} ({encoding_str}) {instr['instruction']}{reg_info}")
        
        # Program phases
        phases = self.detect_program_phases()
        print("\n" + "="*60)
        print("📈 PROGRAM EXECUTION PHASES")
        print("="*60)
        
        for phase, count in phases.items():
            if count > 0:
                percent = (count / self.statistics['total_instructions']) * 100
                print(f"  {phase.replace('_', ' ').title():<20}: {count:>6} ({percent:>5.1f}%)")
        
        # Memory access patterns
        print("\n" + "="*60)
        print("💾 MEMORY ACCESS PATTERNS")
        print("="*60)
        
        total_memory = self.statistics['memory_reads'] + self.statistics['memory_writes']
        if total_memory > 0:
            read_percent = (self.statistics['memory_reads'] / total_memory) * 100
            write_percent = (self.statistics['memory_writes'] / total_memory) * 100
            print(f"  Total memory accesses: {total_memory}")
            print(f"  Memory reads: {self.statistics['memory_reads']} ({read_percent:.1f}%)")
            print(f"  Memory writes: {self.statistics['memory_writes']} ({write_percent:.1f}%)")
        else:
            print("  No explicit memory accesses detected")
        
        # Register usage analysis
        if self.register_writes:
            print("\n" + "="*60)
            print("🏛️ REGISTER USAGE ANALYSIS")
            print("="*60)
            
            reg_usage = Counter([rw['reg'] for rw in self.register_writes])
            print(f"  Total register writes: {len(self.register_writes)}")
            print(f"  Unique registers written: {len(reg_usage)}")
            
            print("\n  Top 10 most written registers:")
            for reg, count in reg_usage.most_common(10):
                print(f"    x{reg:<2}: {count:>4} writes")
    
    def run_performance_analysis(self, max_width=4):
        """Run performance modeling analysis if available"""
        if not HAS_MODEL:
            print("\n⚠️  Performance modeling not available (model.py not found)")
            return
        
        print("\n" + "="*60)
        print("⚡ PERFORMANCE MODELING ANALYSIS")
        print("="*60)
        
        print(f"🔍 Testing issue/commit combinations from 1x1 to {max_width}x{max_width}...")
        
        results = {}
        total_combinations = max_width * max_width
        current = 0
        
        for issue in range(1, max_width + 1):
            for commit in range(1, max_width + 1):
                current += 1
                print(f"[{current}/{total_combinations}] Testing issue={issue}, commit={commit}...", end=" ")
                
                try:
                    model = Model(debug=False, issue=issue, commit=commit)
                    model.load_file(self.trace_file)
                    model.run()
                    
                    # Calculate metrics
                    n_cycles = count_cycles(model.retired)
                    n_instructions = len(model.retired)
                    ipc = n_instructions / n_cycles if n_cycles > 0 else 0
                    performance = 1000000 / n_cycles if n_cycles > 0 else 0
                    
                    results[(issue, commit)] = {
                        'cycles': n_cycles,
                        'instructions': n_instructions,
                        'ipc': ipc,
                        'performance': performance
                    }
                    
                    print(f"IPC: {ipc:.2f}, Performance: {performance:.2f}")
                    
                except Exception as e:
                    print(f"Error: {e}")
                    results[(issue, commit)] = {
                        'cycles': 0, 'instructions': 0, 'ipc': 0, 'performance': 0
                    }
        
        # Display results
        print("\n" + "="*60)
        print("📊 PERFORMANCE RESULTS SUMMARY")
        print("="*60)
        
        print(f"{'Config':<10} {'Cycles':<8} {'Instrs':<8} {'IPC':<6} {'Score':<8}")
        print("-" * 50)
        
        for (issue, commit), data in sorted(results.items()):
            config = f"{issue}x{commit}"
            print(f"{config:<10} {data['cycles']:<8} {data['instructions']:<8} "
                  f"{data['ipc']:<6.2f} {data['performance']:<8.2f}")
        
        # Find best configuration
        valid_results = {k: v for k, v in results.items() if v['performance'] > 0}
        if valid_results:
            best_config = max(valid_results.items(), key=lambda x: x[1]['performance'])
            best_issue, best_commit = best_config[0]
            best_perf = best_config[1]['performance']
            
            print(f"\n🏆 Best Configuration: Issue={best_issue}, Commit={best_commit}")
            print(f"🎯 Best Performance: {best_perf:.2f} Coremark/MHz")
            
            # Show improvement over baseline
            if (1, 1) in valid_results:
                baseline = valid_results[(1, 1)]['performance']
                improvement = (best_perf / baseline - 1) * 100
                print(f"📈 Improvement over 1x1: {improvement:.1f}%")
    
    def print_optimization_recommendations(self):
        """Print optimization recommendations based on analysis"""
        print("\n" + "="*60)
        print("💡 OPTIMIZATION RECOMMENDATIONS")
        print("="*60)
        
        total_instrs = self.statistics['total_instructions']
        
        # Instruction mix analysis
        branch_ratio = self.statistics['branches'] / total_instrs if total_instrs > 0 else 0
        load_ratio = self.statistics['loads'] / total_instrs if total_instrs > 0 else 0
        comp_ratio = self.statistics['compressed_instructions'] / total_instrs if total_instrs > 0 else 0
        
        print("🎯 Based on your instruction mix:")
        
        if branch_ratio > 0.15:
            print("  • High branch ratio detected - consider branch prediction optimizations")
        
        if load_ratio > 0.25:
            print("  • High load instruction ratio - focus on cache optimization")
        
        if comp_ratio < 0.7:
            print("  • Low compressed instruction usage - consider code density optimization")
        
        if self.statistics['memory_reads'] > self.statistics['memory_writes'] * 3:
            print("  • Read-heavy workload - optimize for cache prefetching")
        
        print("\n🔧 General recommendations:")
        print("  • Enable all available CPU extensions (C, M, A, F, D)")
        print("  • Use -O2 or -O3 compiler optimizations")
        print("  • Consider profile-guided optimization (PGO)")
        print("  • Analyze hot loops with detailed profiling")
        print("  • Consider vectorization for data-parallel workloads")
        
        print("\n🏗️ Hardware considerations:")
        print("  • Wider issue width may help with instruction-level parallelism")
        print("  • Larger caches can reduce memory stalls")
        print("  • Branch prediction improvements for control-intensive code")
        print("  • Out-of-order execution for better instruction scheduling")
    
    def print_technical_background(self):
        """Print technical background information"""
        print("\n" + "="*60)
        print("📚 TECHNICAL BACKGROUND")
        print("="*60)
        
        print("🔍 What is RVFI?")
        print("RVFI (RISC-V Formal Interface) is a standardized interface for")
        print("capturing detailed execution information from RISC-V processors:")
        print("  • Every instruction executed with PC and encoding")
        print("  • Register reads/writes with values and timing")
        print("  • Memory accesses with addresses and data")
        print("  • Exception and interrupt information")
        print("  • Timing information for performance analysis")
        
        print("\n🎯 CVA6 Processor:")
        print("CVA6 is a 6-stage, single-issue, in-order RISC-V processor:")
        print("  • Fetch, Decode, Issue, Execute, Commit stages")
        print("  • Support for RV32/RV64 with multiple extensions")
        print("  • Configurable caches and MMU")
        print("  • Designed for high-performance embedded applications")
        
        print("\n📊 Performance Metrics:")
        print("  • IPC (Instructions Per Cycle): Measure of processor efficiency")
        print("  • Coremark/MHz: Standardized performance benchmark")
        print("  • Issue width: Number of instructions issued per cycle")
        print("  • Commit width: Number of instructions committed per cycle")
        print("  • Cycle count: Total cycles needed for execution")
        
        print("\n🔬 This analysis helps with:")
        print("  • Performance optimization and bottleneck identification")
        print("  • Hardware verification and debugging")
        print("  • Microarchitecture exploration and design")
        print("  • Compiler optimization evaluation")
        print("  • Instruction-level profiling and analysis")
    
    def export_summary(self, output_file):
        """Export analysis summary to file"""
        print(f"\n💾 Exporting summary to {output_file}...")
        
        with open(output_file, 'w') as f:
            f.write("RVFI Trace Analysis Summary\n")
            f.write("="*40 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Trace file: {self.trace_file}\n\n")
            
            f.write("Basic Statistics:\n")
            f.write(f"  Total instructions: {self.statistics['total_instructions']}\n")
            f.write(f"  Compressed instructions: {self.statistics['compressed_instructions']}\n")
            f.write(f"  Register writes: {self.statistics['register_writes']}\n")
            f.write(f"  Memory reads: {self.statistics['memory_reads']}\n")
            f.write(f"  Memory writes: {self.statistics['memory_writes']}\n")
            f.write(f"  Branches: {self.statistics['branches']}\n")
            f.write(f"  Jumps: {self.statistics['jumps']}\n")
            f.write(f"  Arithmetic: {self.statistics['arithmetic']}\n")
            f.write(f"  CSR instructions: {self.statistics['csrs']}\n\n")
            
            f.write("Top 10 Instruction Types:\n")
            sorted_types = sorted(self.instruction_types.items(), key=lambda x: x[1], reverse=True)
            for i, (opcode, count) in enumerate(sorted_types[:10]):
                percent = (count / self.statistics['total_instructions']) * 100
                f.write(f"  {i+1}. {opcode}: {count} ({percent:.1f}%)\n")
            
            f.write("\nInstruction Categories:\n")
            for cat_key, count in self.instruction_categories.items():
                if count > 0:
                    percent = (count / self.statistics['total_instructions']) * 100
                    f.write(f"  {cat_key}: {count} ({percent:.1f}%)\n")
        
        print("✅ Summary exported successfully!")
        print(f"📄 Summary exported to: {output_file}")

def main():
    """Main function with command-line interface"""
    parser = argparse.ArgumentParser(
        description='Unified RVFI Trace Analyzer for CVA6',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 unified_analyzer.py trace.log
  python3 unified_analyzer.py trace.log --max-width 6
  python3 unified_analyzer.py trace.log --export summary.txt
  python3 unified_analyzer.py trace.log --skip-perf --debug
        """
    )
    
    parser.add_argument('trace_file', help='RVFI trace file to analyze')
    parser.add_argument('--max-width', type=int, default=4, 
                       help='Maximum issue/commit width for performance analysis (default: 4)')
    parser.add_argument('--export', type=str, metavar='FILE',
                       help='Export summary to specified file')
    parser.add_argument('--skip-perf', action='store_true',
                       help='Skip performance modeling analysis')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug output')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.trace_file):
        print(f"❌ Error: Trace file '{args.trace_file}' not found")
        sys.exit(1)
    
    # Create analyzer instance
    analyzer = UnifiedRVFIAnalyzer(args.trace_file, debug=args.debug)
    
    # Parse the trace file
    if not analyzer.parse_trace():
        sys.exit(1)
    
    # Print comprehensive analysis
    analyzer.print_comprehensive_analysis()
    
    # Run performance analysis if not skipped
    if not args.skip_perf:
        analyzer.run_performance_analysis(args.max_width)
    
    # Print optimization recommendations
    analyzer.print_optimization_recommendations()
    
    # Print technical background
    analyzer.print_technical_background()
    
    # Export summary if requested
    if args.export:
        analyzer.export_summary(args.export)
    
    print("\n" + "="*80)
    print("🎉 Analysis complete! Thank you for using the Unified RVFI Analyzer.")
    print("="*80)

if __name__ == "__main__":
    main()
