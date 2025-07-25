// Copyright 2023 ETH Zurich and University of Bologna.
// Solderpad Hardware License, Version 0.51, see LICENSE for details.
// SPDX-License-Identifier: SHL-0.51

// CVA6 + ARA Integration Wrapper
// This module integrates the CVA6 scalar core with the ARA vector unit

module cva6_ara_wrapper
  import ariane_pkg::*;
#(
    parameter config_pkg::cva6_cfg_t CVA6Cfg = config_pkg::cva6_cfg_empty,
    parameter type axi_ar_chan_t = logic,
    parameter type axi_aw_chan_t = logic,
    parameter type axi_w_chan_t = logic,
    parameter type axi_req_t = logic,
    parameter type axi_rsp_t = logic
) (
    // Clock and Reset
    input logic clk_i,
    input logic rst_ni,
    
    // Boot address
    input logic [CVA6Cfg.VLEN-1:0] boot_addr_i,
    
    // Interrupt inputs
    input logic [1:0] irq_i,
    input logic ipi_i,
    input logic time_irq_i,
    input logic debug_req_i,
    
    // AXI Interface
    output axi_req_t axi_req_o,
    input  axi_rsp_t axi_rsp_i,
    
    // RVFI Interface (for verification)
    output logic [CVA6Cfg.NrCommitPorts-1:0] rvfi_valid_o,
    output logic [CVA6Cfg.NrCommitPorts-1:0][63:0] rvfi_order_o,
    output logic [CVA6Cfg.NrCommitPorts-1:0][CVA6Cfg.ILEN-1:0] rvfi_insn_o,
    output logic [CVA6Cfg.NrCommitPorts-1:0] rvfi_trap_o,
    output logic [CVA6Cfg.NrCommitPorts-1:0] rvfi_halt_o,
    output logic [CVA6Cfg.NrCommitPorts-1:0] rvfi_intr_o,
    output logic [CVA6Cfg.NrCommitPorts-1:0][1:0] rvfi_mode_o,
    output logic [CVA6Cfg.NrCommitPorts-1:0][1:0] rvfi_ixl_o,
    output logic [CVA6Cfg.NrCommitPorts-1:0][4:0] rvfi_rs1_addr_o,
    output logic [CVA6Cfg.NrCommitPorts-1:0][4:0] rvfi_rs2_addr_o,
    output logic [CVA6Cfg.NrCommitPorts-1:0][CVA6Cfg.XLEN-1:0] rvfi_rs1_rdata_o,
    output logic [CVA6Cfg.NrCommitPorts-1:0][CVA6Cfg.XLEN-1:0] rvfi_rs2_rdata_o,
    output logic [CVA6Cfg.NrCommitPorts-1:0][4:0] rvfi_rd_addr_o,
    output logic [CVA6Cfg.NrCommitPorts-1:0][CVA6Cfg.XLEN-1:0] rvfi_rd_wdata_o,
    output logic [CVA6Cfg.NrCommitPorts-1:0][CVA6Cfg.VLEN-1:0] rvfi_pc_rdata_o,
    output logic [CVA6Cfg.NrCommitPorts-1:0][CVA6Cfg.VLEN-1:0] rvfi_pc_wdata_o,
    output logic [CVA6Cfg.NrCommitPorts-1:0][CVA6Cfg.XLEN-1:0] rvfi_mem_addr_o,
    output logic [CVA6Cfg.NrCommitPorts-1:0][3:0] rvfi_mem_rmask_o,
    output logic [CVA6Cfg.NrCommitPorts-1:0][3:0] rvfi_mem_wmask_o,
    output logic [CVA6Cfg.NrCommitPorts-1:0][CVA6Cfg.XLEN-1:0] rvfi_mem_rdata_o,
    output logic [CVA6Cfg.NrCommitPorts-1:0][CVA6Cfg.XLEN-1:0] rvfi_mem_wdata_o
);

  // CVA6-ARA Interface signals
  logic        acc_req_valid;
  logic        acc_req_ready;
  logic [31:0] acc_req_instr;
  logic [4:0]  acc_req_rs1;
  logic [4:0]  acc_req_rs2;
  logic [4:0]  acc_req_rd;
  logic [CVA6Cfg.XLEN-1:0] acc_req_rs1_data;
  logic [CVA6Cfg.XLEN-1:0] acc_req_rs2_data;
  
  logic        acc_resp_valid;
  logic        acc_resp_ready;
  logic [4:0]  acc_resp_rd;
  logic [CVA6Cfg.XLEN-1:0] acc_resp_data;
  logic        acc_resp_error;

  // ARA-specific AXI interface (you'll need to connect this to main AXI)
  axi_req_t ara_axi_req;
  axi_rsp_t ara_axi_rsp;

  // CVA6 Core Instance
  cva6 #(
    .CVA6Cfg(CVA6Cfg),
    .axi_ar_chan_t(axi_ar_chan_t),
    .axi_aw_chan_t(axi_aw_chan_t), 
    .axi_w_chan_t(axi_w_chan_t),
    .axi_req_t(axi_req_t),
    .axi_rsp_t(axi_rsp_t)
  ) i_cva6 (
    .clk_i(clk_i),
    .rst_ni(rst_ni),
    .boot_addr_i(boot_addr_i),
    .hart_id_i('0),
    .irq_i(irq_i),
    .ipi_i(ipi_i),
    .time_irq_i(time_irq_i),
    .debug_req_i(debug_req_i),
    .axi_req_o(axi_req_o),
    .axi_resp_i(axi_rsp_i),
    .rvfi_valid_o(rvfi_valid_o),
    .rvfi_order_o(rvfi_order_o),
    .rvfi_insn_o(rvfi_insn_o),
    .rvfi_trap_o(rvfi_trap_o),
    .rvfi_halt_o(rvfi_halt_o),
    .rvfi_intr_o(rvfi_intr_o),
    .rvfi_mode_o(rvfi_mode_o),
    .rvfi_ixl_o(rvfi_ixl_o),
    .rvfi_rs1_addr_o(rvfi_rs1_addr_o),
    .rvfi_rs2_addr_o(rvfi_rs2_addr_o),
    .rvfi_rs1_rdata_o(rvfi_rs1_rdata_o),
    .rvfi_rs2_rdata_o(rvfi_rs2_rdata_o),
    .rvfi_rd_addr_o(rvfi_rd_addr_o),
    .rvfi_rd_wdata_o(rvfi_rd_wdata_o),
    .rvfi_pc_rdata_o(rvfi_pc_rdata_o),
    .rvfi_pc_wdata_o(rvfi_pc_wdata_o),
    .rvfi_mem_addr_o(rvfi_mem_addr_o),
    .rvfi_mem_rmask_o(rvfi_mem_rmask_o),
    .rvfi_mem_wmask_o(rvfi_mem_wmask_o),
    .rvfi_mem_rdata_o(rvfi_mem_rdata_o),
    .rvfi_mem_wdata_o(rvfi_mem_wdata_o)
  );

  // ARA Vector Unit Instance (placeholder - you'll need actual ARA module)
  /*
  ara #(
    // ARA parameters will go here
  ) i_ara (
    .clk_i(clk_i),
    .rst_ni(rst_ni),
    
    // Accelerator interface from CVA6
    .acc_req_valid_i(acc_req_valid),
    .acc_req_ready_o(acc_req_ready),
    .acc_req_instr_i(acc_req_instr),
    .acc_req_rs1_i(acc_req_rs1),
    .acc_req_rs2_i(acc_req_rs2),
    .acc_req_rd_i(acc_req_rd),
    .acc_req_rs1_data_i(acc_req_rs1_data),
    .acc_req_rs2_data_i(acc_req_rs2_data),
    
    .acc_resp_valid_o(acc_resp_valid),
    .acc_resp_ready_i(acc_resp_ready),
    .acc_resp_rd_o(acc_resp_rd),
    .acc_resp_data_o(acc_resp_data),
    .acc_resp_error_o(acc_resp_error),
    
    // AXI interface for vector memory operations
    .axi_req_o(ara_axi_req),
    .axi_resp_i(ara_axi_rsp)
  );
  */

  // For now, create a simple ARA stub that acknowledges requests
  // This will be replaced with actual ARA integration
  assign acc_req_ready = 1'b1;
  assign acc_resp_valid = acc_req_valid;
  assign acc_resp_rd = acc_req_rd;
  assign acc_resp_data = acc_req_rs1_data + acc_req_rs2_data; // Simple add for testing
  assign acc_resp_error = 1'b0;
  
  // Connect ARA AXI to main AXI (simple passthrough for now)
  assign ara_axi_req = '0;
  assign ara_axi_rsp = axi_rsp_i;

endmodule : cva6_ara_wrapper
