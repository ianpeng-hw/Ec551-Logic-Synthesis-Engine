"""Generate Basys 3 automatic/manual FPGA wrapper and pin constraints. 

Usage: generate_basys3_auto_files(BooleanFunction(...))
The generated top_auto.v instantiates an existing `structurallogic` module.
"""

# Used AI to help out
from pathlib import Path
from string import Template

# Digilent Basys 3 master constraints, SW0 .. SW15.
SWITCH_PINS = [
    "V17", "V16", "W16", "W17", "W15", "V15", "W14", "W13",
    "V2", "T3", "T2", "R3", "W2", "U1", "T1", "R2"
]

# LD0 .. LD15.
LED_PINS = [
    "U16", "E19", "U19", "V19", "W18", "U15", "U14", "V14",
    "V13", "V3", "W3", "U3", "P3", "N3", "P1", "L1"
]

# Seven-segment A .. G and digit AN0 .. AN3.
SEGMENT_PINS = ["W7", "W6", "U8", "V8", "U5", "V5", "U7"]
DIGIT_PINS = ["U2", "U4", "V4", "W4"]


def _constraint(port, pin):
    return (
        f"set_property -dict {{ PACKAGE_PIN {pin} IOSTANDARD LVCMOS33 }} "
        f"[get_ports {{{port}}}]"
    )


TOP_TEMPLATE = Template("""`timescale 1ns / 1ps
// Auto-generated Basys 3 manual/automatic truth-table sweep.
// SW15 = 0: manually set inputs using SW0 .. SW(N-1).
// SW15 = 1: cycle through all 2^N input combinations once per second.
// LD15 = function output, LD14 = auto-mode indicator.
// LD13 .. LD0 = current input combination (binary).
// Seven-segment display = current input number (hexadecimal).

module top_auto #(
    parameter integer TICKS = 100_000_000  // 100 MHz clock -> 1 second
)(
    input clk,
    input [15:0] sw,
    output [15:0] led,
    output reg [6:0] seg,
    output reg [3:0] an,
    output dp
);
    localparam integer N = $N;

    // Automatic N-bit counter. Each auto-mode entry restarts at zero.
    reg [26:0] timer = 27'd0;
    reg [N-1:0] m_auto = {N{1'b0}};

    always @(posedge clk) begin
        if (!sw[15]) begin
            timer <= 27'd0;
            m_auto <= {N{1'b0}};
        end else if (timer == TICKS - 1) begin
            timer <= 27'd0;
            m_auto <= m_auto + 1'b1;  // wraps from 2^N - 1 to 0
        end else begin
            timer <= timer + 1'b1;
        end
    end

    // Current inputs: either switch positions or automatic counter.
    wire [N-1:0] m = sw[15] ? m_auto : sw[N-1:0];

    // Generated structural Boolean circuit.
    wire logic_out;
    structurallogic u_logic (
$CONNECTIONS
    );

    assign led[15] = logic_out;
    assign led[14] = sw[15];
    assign led[13:0] = {{(14-N){1'b0}}, m};

    // Multiplex seven-segment digits for more than four input bits.
    // Hex 0-9, A-F. N <= 4 uses rightmost digit only.
    reg [16:0] refresh = 17'd0;
    always @(posedge clk) refresh <= refresh + 1'b1;

    wire [15:0] display_value = {{(16-N){1'b0}}, m};
    wire [1:0] scan_digit = (N <= 4) ? 2'b00 : refresh[16:15];
    reg [3:0] nibble;

    always @(*) begin
        case (scan_digit)
            2'b00: begin
                an = 4'b1110;
                nibble = display_value[3:0];
            end
            2'b01: begin
                an = (N > 4) ? 4'b1101 : 4'b1111;
                nibble = display_value[7:4];
            end
            2'b10: begin
                an = (N > 8) ? 4'b1011 : 4'b1111;
                nibble = display_value[11:8];
            end
            default: begin
                an = (N > 12) ? 4'b0111 : 4'b1111;
                nibble = display_value[15:12];
            end
        endcase
    end

    // Active-low seven-segment patterns: {g,f,e,d,c,b,a}.
    always @(*) begin
        case (nibble)
            4'h0: seg = 7'b1000000;
            4'h1: seg = 7'b1111001;
            4'h2: seg = 7'b0100100;
            4'h3: seg = 7'b0110000;
            4'h4: seg = 7'b0011001;
            4'h5: seg = 7'b0010010;
            4'h6: seg = 7'b0000010;
            4'h7: seg = 7'b1111000;
            4'h8: seg = 7'b0000000;
            4'h9: seg = 7'b0010000;
            4'hA: seg = 7'b0001000;
            4'hB: seg = 7'b0000011;
            4'hC: seg = 7'b1000110;
            4'hD: seg = 7'b0100001;
            4'hE: seg = 7'b0000110;
            default: seg = 7'b0001110;  // F
        endcase
    end

    assign dp = 1'b1;  // decimal point off
endmodule
""")


def generate_basys3_auto_files(f, folder="fpga"):
    """Generate top_auto.v and basys3_auto.xdc for a BooleanFunction.

    This function does not generate the structural logic module itself;
    use generate_verilog(f, filepath="fpga/generated_logic_auto.v") too.
    """
    variables = list(f.var_names)
    n = len(variables)

    # SW15 selects manual or auto mode. LD15 = result, LD14 = mode,
    # leaving LD0 .. LD13 for at most fourteen input bits.
    if not 1 <= n <= 14:
        raise ValueError("Auto mode supports 1 to 14 Boolean inputs.")
    if f.output_name in variables:
        raise ValueError("Output name conflicts with an input variable.")

    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)

    # The first variable corresponds to the most significant input bit,
    # matching BooleanFunction's minterm numbering.
    connections = [
        f"        .{variable}(m[{n-1-i}]),"
        for i, variable in enumerate(variables)
    ]
    connections.append(f"        .{f.output_name}(logic_out)")
    top_text = TOP_TEMPLATE.substitute(
        N=n,
        CONNECTIONS="\n".join(connections),
    )
    top_path = folder / "top_auto.v"
    top_path.write_text(top_text, encoding="utf-8")

    xdc_lines = [
        "# Basys 3 automatic/manual demo pin constraints",
        "# Clock: 100 MHz oscillator",
        _constraint("clk", "W5"),
        "create_clock -add -name sys_clk_pin -period 10.00 -waveform {0 5} [get_ports clk]",
        "",
        "# Switches SW0 through SW15",
    ]
    for i, pin in enumerate(SWITCH_PINS):
        xdc_lines.append(_constraint(f"sw[{i}]", pin))

    xdc_lines.extend(["", "# LEDs LD0 through LD15"])
    for i, pin in enumerate(LED_PINS):
        xdc_lines.append(_constraint(f"led[{i}]", pin))

    xdc_lines.extend(["", "# Seven-segment display: A through G"])
    for i, pin in enumerate(SEGMENT_PINS):
        xdc_lines.append(_constraint(f"seg[{i}]", pin))

    xdc_lines.extend(["", "# Decimal point", _constraint("dp", "V7")])
    xdc_lines.extend(["", "# Digit selects AN0 through AN3"])
    for i, pin in enumerate(DIGIT_PINS):
        xdc_lines.append(_constraint(f"an[{i}]", pin))

    xdc_lines.extend([
        "", "# Basys 3 configuration settings",
        "set_property CONFIG_VOLTAGE 3.3 [current_design]",
        "set_property CFGBVS VCCO [current_design]",
    ])
    xdc_path = folder / "basys3_auto.xdc"
    xdc_path.write_text("\n".join(xdc_lines) + "\n", encoding="utf-8")

    return top_path, xdc_path
