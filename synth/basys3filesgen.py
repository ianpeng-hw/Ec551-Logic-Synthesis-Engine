
from pathlib import Path

# Official Basys 3 switch pins, from SW0 to SW15
SWITCH_PINS = [
    "V17", "V16", "W16", "W17",
    "W15", "V15", "W14", "W13",
    "V2", "T3", "T2", "R3",
    "W2", "U1", "T1", "R2"
]

# Seven-segment display pins, segments A through G
SEGMENT_PINS = ["W7", "W6", "U8", "V8", "U5", "V5", "U7"]

# Digit enable pins, AN0 through AN3
DIGIT_PINS = ["U2", "U4", "V4", "W4"]


def generate_basys3_files(f, folder="fpga"):

    variables = f.var_names
    output_name = f.output_name
    n = len(variables)

    # Basys 3 supports up to 16 switch inputs
    if n < 1 or n > 16:
        raise ValueError("Basys 3 supports 1 to 16 switch inputs.")

    if output_name in variables:
        raise ValueError("Output name conflicts with an input variable.")

    # Create output folder
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)

    # ==========================================
    # Generate top.v
    # ==========================================

    top_lines = [
        "module top(",
        f"    input [{n - 1}:0] sw,",
        "    output led,",
        "    output [6:0] seg,",
        "    output [3:0] an,",
        "    output dp",
        ");",
        "",
        "    wire logic_out;",
        "",
        "    // Instance of generated Boolean circuit",
        "    structurallogic u_logic ("
    ]

    # Connect each variable to a corresponding switch
    for i, variable in enumerate(variables):
        top_lines.append(f"        .{variable}(sw[{i}]),")

    # Connect circuit output to internal wire
    top_lines.append(f"        .{output_name}(logic_out)")
    top_lines.append("    );")

    # LED and seven-segment display
    top_lines.extend([
        "",
        "    // LED follows the Boolean result",
        "    assign led = logic_out;",
        "",
        "    // Enable rightmost seven-segment digit",
        "    assign an = 4'b1110;",
        "",
        "    // Turn off decimal point",
        "    assign dp = 1'b1;",
        "",
        "    // Display 1 or 0",
        "    assign seg = logic_out ? 7'b1111001 : 7'b1000000;",
        "",
        "endmodule"
    ])

    top_path = folder / "top.v"
    top_path.write_text("\n".join(top_lines) + "\n", encoding="utf-8")

    # ==========================================
    # Generate basys3.xdc
    # ==========================================

    xdc_lines = [
        "# Auto-generated Basys 3 pin constraints",
        "",
        "# Input switches"
    ]

    # Assign each switch to its physical FPGA pin
    for i in range(n):
        pin = SWITCH_PINS[i]

        xdc_lines.append(
            f"set_property -dict {{ PACKAGE_PIN {pin} "
            f"IOSTANDARD LVCMOS33 }} [get_ports {{sw[{i}]}}]"
        )

    # Output LED
    xdc_lines.extend([
        "",
        "# LED0",
        "set_property -dict { PACKAGE_PIN U16 IOSTANDARD LVCMOS33 } [get_ports led]",
        "",
        "# Seven-segment display"
    ])

    # Segments A to G
    for i, pin in enumerate(SEGMENT_PINS):
        xdc_lines.append(
            f"set_property -dict {{ PACKAGE_PIN {pin} "
            f"IOSTANDARD LVCMOS33 }} [get_ports {{seg[{i}]}}]"
        )

    # Decimal point
    xdc_lines.extend([
        "",
        "# Decimal point",
        "set_property -dict { PACKAGE_PIN V7 IOSTANDARD LVCMOS33 } [get_ports dp]",
        "",
        "# Digit enables"
    ])

    # AN0 through AN3
    for i, pin in enumerate(DIGIT_PINS):
        xdc_lines.append(
            f"set_property -dict {{ PACKAGE_PIN {pin} "
            f"IOSTANDARD LVCMOS33 }} [get_ports {{an[{i}]}}]"
        )

    xdc_path = folder / "basys3.xdc"
    xdc_path.write_text("\n".join(xdc_lines) + "\n", encoding="utf-8")

    return top_path, xdc_path
