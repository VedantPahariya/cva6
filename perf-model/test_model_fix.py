#!/usr/bin/env python3

"""
Test the fixed model.py with a small trace sample
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Create a small sample trace to test
sample_trace = """core   0: 0x0000000000010000 (0x00100413) li      s0, 1
3 0x0000000000010000 (0x00100413) x 8 0x0000000000000001
core   0: 0x0000000000010004 (0x01f41413) slli    s0, s0, 31
3 0x0000000000010004 (0x01f41413) x 8 0x0000000080000000
core   0: 0x0000000000010008 (0xf1402573) csrrs   a0, mhartid, zero
3 0x0000000000010008 (0xf1402573) x10 0x0000000000000000
core   0: 0x000000000001000c (0x00000597) auipc   a1, 0x0
3 0x000000000001000c (0x00000597) x11 0x000000000001000c
core   0: 0x0000000000010010 (0x07458593) addi    a1, a1, 116
3 0x0000000000010010 (0x07458593) x11 0x0000000000010080
"""

# Write sample trace to a temporary file
sample_file = "sample_trace.log"
with open(sample_file, 'w') as f:
    f.write(sample_trace)

print("Testing the fixed CVA6 performance model...")
print("="*50)

try:
    # Import the model
    from model import Model
    print("✓ Successfully imported Model class")
    
    # Create a model instance with the sample trace
    model = Model(sample_file, debug=True)
    print("✓ Successfully created Model instance")
    
    # Try to run a few cycles
    print("✓ Running model for a few cycles...")
    try:
        # Run just a few cycles to test
        for cycle in range(5):
            model.run_cycle(cycle)
            print(f"  Cycle {cycle}: OK")
        print("✓ Model executed successfully without KeyError!")
        
    except KeyError as e:
        print(f"✗ KeyError still exists: {e}")
    except Exception as e:
        print(f"✗ Other error during execution: {e}")
    
except ImportError as e:
    print(f"✗ Failed to import model: {e}")
except Exception as e:
    print(f"✗ Unexpected error: {e}")
finally:
    # Clean up
    if os.path.exists(sample_file):
        os.remove(sample_file)

print("\n" + "="*60)
print("ISSUE DIAGNOSIS:")
print("="*60)
print("The original problem was:")
print("  KeyError: 'OP-FP' in isa.py line 501")
print("")
print("Root cause:")
print("  The type_of_base dictionary was missing entries for")
print("  floating-point and other instruction types that appear")
print("  in the RISC-V instruction table but weren't mapped to")
print("  their corresponding format classes.")
print("")
print("Solution applied:")
print("  Added missing instruction type mappings:")
print("  - OP-FP, MADD, MSUB, NMSUB, NMADD → Rtype")
print("  - LOAD-FP, MISC-MEM, OP-IMM-32 → Itype") 
print("  - STORE-FP → Stype")
print("  - AMO → Rtype")
print("")
print("This should resolve the model.py execution issue.")
