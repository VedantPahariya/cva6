#!/usr/bin/env python3

"""
Test script to verify the isa.py fixes
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from isa import Instr
    print("✓ Successfully imported Instr from isa.py")
    
    # Test if OP-FP is now supported
    if 'OP-FP' in Instr.type_of_base:
        print("✓ OP-FP instruction type is now supported")
    else:
        print("✗ OP-FP instruction type is still missing")
    
    # Test other floating-point instruction types
    fp_types = ['LOAD-FP', 'STORE-FP', 'MADD', 'MSUB', 'NMSUB', 'NMADD', 'AMO', 'MISC-MEM', 'OP-IMM-32']
    
    for fp_type in fp_types:
        if fp_type in Instr.type_of_base:
            print(f"✓ {fp_type} instruction type is supported")
        else:
            print(f"✗ {fp_type} instruction type is missing")
    
    print(f"\nTotal instruction types supported: {len(Instr.type_of_base)}")
    
    # Test creating a simple instruction to see if the fix works
    try:
        # Create a test instruction (this is a dummy 32-bit instruction)
        test_instr = Instr(0x007302b3, "add t0, t1, t2")  # Example R-type instruction
        print(f"✓ Successfully created test instruction: {test_instr}")
        
        # Test the base() method
        base = test_instr.base()
        print(f"✓ Instruction base type: {base}")
        
        # Test the fields() method
        fields = test_instr.fields()
        print(f"✓ Successfully got instruction fields: {type(fields).__name__}")
        
    except Exception as e:
        print(f"✗ Error testing instruction creation: {e}")
    
except ImportError as e:
    print(f"✗ Failed to import isa.py: {e}")
except Exception as e:
    print(f"✗ Unexpected error: {e}")

print("\n" + "="*60)
print("SUMMARY OF FIXES APPLIED:")
print("="*60)
print("1. Added 'OP-FP': Rtype - Floating-point operations")
print("2. Added 'LOAD-FP': Itype - Floating-point loads")
print("3. Added 'STORE-FP': Stype - Floating-point stores")
print("4. Added 'MADD': Rtype - Fused multiply-add")
print("5. Added 'MSUB': Rtype - Fused multiply-subtract")
print("6. Added 'NMSUB': Rtype - Negated fused multiply-subtract")
print("7. Added 'NMADD': Rtype - Negated fused multiply-add")
print("8. Added 'AMO': Rtype - Atomic memory operations")
print("9. Added 'MISC-MEM': Itype - Memory ordering (fence)")
print("10. Added 'OP-IMM-32': Itype - 32-bit immediate operations")
print("\nThese fixes should resolve the KeyError: 'OP-FP' issue.")
