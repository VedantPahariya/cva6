# Basic startup code for RISC-V tests
.global _start
_start:
    la sp, _stack_top
    call main
    li a0, 0
    li a7, 93  # exit syscall
    ecall
