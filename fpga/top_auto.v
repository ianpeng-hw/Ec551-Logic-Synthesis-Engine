// top_auto.v - Basys 3 wrapper with an automatic truth-table sweep.
//
// Two modes, chosen with the leftmost switch sw[15]:
//   sw[15] = 0  manual: the inputs A B C come from switches sw[2:0]
//   sw[15] = 1  auto:   a counter steps through m = 0, 1, ..., 7 once per
//                       second, so the board plays the whole truth table
//
// Outputs:
//   led[15]    F (the output of the generated circuit)
//   led[14]    on in auto mode
//   led[2:0]   the current inputs A B C
//   7-segment  the current minterm number m (rightmost digit)
//
// Vivado files for this version:
//   fpga/top_auto.v              (this wrapper, set as the top module)
//   fpga/generated_logic_auto.v  (structurallogic, made by our verilog_gen.py
//                                 from examples/example.blif: F = A'B + AC)
//   fpga/basys3_auto.xdc         (pins)
// Any other 3-input module from the "verilog" command works too:
//   structurallogic(A, B, C, <output>)
// Add only ONE file that defines structurallogic to the project.
//
// AI usage: written with help from Claude (Anthropic).

module top_auto #(
    parameter TICKS = 100_000_000      // clock cycles per step: 100 MHz -> 1 second
) (
    input         clk,                 // 100 MHz board clock
    input  [15:0] sw,
    output [15:0] led,
    output [6:0]  seg,
    output [3:0]  an,
    output        dp
);

    // ---- 1. a counter that ticks once per second -------------------------
    reg [26:0] timer  = 0;             // counts 0 .. TICKS-1
    reg [2:0]  m_auto = 0;             // minterm number used in auto mode

    always @(posedge clk) begin
        if (sw[15] == 1'b0) begin
            // manual mode: hold the counter at 0,
            // so auto mode always starts from m = 0
            timer  <= 0;
            m_auto <= 0;
        end else if (timer == TICKS - 1) begin
            timer  <= 0;
            m_auto <= m_auto + 1;      // 7 + 1 wraps back to 0
        end else begin
            timer  <= timer + 1;
        end
    end

    // ---- 2. choose where the inputs come from ----------------------------
    wire [2:0] m;
    assign m = sw[15] ? m_auto : sw[2:0];

    // ---- 3. the generated circuit ----------------------------------------
    wire F;
    //                        A     B     C     output
    structurallogic u_logic (m[2], m[1], m[0], F);

    // ---- 4. LEDs ---------------------------------------------------------
    assign led[15]   = F;
    assign led[14]   = sw[15];         // auto mode indicator
    assign led[13:3] = 11'b0;
    assign led[2:0]  = m;              // current inputs A B C

    // ---- 5. 7-segment: show m on the rightmost digit ---------------------
    // Segments and digit enables are active-low (0 = on).
    // seg = {g, f, e, d, c, b, a}
    reg [6:0] digit;
    always @(*) begin
        case (m)
            3'd0:    digit = 7'b1000000;
            3'd1:    digit = 7'b1111001;
            3'd2:    digit = 7'b0100100;
            3'd3:    digit = 7'b0110000;
            3'd4:    digit = 7'b0011001;
            3'd5:    digit = 7'b0010010;
            3'd6:    digit = 7'b0000010;
            default: digit = 7'b1111000;   // 7
        endcase
    end

    assign seg = digit;
    assign an  = 4'b1110;              // only the rightmost digit is on
    assign dp  = 1'b1;                 // decimal point off

endmodule
