OUTPUT_ARCH(riscv)
ENTRY(_start)
MEMORY {
  RAM : ORIGIN = 0x80000000, LENGTH = 64M
}
SECTIONS {
  .text : { *(.text*) } > RAM
  .data : { *(.data*) } > RAM
  .bss  : { *(.bss*) } > RAM
  _stack_top = ORIGIN(RAM) + LENGTH(RAM);
}
