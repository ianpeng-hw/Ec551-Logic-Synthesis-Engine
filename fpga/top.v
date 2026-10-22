module top(
    input [6:0] sw,
    output led,
    output [6:0] seg,
    output [3:0] an,
    output dp
);

    wire logic_out;

    // Instance of generated Boolean circuit
    structurallogic u_logic (
        .A(sw[0]),
        .B(sw[1]),
        .C(sw[2]),
        .D(sw[3]),
        .E(sw[4]),
        .F(sw[5]),
        .G(sw[6]),
        .out(logic_out)
    );

    // LED follows the Boolean result
    assign led = logic_out;

    // Enable rightmost seven-segment digit
    assign an = 4'b1110;

    // Turn off decimal point
    assign dp = 1'b1;

    // Display 1 or 0
    assign seg = logic_out ? 7'b1111001 : 7'b1000000;

endmodule
