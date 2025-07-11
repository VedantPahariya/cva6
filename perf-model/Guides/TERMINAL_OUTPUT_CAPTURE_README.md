# Terminal Output Capture Feature for complete_execution_flow.py

## Overview

The `complete_execution_flow.py` script has been enhanced with a new **Terminal Output Capture** feature that allows you to save all terminal output (progress messages, analysis results, statistics, etc.) to a file for better accessibility and documentation.

## New Feature: `--save-terminal-output`

### What it does:
- Captures ALL terminal output from the script execution
- Saves it to a specified file with proper formatting
- Includes timestamps and clean formatting (ANSI color codes are automatically removed)
- Still displays output on the console (unless redirected)
- Useful for documentation, debugging, sharing results, and long-running analyses

### Usage:

```bash
# Basic usage - save terminal output to a file
python3 complete_execution_flow.py trace.log --save-terminal-output terminal_log.txt

# Save both execution flow and terminal output to separate files
python3 complete_execution_flow.py trace.log --output flow.txt --save-terminal-output terminal_log.txt

# Include statistics and save terminal output
python3 complete_execution_flow.py trace.log --save-terminal-output terminal_log.txt --stats

# Use with colors (colors won't appear in the saved file, only on console)
python3 complete_execution_flow.py trace.log --save-terminal-output terminal_log.txt --colors
```

## File Structure

The terminal output file includes:

1. **Header Section**:
   - Timestamp of when the analysis was run
   - Script name and version info
   - Separator lines for clarity

2. **All Terminal Messages**:
   - Progress updates (parsing, processing, etc.)
   - Complete execution flow output
   - Summary statistics
   - Error messages (if any)

3. **Footer Section**:
   - End timestamp
   - Total number of output lines captured

## Example Output File

```
================================================================================
COMPLETE EXECUTION FLOW ANALYZER - TERMINAL OUTPUT LOG
================================================================================
Generated on: 2025-07-08 17:59:03
Script: complete_execution_flow.py
================================================================================

🖥️  Terminal output will be saved to: terminal_log.txt
📊 Parsing RVFI trace: sample_trace.log
📄 Processing 6 lines...
🔄 Running pipeline simulation for accurate cycle calculation...
✅ Found 3 instructions
COMPLETE EXECUTION FLOW - ALL INSTRUCTIONS
====================================================================================================
📁 Trace file: sample_trace.log
🔢 Total instructions: 3

#      Cycle    PC                 Encoding     Instruction                    Register Write      
----------------------------------------------------------------------------------------------------
1      2        0x0000000080000000 0x00000297 auipc t0, 0x0                  x5 = 0x80000000
2      3        0x0000000080000004 0x02028293 addi t0, t0, 32                x5 = 0x80000020
3      4        0x0000000080000008 0x30529073 csrw mtvec, t0                 x0 = 0x0

[... rest of the analysis output ...]

================================================================================
END OF TERMINAL OUTPUT LOG
Generated 42 lines of output
================================================================================
```

## Use Cases

### 1. **Documentation**
- Keep records of analysis runs for reports
- Document performance analysis workflows
- Create audit trails for research projects

### 2. **Debugging**
- Capture error messages and progress information
- Share debug output with team members
- Compare outputs between different runs

### 3. **Automated Pipelines**
- Save logs from batch processing jobs
- Monitor analysis progress in automated systems
- Archive results for later review

### 4. **Long-running Analyses**
- Review output after completion without scrolling through terminal history
- Resume work on large datasets
- Share results via file rather than copy-paste

## Technical Implementation

### New Classes Added:

#### `TerminalOutputCapture`
- Manages output capture to file
- Handles ANSI color code removal for clean file output
- Provides timestamped headers and footers
- Supports both file output and console display

### Modified Components:

#### `CompleteExecutionFlowAnalyzer`
- Added `output_capture` parameter to constructor
- All `print()` calls now route through custom `print()` method
- Maintains backward compatibility

#### Command Line Interface
- Added `--save-terminal-output FILE` argument
- Updated help text and examples
- Enhanced error handling

## Backward Compatibility

- **100% backward compatible** - existing scripts and commands work unchanged
- New feature is entirely optional
- No performance impact when not used
- All existing functionality preserved

## File Format

- **Encoding**: UTF-8
- **Line endings**: Unix-style (\\n)
- **Color codes**: Automatically stripped from file output
- **Formatting**: Clean, readable text suitable for documentation

## Example Commands

```bash
# Simple analysis with terminal logging
python3 complete_execution_flow.py my_trace.log --save-terminal-output analysis_log.txt

# Full analysis with separate output files
python3 complete_execution_flow.py my_trace.log \\
    --output execution_details.txt \\
    --save-terminal-output terminal_session.txt \\
    --stats

# Debug mode with terminal capture
python3 complete_execution_flow.py my_trace.log \\
    --save-terminal-output debug_log.txt \\
    --debug \\
    --stats

# Colored console output with clean file logging
python3 complete_execution_flow.py my_trace.log \\
    --save-terminal-output clean_log.txt \\
    --colors
```

## File Size Considerations

- Terminal output files are typically small (1-5 KB for most analyses)
- Large traces may generate larger log files
- No built-in size limits - adjust based on your needs
- Files use efficient text format without binary data

## Troubleshooting

### Permission Issues
```bash
# Ensure write permissions to output directory
chmod 755 /path/to/output/directory
```

### File Already Exists
- The script will overwrite existing files
- Use unique filenames or timestamps if needed

### Large Output Files
- Monitor disk space for very large traces
- Consider using compression for archival

## Benefits

1. **Better Accessibility**: All output saved in easily accessible text files
2. **Documentation**: Perfect for creating analysis reports
3. **Debugging**: Easier to share and review error messages
4. **Automation**: Essential for batch processing and CI/CD pipelines
5. **Archival**: Keep permanent records of analysis runs
6. **Collaboration**: Share complete analysis sessions with team members

This enhancement makes the `complete_execution_flow.py` tool more professional and suitable for production environments while maintaining its ease of use for interactive analysis.
