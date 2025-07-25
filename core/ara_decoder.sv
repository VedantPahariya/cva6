// Copyright 2023 ETH Zurich and University of Bologna.
// Solderpad Hardware License, Version 0.51, see LICENSE for details.
// SPDX-License-Identifier: SHL-0.51

// ARA Vector Accelerator First Pass Decoder for CVA6
// This decoder identifies RISC-V vector instructions and forwards them to ARA

module cva6_accel_first_pass_decoder
  import ariane_pkg::*;
#(
    parameter config_pkg::cva6_cfg_t CVA6Cfg = '0,
    parameter type scoreboard_entry_t = logic
) (
    input  logic              [31:0] instruction_i,           // instruction from IF
    input  riscv::xs_t               fs_i,                    // floating point extension status
    input  riscv::xs_t               vs_i,                    // vector extension status
    output logic                     is_accel_o,              // is an accelerator instruction
    output scoreboard_entry_t        instruction_o,           // predecoded instruction
    output logic                     illegal_instr_o,         // is an illegal instruction
    output logic                     is_control_flow_instr_o  // is a control flow instruction
);

  // RISC-V Vector Extension opcodes
  localparam logic [6:0] OpcodeVec       = 7'b1010111;  // Vector arithmetic instructions
  localparam logic [6:0] OpcodeVecLoad   = 7'b0000111;  // Vector load instructions  
  localparam logic [6:0] OpcodeVecStore  = 7'b0100111;  // Vector store instructions

  // Decode instruction opcode
  logic [6:0] opcode;
  assign opcode = instruction_i[6:0];

  // Check if this is a vector instruction
  logic is_vector_instr;
  assign is_vector_instr = (opcode == OpcodeVec) || 
                          (opcode == OpcodeVecLoad) || 
                          (opcode == OpcodeVecStore);

  // Check if vector extensions are enabled and vector unit is accessible
  logic vector_enabled;
  assign vector_enabled = (vs_i != riscv::Off) && CVA6Cfg.RVV;

  // Main decoder logic
  assign is_accel_o = is_vector_instr && vector_enabled;
  assign illegal_instr_o = is_vector_instr && !vector_enabled;
  assign is_control_flow_instr_o = 1'b0;  // Vector instructions are not control flow

  // Prepare instruction for accelerator
  always_comb begin
    instruction_o = '0;
    
    if (is_accel_o) begin
      // Basic instruction setup for vector operations
      instruction_o.pc = '0;  // Will be filled by CVA6
      instruction_o.trans_id = '0;  // Will be assigned by CVA6
      instruction_o.fu = ACCEL;  // Send to accelerator functional unit
      instruction_o.op = ADD;  // Placeholder - ARA will decode the actual operation
      instruction_o.rs1 = instruction_i[19:15];  // Source register 1
      instruction_o.rs2 = instruction_i[24:20];  // Source register 2  
      instruction_o.rd = instruction_i[11:7];    // Destination register
      instruction_o.use_imm = 1'b0;
      instruction_o.use_pc = 1'b0;
      instruction_o.is_compressed = 1'b0;
    end
  end

endmodule : cva6_accel_first_pass_decoder
