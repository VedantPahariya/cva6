#!/usr/bin/env python3

"""
Complete Execution Flow Analyzer for RVFI Traces
================================================

This tool prints the complete execution flow of all instructions in an RVFI trace,
including cycle numbers, program counter, encoding, instruction mnemonics, and 
register write information.

Features:
- Shows ALL instructions (not limited to first 20)
- Includes cycle numbers for each instruction
- Displays PC, encoding, instruction, and register writes
- Supports output to file for large traces
- Color-coded output for better readability (optional)
- Terminal output capture for better accessibility
- Performance model analysis with issue/commit matrix (NEW!)

NEW FEATURE: Performance Model Analysis
- Use --performance to run CVA6 performance model analysis
- Includes cycle count, Coremark/MHz performance metrics
- Event statistics (RAW hazards, structural hazards, branch hits/misses)
- Issue/Commit width performance matrix analysis
- Tests combinations from 1x1 to 3x3 issue/commit configurations
- Requires model.py to be available in the same directory

NEW FEATURE: Terminal Output Capture
- Use --save-terminal-output <file> to save all terminal output to a file
- This captures all console messages, progress updates, and analysis results
- Useful for documentation, debugging, or sharing analysis results
- Output file includes timestamps and clean formatting (no ANSI color codes)

Usage:
    python3 complete_execution_flow.py <trace_file> [options]
    
Examples:
    # Basic analysis with terminal output saved
    python3 complete_execution_flow.py trace.log --save-terminal-output analysis_log.txt
    
    # Run performance analysis and save results
    python3 complete_execution_flow.py trace.log --performance --save-terminal-output perf_analysis.txt
    
    # Save both execution flow and terminal output to separate files
    python3 complete_execution_flow.py trace.log --output flow.txt --save-terminal-output terminal.txt
"""

import sys
import os
import re
import argparse
from collections import defaultdict
from datetime import datetime
from datetime import datetime

class TerminalOutputCapture:
    """Class to capture all terminal output and save it to a file"""
    
    def __init__(self, output_file=None, also_print=True):
        self.output_file = output_file
        self.also_print = also_print
        self.captured_lines = []
        self.file_handle = None
        
        if self.output_file:
            try:
                self.file_handle = open(self.output_file, 'w', encoding='utf-8')
                self.write_header()
            except Exception as e:
                print(f"❌ Error opening output file '{self.output_file}': {e}")
                self.output_file = None
    
    def write_header(self):
        """Write header information to the output file"""
        if self.file_handle:
            header = f"""
{'='*80}
COMPLETE EXECUTION FLOW ANALYZER - TERMINAL OUTPUT LOG
{'='*80}
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Script: complete_execution_flow.py
{'='*80}

"""
            self.file_handle.write(header)
            self.file_handle.flush()
    
    def print(self, *args, **kwargs):
        """Custom print function that captures output to file and optionally prints to console"""
        # Convert arguments to string as print would
        message = ' '.join(str(arg) for arg in args)
        
        # Add to captured lines
        self.captured_lines.append(message)
        
        # Write to file if file handle exists
        if self.file_handle:
            # Remove ANSI color codes when writing to file
            clean_message = re.sub(r'\033\[[0-9;]*m', '', message)
            self.file_handle.write(clean_message + '\n')
            self.file_handle.flush()
        
        # Print to console if requested
        if self.also_print:
            print(*args, **kwargs)
    
    def close(self):
        """Close the output file and write footer"""
        if self.file_handle:
            footer = f"""

{'='*80}
END OF TERMINAL OUTPUT LOG
Generated {len(self.captured_lines)} lines of output
{'='*80}
"""
            self.file_handle.write(footer)
            self.file_handle.close()
            self.file_handle = None
    
    def get_captured_output(self):
        """Return all captured output as a single string"""
        return '\n'.join(self.captured_lines)

# Import the Model class from model.py to use the same cycle calculation logic
try:
    from model import Model, Instruction, EventKind, count_cycles, print_stats, issue_commit_graph
    HAS_MODEL = True
except ImportError:
    HAS_MODEL = False
    # Warning will be printed by the analyzer when it's created

class CompleteExecutionFlowAnalyzer:
    """Analyzer that shows complete execution flow with cycle information"""
    
    def __init__(self, trace_file, debug=False, output_capture=None):
        self.trace_file = trace_file
        self.debug = debug
        self.instructions = []
        self.register_writes = []
        self.output_capture = output_capture or TerminalOutputCapture()
        
    def print(self, *args, **kwargs):
        """Use output capture for printing"""
        self.output_capture.print(*args, **kwargs)
        
    def parse_trace(self):
        """Parse the RVFI trace file using model.py's simulation logic for cycle calculation"""
        self.print(f"📊 Parsing RVFI trace: {self.trace_file}")
        
        # Print warning if model.py not available
        if not HAS_MODEL:
            self.print("⚠️  Warning: Could not import model.py. Using fallback cycle calculation.")
        
        try:
            with open(self.trace_file, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            self.print(f"❌ Error: File '{self.trace_file}' not found")
            return False
        
        self.print(f"📄 Processing {len(lines)} lines...")
        
        if HAS_MODEL:
            # Use model.py's simulation logic to get correct cycle numbers
            self.print("🔄 Running pipeline simulation for accurate cycle calculation...")
            model = Model(debug=False, issue=2, commit=2)
            model.load_file(self.trace_file)
            model.run()
            
            # First, parse the original trace to get register write information
            reg_writes_by_pc = {}
            self._extract_register_writes(lines, reg_writes_by_pc)
            
            # Extract instruction information with correct cycle numbers from simulation
            instruction_count = 0
            for instr in model.retired:
                # Get the commit cycle from the last event (commit event)
                commit_event = instr.events[-1]
                cycle_number = commit_event.cycle
                
                instruction_count += 1
                
                # Look up register write data by PC address
                reg_write_data = reg_writes_by_pc.get(instr.address, None)
                if reg_write_data:
                    self.register_writes.append(reg_write_data)
                
                self.instructions.append({
                    'index': instruction_count,
                    'pc': instr.address,
                    'encoding': int(instr.hex_code, 16),
                    'instruction': instr.mnemo,
                    'reg_write': reg_write_data,
                    'cycle': cycle_number
                })
        else:
            # Fallback to original parsing logic if model.py not available
            self.print("⚠️  Using fallback cycle calculation (model.py not available)")
            self._parse_trace_fallback(lines)
        
        self.print(f"✅ Found {len(self.instructions)} instructions")
        return True
    
    def _extract_register_writes(self, lines, reg_writes_by_pc):
        """Extract register write information from trace lines"""
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for instruction lines followed by register write lines
            if line.startswith("core   0:"):
                instr_match = re.match(r'core\s+0:\s+0x([0-9a-fA-F]+)\s+\(0x([0-9a-fA-F]+)\)\s+(.+)', line)
                if instr_match:
                    pc = int(instr_match.group(1), 16)
                    
                    # Check if next line has register write information  
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        reg_match = re.match(r'(\d+)\s+0x([0-9a-fA-F]+)\s+\(0x([0-9a-fA-F]+)\)\s+x\s*(\d+)\s+0x([0-9a-fA-F]+)', next_line)
                        if reg_match:
                            cycle_number = int(reg_match.group(1))
                            reg_num = int(reg_match.group(4))
                            reg_value = int(reg_match.group(5), 16)
                            reg_writes_by_pc[pc] = {
                                'cycle': cycle_number, 
                                'reg': reg_num, 
                                'value': reg_value
                            }
                            i += 1  # Skip the register write line
            i += 1
    
    def _parse_trace_fallback(self, lines):
        """Fallback parsing method when model.py is not available"""
        i = 0
        instruction_count = 0
        current_cycle = 0  # Track cycles sequentially as instructions are processed
        
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
                    cycle_number = None
                    
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        reg_match = re.match(r'(\d+)\s+0x([0-9a-fA-F]+)\s+\(0x([0-9a-fA-F]+)\)\s+x\s*(\d+)\s+0x([0-9a-fA-F]+)', next_line)
                        if reg_match:
                            cycle_number = int(reg_match.group(1))
                            current_cycle = cycle_number  # Update current cycle from register write
                            reg_num = int(reg_match.group(4))
                            reg_value = int(reg_match.group(5), 16)
                            reg_write_data = {
                                'cycle': cycle_number, 
                                'reg': reg_num, 
                                'value': reg_value
                            }
                            self.register_writes.append(reg_write_data)
                            i += 1  # Skip the register write line
                    
                    # If no register write found, estimate cycle based on sequential execution
                    if cycle_number is None:
                        # Increment current cycle for instructions without register writes
                        current_cycle += 1
                        cycle_number = current_cycle
                    
                    instruction_count += 1
                    self.instructions.append({
                        'index': instruction_count,
                        'pc': pc,
                        'encoding': encoding,
                        'instruction': instruction,
                        'reg_write': reg_write_data,
                        'cycle': cycle_number
                    })
                    
            i += 1
    
    def print_complete_execution_flow(self, output_file=None, use_colors=False):
        """Print complete execution flow of all instructions"""
        
        # ANSI color codes for better readability
        colors = {
            'header': '\033[1;36m',    # Cyan bold
            'pc': '\033[1;33m',        # Yellow bold
            'encoding': '\033[0;35m',   # Magenta
            'instruction': '\033[0;32m', # Green
            'reg_write': '\033[1;31m',  # Red bold
            'cycle': '\033[1;34m',      # Blue bold
            'reset': '\033[0m'          # Reset
        } if use_colors else {k: '' for k in ['header', 'pc', 'encoding', 'instruction', 'reg_write', 'cycle', 'reset']}
        
        # Prepare output
        lines = []
        
        # Header
        header_line = f"{colors['header']}COMPLETE EXECUTION FLOW - ALL INSTRUCTIONS{colors['reset']}"
        separator = "=" * 100
        
        lines.append("")
        lines.append(separator)
        lines.append(header_line)
        lines.append(separator)
        lines.append(f"📁 Trace file: {self.trace_file}")
        lines.append(f"🔢 Total instructions: {len(self.instructions)}")
        lines.append("")
        
        # Column headers
        col_headers = f"{colors['header']}{'#':<6} {'Cycle':<8} {'PC':<18} {'Encoding':<12} {'Instruction':<30} {'Register Write':<20}{colors['reset']}"
        col_separator = "-" * 100
        
        lines.append(col_headers)
        lines.append(col_separator)
        
        # Instruction details
        for instr in self.instructions:
            # Format each field
            index_str = f"{colors['cycle']}{instr['index']:<6}{colors['reset']}"
            
            cycle_str = f"{colors['cycle']}{instr['cycle'] if instr['cycle'] is not None else 'N/A':<8}{colors['reset']}"
            
            pc_str = f"{colors['pc']}0x{instr['pc']:016x}{colors['reset']}"
            
            encoding_str = f"{colors['encoding']}0x{instr['encoding']:08x}{colors['reset']}"
            
            # Truncate long instructions for better formatting
            instr_text = instr['instruction']
            if len(instr_text) > 28:
                instr_text = instr_text[:25] + "..."
            instruction_str = f"{colors['instruction']}{instr_text:<30}{colors['reset']}"
            
            # Register write information
            reg_info = ""
            if instr['reg_write']:
                reg_info = f"{colors['reg_write']}x{instr['reg_write']['reg']} = 0x{instr['reg_write']['value']:x}{colors['reset']}"
            
            # Combine all fields
            line = f"{index_str} {cycle_str} {pc_str} {encoding_str} {instruction_str} {reg_info}"
            lines.append(line)
        
        # Summary statistics
        lines.append("")
        lines.append(separator)
        lines.append(f"{colors['header']}EXECUTION FLOW SUMMARY{colors['reset']}")
        lines.append(separator)
        
        # Calculate some statistics
        instructions_with_cycles = [i for i in self.instructions if i['cycle'] is not None]
        instructions_with_reg_writes = [i for i in self.instructions if i['reg_write'] is not None]
        
        if instructions_with_cycles:
            min_cycle = min(i['cycle'] for i in instructions_with_cycles)
            max_cycle = max(i['cycle'] for i in instructions_with_cycles)
            total_cycles = max_cycle - min_cycle + 1
            
            lines.append(f"⏱️  Cycle range: {min_cycle} to {max_cycle} (total: {total_cycles} cycles)")
            lines.append(f"📊 Instructions per cycle: {len(self.instructions) / total_cycles:.2f}")
        
        lines.append(f"📝 Instructions with register writes: {len(instructions_with_reg_writes)}")
        lines.append(f"🎯 Register write percentage: {len(instructions_with_reg_writes) / len(self.instructions) * 100:.1f}%")
        
        # PC address range
        min_pc = min(i['pc'] for i in self.instructions)
        max_pc = max(i['pc'] for i in self.instructions)
        lines.append(f"🗺️  PC address range: 0x{min_pc:016x} to 0x{max_pc:016x}")
        
        # Instruction encoding statistics
        compressed_count = sum(1 for i in self.instructions if i['encoding'] <= 0xFFFF)
        lines.append(f"📦 Compressed instructions: {compressed_count} ({compressed_count / len(self.instructions) * 100:.1f}%)")
        
        # Output results
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    # Remove color codes when writing to file
                    clean_lines = []
                    for line in lines:
                        # Remove ANSI color codes
                        clean_line = re.sub(r'\033\[[0-9;]*m', '', line)
                        clean_lines.append(clean_line)
                    f.write('\n'.join(clean_lines))
                    f.write('\n')
                self.print(f"✅ Complete execution flow saved to: {output_file}")
                self.print(f"📄 Wrote {len(lines)} lines to file")
            except Exception as e:
                self.print(f"❌ Error writing to file: {e}")
        else:
            # Print to console using custom print
            for line in lines:
                self.print(line)
    
    def print_model_performance_analysis(self):
        """Print comprehensive performance analysis using model.py logic"""
        if not HAS_MODEL:
            self.print("⚠️  Performance analysis requires model.py - skipping detailed analysis")
            return
        
        self.print("\n" + "="*80)
        self.print("CVA6 PERFORMANCE MODEL ANALYSIS")
        self.print("="*80)
        
        # Run single configuration analysis (issue=2, commit=2)
        self.print("Running single configuration (issue=2, commit=2):")
        self.print("="*60)
        
        model = Model(debug=False, issue=2, commit=2)
        model.load_file(self.trace_file)
        model.run()
        
        # Use count_cycles for consistency with demo_issue_commit.py
        cycles = count_cycles(model.retired)
        
        # Calculate and print statistics similar to model.py
        self._print_model_stats(model.retired, cycles)
        
        # Generate Issue/Commit Performance Analysis
        self.print("\n" + "="*60)
        self.print("Generating Issue/Commit Performance Analysis...")
        self._run_issue_commit_analysis(3)  # Test combinations from 1 to 3
    
    def _print_model_stats(self, retired_instructions, cycles):
        """Print statistics in model.py format"""
        from collections import defaultdict
        
        # Count events
        ecount = defaultdict(lambda: 0)
        for instr in retired_instructions:
            for e in instr.events:
                ecount[e.kind] += 1
        
        n_instr = len(retired_instructions)
        n_cycles = cycles
        
        # Print statistics in the same format as model.py
        self._print_data("cycle number", n_cycles)
        self._print_data("Coremark/MHz", 1000000 / n_cycles)
        self._print_data("instruction number", n_instr)
        
        for ek, count in ecount.items():
            percentage = f"{100 * count / n_instr:.2f}%"
            self._print_data(f"{ek.name}/instr", percentage)
    
    def _print_data(self, name, value, ts=24, sep='='):
        """Print 'name = data' with alignment of the '=' (matching model.py format)"""
        spaces = ' ' * (ts - len(name))
        self.print(f"{name}{spaces} {sep} {value}")
    
    def _run_issue_commit_analysis(self, max_width=3):
        """Run issue/commit width performance analysis"""
        self.print(f"Testing issue/commit combinations from 1 to {max_width}...")
        
        # Initialize scores matrix and detailed results storage
        scores = [[0 for _ in range(max_width + 1)] for _ in range(max_width + 1)]
        detailed_results = {}
        
        total_combinations = max_width * max_width
        current = 0
        
        for issue in range(1, max_width + 1):
            for commit in range(1, max_width + 1):
                current += 1
                
                # Run model with specific issue/commit configuration
                model = Model(debug=False, issue=issue, commit=commit)
                model.load_file(self.trace_file)
                model.run()
                
                # Calculate metrics using count_cycles (same as demo_issue_commit.py)
                cycles = count_cycles(model.retired)
                n_instructions = len(model.retired)
                ipc = n_instructions / cycles if cycles > 0 else 0
                performance = 1000000 / cycles if cycles > 0 else 0
                
                # Store detailed results
                detailed_results[(issue, commit)] = {
                    'cycles': cycles,
                    'instructions': n_instructions,
                    'ipc': ipc,
                    'performance': performance,
                    'retired': model.retired
                }
                
                # Calculate performance score (Coremark/MHz)
                scores[issue][commit] = performance
                
                self.print(f"[{current}/{total_combinations}] Testing issue={issue}, commit={commit}... Performance: {performance:.2f}")
        
        # self.print(f"\nFinal scores matrix:")
        # self.print(scores)
        
        # Display enhanced analysis
        self._display_performance_matrix(scores, max_width)
        self._display_results_summary(detailed_results, max_width)
        self._display_improvement_analysis(detailed_results, max_width)
        self._display_hazard_analysis(detailed_results, max_width)
    
    def _display_results_summary(self, detailed_results, max_width):
        """Display detailed results summary similar to demo_issue_commit.py"""
        self.print("\n" + "=" * 60)
        self.print("RESULTS SUMMARY")
        self.print("=" * 60)
        
        # Print header
        self.print(f"{'Config':<12} {'Cycles':<8} {'Instrs':<8} {'IPC':<6} {'Perf':<8}")
        self.print("-" * 50)
        
        # Print data for each configuration
        for issue in range(1, max_width + 1):
            for commit in range(1, max_width + 1):
                config = f"{issue}x{commit}"
                data = detailed_results[(issue, commit)]
                self.print(f"{config:<12} {data['cycles']:<8} {data['instructions']:<8} "
                          f"{data['ipc']:<6.2f} {data['performance']:<8.2f}")
        
        # Find best configuration
        best_config = max(detailed_results.items(), key=lambda x: x[1]['performance'])
        best_issue, best_commit = best_config[0]
        best_perf = best_config[1]['performance']
        
        self.print(f"\nBest Configuration: Issue={best_issue}, Commit={best_commit}")
        self.print(f"Best Performance: {best_perf:.2f}")
    
    def _display_improvement_analysis(self, detailed_results, max_width):
        """Display improvement analysis comparing all configurations to baseline"""
        self.print("\n" + "=" * 60)
        self.print("IMPROVEMENT ANALYSIS")
        self.print("=" * 60)
        
        baseline = detailed_results[(1, 1)]['performance']
        self.print(f"Baseline (1x1): {baseline:.2f}")
        self.print()
        
        for issue in range(1, max_width + 1):
            for commit in range(1, max_width + 1):
                if issue == 1 and commit == 1:
                    continue
                
                data = detailed_results[(issue, commit)]
                improvement = (data['performance'] / baseline - 1) * 100
                self.print(f"Issue={issue}, Commit={commit}: {improvement:+.1f}% improvement")
    
    def _display_hazard_analysis(self, detailed_results, max_width):
        """Display hazard analysis for different configurations"""
        self.print("\n" + "=" * 60)
        self.print("HAZARD ANALYSIS")
        self.print("=" * 60)
        
        # Select specific configurations to analyze (similar to demo)
        configs_to_analyze = [(1, 1), (2, 2), (3, 3)]
        
        for issue, commit in configs_to_analyze:
            if issue <= max_width and commit <= max_width:
                self.print(f"\nConfiguration: Issue={issue}, Commit={commit}")
                self.print("-" * 40)
                
                data = detailed_results[(issue, commit)]
                retired_instructions = data['retired']
                total_instructions = len(retired_instructions)
                
                # Count different types of events
                event_counts = {}
                
                for instr in retired_instructions:
                    for event in instr.events:
                        event_type = event.kind.name
                        event_counts[event_type] = event_counts.get(event_type, 0) + 1
                
                # Display hazard statistics in the same format as demo
                hazard_types = ['RAW', 'WAW', 'STRUCT', 'BMISS', 'BHIT']
                
                for hazard_type in hazard_types:
                    count = event_counts.get(hazard_type, 0)
                    percentage = (count / total_instructions * 100) if total_instructions > 0 else 0
                    self.print(f"  {hazard_type:<8}: {count:>4} ({percentage:>5.1f}%)")

    def _display_performance_matrix(self, scores, max_width):
        """Display the issue/commit performance matrix"""
        self.print("\nIssue/Commit Performance Matrix:")
        self.print("="*50)
        
        # Print header
        header_line = "Issue\\Commit"
        for j in range(max_width + 1):
            header_line += f"\t{j:8.1f}"
        self.print(header_line)
        
        # Print data rows
        for i, row in enumerate(scores):
            if i <= max_width:
                line = f"{i:9d}"
                for j in range(len(row)):
                    if j <= max_width:
                        line += f"\t{row[j]:8.2f}"
                self.print(line)
    
    def print_execution_statistics(self):
        """Print instruction type distribution"""
        self.print("\n" + "="*60)
        self.print("INSTRUCTION TYPE DISTRIBUTION")
        self.print("="*60)
        
        # Instruction type analysis
        instruction_types = defaultdict(int)
        for instr in self.instructions:
            opcode = instr['instruction'].split()[0]
            instruction_types[opcode] += 1
        
        self.print(f"\n🏆 Top 15 most frequent instructions:")
        sorted_types = sorted(instruction_types.items(), key=lambda x: x[1], reverse=True)
        for i, (opcode, count) in enumerate(sorted_types[:15]):
            percentage = (count / len(self.instructions)) * 100
            self.print(f"  {i+1:2d}. {opcode:<15} {count:>6} ({percentage:>5.1f}%)")
        
        # Cycle distribution analysis
        cycles_with_counts = defaultdict(int)
        for instr in self.instructions:
            if instr['cycle'] is not None:
                cycles_with_counts[instr['cycle']] += 1
        
        if cycles_with_counts:
            self.print(f"\n⏱️  Cycle distribution:")
            max_instrs_per_cycle = max(cycles_with_counts.values())
            min_instrs_per_cycle = min(cycles_with_counts.values())
            avg_instrs_per_cycle = sum(cycles_with_counts.values()) / len(cycles_with_counts)
            
            self.print(f"  Max instructions per cycle: {max_instrs_per_cycle}")
            self.print(f"  Min instructions per cycle: {min_instrs_per_cycle}")
            self.print(f"  Avg instructions per cycle: {avg_instrs_per_cycle:.2f}")
        
        # Register usage analysis
        if self.register_writes:
            reg_usage = defaultdict(int)
            for reg_write in self.register_writes:
                reg_usage[reg_write['reg']] += 1
            
            self.print(f"\n🏛️  Register usage (top 10):")
            sorted_regs = sorted(reg_usage.items(), key=lambda x: x[1], reverse=True)
            for i, (reg, count) in enumerate(sorted_regs[:10]):
                self.print(f"  {i+1:2d}. x{reg:<2} : {count:>4} writes")

def main():
    """Main function with command-line interface"""
    parser = argparse.ArgumentParser(
        description='Complete Execution Flow Analyzer for RVFI Traces',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 complete_execution_flow.py trace.log
  python3 complete_execution_flow.py trace.log --output execution_flow.txt
  python3 complete_execution_flow.py trace.log --colors --stats
  python3 complete_execution_flow.py trace.log --performance
  python3 complete_execution_flow.py trace.log --performance --save-terminal-output analysis.txt
  python3 complete_execution_flow.py trace.log -o flow.txt --no-stats
  python3 complete_execution_flow.py trace.log --save-terminal-output terminal_log.txt
  python3 complete_execution_flow.py trace.log --save-terminal-output terminal_log.txt --output flow.txt
        """
    )
    
    parser.add_argument('trace_file', help='RVFI trace file to analyze')
    parser.add_argument('-o', '--output', type=str, metavar='FILE',
                       help='Output file to save execution flow (default: print to console)')
    parser.add_argument('--save-terminal-output', type=str, metavar='FILE',
                       help='Save all terminal output to a file for better accessibility')
    parser.add_argument('--colors', action='store_true',
                       help='Use colored output (only for console display)')
    parser.add_argument('--stats', action='store_true',
                       help='Print additional execution statistics')
    parser.add_argument('--no-stats', action='store_true',
                       help='Skip printing execution statistics')
    parser.add_argument('--performance', action='store_true',
                       help='Run performance model analysis (requires model.py)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug output')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.trace_file):
        print(f"❌ Error: Trace file '{args.trace_file}' not found")
        sys.exit(1)
    
    # Set up terminal output capture if requested
    output_capture = None
    if args.save_terminal_output:
        output_capture = TerminalOutputCapture(
            output_file=args.save_terminal_output, 
            also_print=True  # Still show output on console
        )
        output_capture.print(f"🖥️  Terminal output will be saved to: {args.save_terminal_output}")
    
    # Create analyzer instance with output capture
    analyzer = CompleteExecutionFlowAnalyzer(
        args.trace_file, 
        debug=args.debug, 
        output_capture=output_capture
    )
    
    # Parse the trace file
    if not analyzer.parse_trace():
        if output_capture:
            output_capture.close()
        sys.exit(1)
    
    # Run performance model analysis if requested
    if args.performance:
        analyzer.print_model_performance_analysis()
    
    # Print additional statistics if requested
    if args.stats or (not args.no_stats and not args.output):
        analyzer.print_execution_statistics()
    
    # Print complete execution flow
    analyzer.print_complete_execution_flow(
        output_file=args.output, 
        use_colors=args.colors and not args.output  # Only use colors for console output
    )
    
    analyzer.print("\n" + "="*80)
    analyzer.print("🎉 Complete execution flow analysis finished!")
    analyzer.print("="*80)
    
    # Close output capture and provide summary
    if output_capture:
        output_capture.close()
        print(f"\n💾 Terminal output saved to: {args.save_terminal_output}")
        print(f"📊 Captured {len(output_capture.captured_lines)} lines of terminal output")

if __name__ == "__main__":
    main()
