// Copyright 2024 CVA6-ARA Integration
// SPDX-License-Identifier: Apache-2.0 WITH SHL-2.0
//
// CVA6-ARA Testbench Wrapper
// Simple testbench for CVA6+ARA integration testing

module cva6_ara_tb_wrapper
  import ariane_pkg::*;
  import config_pkg::*;
#(
  parameter config_pkg::cva6_cfg_t CVA6Cfg = config_pkg::cva6_cfg
);

  // Clock and reset
  logic clk;
  logic rst_n;
  
  // Boot configuration
  logic [CVA6Cfg.XLEN-1:0] boot_addr;
  logic [CVA6Cfg.XLEN-1:0] hart_id;
  
  // Interrupt signals
  logic [1:0] irq;
  logic       ipi;
  logic       time_irq;
  logic       debug_req;
  
  // AXI Memory Interface
  axi_req_t  axi_req;
  axi_rsp_t  axi_rsp;

  // ===============================================
  // Clock Generation
  // ===============================================
  
  initial begin
    clk = 0;
    forever #5ns clk = ~clk; // 100MHz clock
  end

  // ===============================================
  // Reset Generation
  // ===============================================
  
  initial begin
    rst_n = 0;
    #100ns;
    rst_n = 1;
    $display("Reset released at time %t", $time);
  end

  // ===============================================
  // Test Configuration
  // ===============================================
  
  initial begin
    boot_addr  = 64'h8000_0000;  // Boot address
    hart_id    = 64'h0;          // Hart ID
    irq        = 2'b00;          // No interrupts
    ipi        = 1'b0;           // No IPI
    time_irq   = 1'b0;           // No timer interrupt
    debug_req  = 1'b0;           // No debug request
  end

  // ===============================================
  // CVA6-ARA Top Instance
  // ===============================================
  
  cva6_ara_top #(
    .CVA6Cfg      ( CVA6Cfg      ),
    .cvxif_req_t  ( cvxif_req_t  ),
    .cvxif_resp_t ( cvxif_resp_t ),
    .axi_ar_chan_t( axi_ar_chan_t),
    .axi_aw_chan_t( axi_aw_chan_t),
    .axi_w_chan_t ( axi_w_chan_t ),
    .axi_req_t    ( axi_req_t    ),
    .axi_rsp_t    ( axi_rsp_t    )
  ) i_dut (
    .clk_i        ( clk        ),
    .rst_ni       ( rst_n      ),
    .boot_addr_i  ( boot_addr  ),
    .hart_id_i    ( hart_id    ),
    .irq_i        ( irq        ),
    .ipi_i        ( ipi        ),
    .time_irq_i   ( time_irq   ),
    .debug_req_i  ( debug_req  ),
    .axi_req_o    ( axi_req    ),
    .axi_resp_i   ( axi_rsp    )
  );

  // ===============================================
  // Simple Memory Model
  // ===============================================
  
  axi_sim_mem #(
    .AddrWidth    ( CVA6Cfg.AxiAddrWidth ),
    .DataWidth    ( CVA6Cfg.AxiDataWidth ),
    .IdWidth      ( CVA6Cfg.AxiIdWidth   ),
    .UserWidth    ( CVA6Cfg.AxiUserWidth ),
    .axi_req_t    ( axi_req_t            ),
    .axi_rsp_t    ( axi_rsp_t            )
  ) i_mem (
    .clk_i        ( clk      ),
    .rst_ni       ( rst_n    ),
    .axi_req_i    ( axi_req  ),
    .axi_rsp_o    ( axi_rsp  )
  );

  // ===============================================
  // Test Monitoring
  // ===============================================
  
  // Monitor vector instruction execution
  always @(posedge clk) begin
    if (rst_n && i_dut.cvxif_req.req_valid && i_dut.cvxif_resp.req_ready) begin
      $display("Vector instruction executed at time %t: 0x%08x", 
               $time, i_dut.cvxif_req.req.instr);
    end
  end

  // ===============================================
  // Test Sequence
  // ===============================================
  
  initial begin
    $display("=== CVA6+ARA Integration Test ===");
    $display("Configuration:");
    $display("  XLEN: %d", CVA6Cfg.XLEN);
    $display("  VLEN: %d", CVA6Cfg.VLEN);
    $display("  Vector support: %s", CVA6Cfg.RVV ? "Enabled" : "Disabled");
    
    // Wait for reset
    wait (rst_n);
    @(posedge clk);
    
    // Run for a reasonable time
    #10000ns;
    
    $display("=== Test completed at time %t ===", $time);
    $finish;
  end

  // ===============================================
  // Assertions
  // ===============================================
  
  // Check that vector extension is enabled
  initial begin
    assert (CVA6Cfg.RVV) else 
      $error("Vector extension not enabled in configuration");
  end
  
  // Check that VLEN is reasonable
  initial begin
    assert (CVA6Cfg.VLEN >= 64 && CVA6Cfg.VLEN <= 1024) else 
      $error("Invalid VLEN configuration: %d", CVA6Cfg.VLEN);
  end

endmodule
