# Global Variables
opcode = {}
registers = {}
labels = {}
loops = {}
pc = 0


def init():
    global opcode, registers

    opcode = {
        "ADD": "00000",
        "SUB": "00001",
        "MUL": "00010",
        "DIV": "00011",
        "MOD": "00100",
        "CMP": "00101",
        "AND": "00110",
        "OR": "00111",
        "NOT": "01000",
        "MOV": "01001",
        "LSL": "01010",
        "LSR": "01011",
        "ASR": "01100",
        "NOP": "01101",
        "LD": "01110",
        "ST": "01111",
        "BEQ": "10000",
        "BGT": "10001",
        "B": "10010",
        "CALL": "10011",
        "RET": "10100",
        "HLT": "11111",
        "END": "11111",
    }

    registers = {
        "R0": "0000",
        "R1": "0001",
        "R2": "0010",
        "R3": "0011",
        "R4": "0100",
        "R5": "0101",
        "R6": "0110",
        "R7": "0111",
        "R8": "1000",
        "R9": "1001",
        "R10": "1010",
        "R11": "1011",
        "R12": "1100",
        "R13": "1101",
        "R14": "1110",  # SP
        "R15": "1111",  # ra
    }


def remove_comments(line):
    line = line.split("//")[0].strip()
    line.split(";")[0].strip()

    return line.replace(",", " ")


def parse_label_and_rest(line):
    line = remove_comments(line)
    if ":" in line:
        label_part, rest = line.split(":", 1)
        return label_part.strip(), rest.strip()

    return None, line.strip()


def handle_twos_complement(num, bits):
    if num < 0:
        num = (1 << int(bits)) + num
    return num


"""Relative Address"""


def relative_address(address, bits):
    global labels, pc
    offset = address - pc
    return format(handle_twos_complement(offset, bits), f"0{bits}b")


"""Parsing intermediate"""


def parse_immediate(imm_str, bits):
    imm_str = str(imm_str)
    if imm_str.startswith("0x") or imm_str.startswith("0X"):
        return handle_twos_complement(int(imm_str, 16), bits)
    elif imm_str.startswith("0b") or imm_str.startswith("0B"):
        return handle_twos_complement(int(imm_str, 2), bits)
    elif imm_str.startswith("0o") or imm_str.startswith("0O"):
        return handle_twos_complement(int(imm_str, 8), bits)
    else:
        return handle_twos_complement(int(imm_str, 10), bits)  # default is decimal


# Look for Label and Loops
def look_for_loops_or_labels(lines):
    global labels, loops
    instruction_address = 0
    for line in lines:
        label, inst = parse_label_and_rest(line)
        if label:
            labels[label] = instruction_address
        if inst:
            instruction_address += 1


"""1. One - Address Instructions"""


def one_address_instruction(inst, label):
    global labels, loops, registers, opcode
    bin_instr = opcode[inst]
    if label not in labels:
        return f"ERROR: Label {label} not defined"
    address = labels[label]
    bin_instr += relative_address(address, 27)

    return bin_instr


"""2. Three - Address Instruction"""


def three_address_instruction(inst, RI_Type, dst, src1, src2, modifier):
    global labels, loops, registers, opcode
    bin_instr = opcode[inst]
    bin_instr += str(RI_Type)
    bin_instr += registers[dst]
    bin_instr += registers[src1]
    if RI_Type == 1:
        bin_instr += modifier
        bin_instr += format(parse_immediate(src2, 16), "016b")
    else:
        bin_instr += registers[src2]
    while len(bin_instr) != 32:
        bin_instr += "0"

    return bin_instr


"""3. Two - Address Instruction"""


def two_address_instruction(inst, RI_Type, rs1, rs2):
    global labels, loops, registers, opcode
    bin_instr = opcode[inst]
    bin_instr += str(RI_Type)

    if inst == "CMP":
        bin_instr += "0000"

    bin_instr += registers[rs1]

    if inst != "CMP":
        bin_instr += "0000"

    if RI_Type == 1:
        bin_instr += format(parse_immediate(rs2, 18), "018b")
    else:
        bin_instr += registers[rs2]

    while len(bin_instr) != 32:
        bin_instr += "0"

    return bin_instr


"""4. Load and Store Instruction"""


def load_store_instruction(inst, address, rd, rs1, imm):
    global labels, loops, registers, opcode
    bin_instr = opcode[inst]
    bin_instr += format(parse_immediate(address, 1), "01b")
    bin_instr += registers[rd]
    bin_instr += registers[rs1]
    if address == 1:
        bin_instr += format(parse_immediate(imm, 18), "018b")
    else:
        bin_instr += registers[imm]

    while len(bin_instr) != 32:
        bin_instr += "0"

    return bin_instr


def zero_address_instruction(inst):
    return opcode[inst] + "0" * 27


"""Assemble Line"""


def assemble_line(line):
    global opcode, registers, labels, loops, pc
    label, inst = parse_label_and_rest(line)
    if not inst:
        return ""

    parts = inst.replace(",", "").split()
    if not parts:
        return ""

    pc = pc + 1

    inst = parts[0].upper()
    operands = parts[1:]
    modifier = "00"

    if len(inst) > 3:
        modifier = inst[-1]
        inst = inst[:-1]
    if modifier not in ["00", "U", "H"]:
        return f"ERROR: Invalid modifier {modifier}"
    else:
        if modifier == "U":
            modifier = "01"
        elif modifier == "H":
            modifier = "10"

    if inst not in opcode:
        return f"ERROR: Unknown opcode {inst}"

    if inst in ["CALL", "B", "BEQ", "BGT"]:
        return one_address_instruction(inst, operands[0])

    if inst in ["ADD", "SUB", "MUL", "DIV", "MOD", "AND", "OR", "LSL", "LSR", "ASR"]:
        dst = operands[0]
        src1 = operands[1]
        src2 = operands[2]
        RI_Type = 1
        if src2.upper() in registers:
            RI_Type = 0

        return three_address_instruction(
            inst, RI_Type, dst.upper(), src1.upper(), src2.upper(), modifier
        )

    if inst in ["CMP", "NOT", "MOV"]:
        rs1 = operands[0]
        rs2 = operands[1]
        RI_Type = 1
        if rs2.upper() in registers:
            RI_Type = 0
        return two_address_instruction(inst, RI_Type, rs1.upper(), rs2.upper())

    if inst in ["LD", "ST"]:
        rd = operands[0]
        rs1 = operands[1]
        imm = operands[2]
        address = 1
        if imm.startswith("[") and imm.endswith("]"):
            imm = imm[1:-1]
            address = 0
        return load_store_instruction(
            inst, address, rd.upper(), rs1.upper(), imm.upper()
        )

    if inst in ["NOP", "RET", "HLT", "END"]:
        return zero_address_instruction(inst)


def main(ip_file, op_file):
    init()

    with open(ip_file, "r") as infile:
        lines = infile.readlines()

    look_for_loops_or_labels(lines)
    print(labels)

    machine_code = []
    for line in lines:
        line = remove_comments(line)
        print(line)
        machine_code_line = assemble_line(line)
        print(machine_code_line)

        if machine_code_line and not machine_code_line.startswith("ERROR"):
            machine_code.append(machine_code_line)

    with open(op_file, "w") as outfile:
        for machine_code_line in machine_code:
            outfile.write(machine_code_line + "\n")

    print("Done")
