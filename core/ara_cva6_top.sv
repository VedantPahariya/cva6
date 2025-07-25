// Copyright 2024 CVA6-ARA Integration
// SPDX-License-Identifier: Apache-2.0 WITH SHL-2.0
//
// CVA6-ARA Integration Top Module
// This module integrates the CVA6 scalar core with the ARA vector unit

module cva6_ara_top
  import ariane_pkg::*;
  import config_pkg::*;
#(
  parameter config_pkg::cva6_cfg_t CVA6Cfg = config_pkg::cva6_cfg,
  parameter type cvxif_req_t = logic,
  parameter type cvxif_resp_t = logic,
  parameter type axi_ar_chan_t = logic,
  parameter type axi_aw_chan_t = logic,
  parameter type axi_w_chan_t = logic,
  parameter type axi_req_t = logic,
  parameter type axi_rsp_t = logic
) (
  input  logic                     clk_i,
  input  logic                     rst_ni,
  
  // CVA6 Boot address
  input  logic [CVA6Cfg.XLEN-1:0]  boot_addr_i,
  input  logic [CVA6Cfg.XLEN-1:0]  hart_id_i,
  
  // Interrupt inputs
  input  logic [1:0]               irq_i,
  input  logic                     ipi_i,
  input  logic                     time_irq_i,
  input  logic                     debug_req_i,
  
  // AXI Memory Interface
  output axi_req_t                 axi_req_o,
  input  axi_rsp_t                 axi_resp_i
);

  // CVA6-ARA Interface Signals
  cvxif_req_t  cvxif_req;
  cvxif_resp_t cvxif_resp;
  
  // ARA specific signals
  logic        ara_req_valid;
  logic        ara_req_ready;
  logic        ara_resp_valid;
  logic        ara_resp_ready;
  
  // AXI signals for vector memory operations
  axi_req_t    ara_axi_req;
  axi_rsp_t    ara_axi_resp;
  axi_req_t    cva6_axi_req;
  axi_rsp_t    cva6_axi_resp;

  // ===============================================
  // CVA6 Scalar Core Instance
  // ===============================================
  cva6 #(
    .CVA6Cfg          ( CVA6Cfg        ),
    .cvxif_req_t      ( cvxif_req_t    ),
    .cvxif_resp_t     ( cvxif_resp_t   ),
    .axi_ar_chan_t    ( axi_ar_chan_t  ),
    .axi_aw_chan_t    ( axi_aw_chan_t  ),
    .axi_w_chan_t     ( axi_w_chan_t   ),
    .axi_req_t        ( axi_req_t      ),
    .axi_rsp_t        ( axi_rsp_t      )
  ) i_cva6 (
    .clk_i            ( clk_i          ),
    .rst_ni           ( rst_ni         ),
    .boot_addr_i      ( boot_addr_i    ),
    .hart_id_i        ( hart_id_i      ),
    .irq_i            ( irq_i          ),
    .ipi_i            ( ipi_i          ),
    .time_irq_i       ( time_irq_i     ),
    .debug_req_i      ( debug_req_i    ),
    .cvxif_req_o      ( cvxif_req      ),
    .cvxif_resp_i     ( cvxif_resp     ),
    .axi_req_o        ( cva6_axi_req   ),
    .axi_resp_i       ( cva6_axi_resp  )
  );

  // ===============================================
  // ARA Vector Unit Instance  
  // ===============================================
  // Note: This is a placeholder for the actual ARA instance
  // You'll need to update this with the actual ARA module interface
  // when integrating with the real ARA repository
  
  ara_system #(
    // ARA configuration parameters
    .NrLanes          ( 4              ),  // Number of vector lanes
    .VLEN             ( CVA6Cfg.VLEN   ),  // Vector length
    .FPUSupport       ( CVA6Cfg.RVF    ),  // Floating-point support
    .FPExtSupport     ( CVA6Cfg.RVD    ),  // Double precision support
    .AxiDataWidth     ( CVA6Cfg.AxiDataWidth ),
    .AxiAddrWidth     ( CVA6Cfg.AxiAddrWidth ),
    .axi_ar_chan_t    ( axi_ar_chan_t  ),
    .axi_aw_chan_t    ( axi_aw_chan_t  ),
    .axi_w_chan_t     ( axi_w_chan_t   ),
    .axi_req_t        ( axi_req_t      ),
    .axi_rsp_t        ( axi_rsp_t      )
  ) i_ara (
    .clk_i            ( clk_i          ),
    .rst_ni           ( rst_ni         ),
    
    // Accelerator interface from CVA6
    .acc_req_valid_i  ( cvxif_req.req_valid     ),
    .acc_req_ready_o  ( cvxif_resp.req_ready    ),
    .acc_req_i        ( cvxif_req.req           ),
    .acc_resp_valid_o ( cvxif_resp.resp_valid   ),
    .acc_resp_ready_i ( cvxif_req.resp_ready    ),
    .acc_resp_o       ( cvxif_resp.resp         ),
    
    // AXI interface for vector memory operations
    .axi_req_o        ( ara_axi_req    ),
    .axi_resp_i       ( ara_axi_resp   )
  );

  // ===============================================
  // AXI Interconnect for Memory Operations
  // ===============================================
  // Simple mux for demonstration - in real implementation,
  // you'd use a proper AXI crossbar/interconnect
  
  always_comb begin
    // Default assignments
    axi_req_o = cva6_axi_req;
    cva6_axi_resp = axi_resp_i;
    ara_axi_resp = '0;
    
    // Vector memory operations take priority
    if (ara_axi_req.aw_valid || ara_axi_req.ar_valid || ara_axi_req.w_valid) begin
      axi_req_o = ara_axi_req;
      ara_axi_resp = axi_resp_i;
      cva6_axi_resp = '0;
    end
  end

  // ===============================================
  // Vector CSR Integration
  // ===============================================
  // Handle vector control and status registers
  // This would typically be integrated with CVA6's CSR unit
  
  // Vector length register (vl)
  logic [CVA6Cfg.XLEN-1:0] vl_q, vl_d;
  // Vector type register (vtype)  
  logic [CVA6Cfg.XLEN-1:0] vtype_q, vtype_d;
  // Vector start register (vstart)
  logic [CVA6Cfg.XLEN-1:0] vstart_q, vstart_d;
  
  always_ff @(posedge clk_i or negedge rst_ni) begin
    if (!rst_ni) begin
      vl_q     <= '0;
      vtype_q  <= '0;
      vstart_q <= '0;
    end else begin
      vl_q     <= vl_d;
      vtype_q  <= vtype_d;
      vstart_q <= vstart_d;
    end
  end

  // ===============================================
  // Debug and Performance Monitoring
  // ===============================================
  
  // Vector instruction counters
  logic [63:0] vector_inst_count;
  logic [63:0] vector_cycles;
  
  always_ff @(posedge clk_i or negedge rst_ni) begin
    if (!rst_ni) begin
      vector_inst_count <= '0;
      vector_cycles     <= '0;
    end else begin
      if (cvxif_req.req_valid && cvxif_resp.req_ready) begin
        vector_inst_count <= vector_inst_count + 1;
      end
      vector_cycles <= vector_cycles + 1;
    end
  end

  // ===============================================
  // Assertions and Checks
  // ===============================================
  
  // Check that vector instructions are properly handled
  `ifdef SIMULATION
    always @(posedge clk_i) begin
      if (cvxif_req.req_valid && !cvxif_resp.req_ready) begin
        $display("Warning: Vector instruction request not accepted by ARA");
      end
    end
  `endif

endmodule

// ===============================================
// ARA System Placeholder Module
// ===============================================
// This is a placeholder for the actual ARA system
// Replace this with the real ARA module when available

module ara_system #(
  parameter int unsigned NrLanes = 4,
  parameter int unsigned VLEN = 256,
  parameter bit FPUSupport = 1,
  parameter bit FPExtSupport = 1,
  parameter int unsigned AxiDataWidth = 64,
  parameter int unsigned AxiAddrWidth = 64,
  parameter type axi_ar_chan_t = logic,
  parameter type axi_aw_chan_t = logic,
  parameter type axi_w_chan_t = logic,
  parameter type axi_req_t = logic,
  parameter type axi_rsp_t = logic
) (
  input  logic                     clk_i,
  input  logic                     rst_ni,
  
  // Accelerator interface
  input  logic                     acc_req_valid_i,
  output logic                     acc_req_ready_o,
  input  logic [31:0]              acc_req_i,
  output logic                     acc_resp_valid_o,
  input  logic                     acc_resp_ready_i,
  output logic [63:0]              acc_resp_o,
  
  // AXI interface
  output axi_req_t                 axi_req_o,
  input  axi_rsp_t                 axi_resp_i
);

  // Placeholder implementation
  // In real integration, this would be replaced with:
  // - Actual ARA top module
  // - Proper interface connections
  // - Vector register file
  // - Vector functional units
  
  assign acc_req_ready_o = 1'b1;
  assign acc_resp_valid_o = acc_req_valid_i;
  assign acc_resp_o = {32'h0, acc_req_i};  // Echo back for now
  assign axi_req_o = '0;  // No memory operations in placeholder
  
  // TODO: Replace with actual ARA instantiation
  // ara_top i_ara_top (
  //   .clk_i(...),
  //   .rst_ni(...),
  //   // ... other connections
  // );

endmodule
