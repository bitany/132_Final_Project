import storage
from addressing import Access, AddressingMode
from convert import Length, Precision, Value

# List of operations grouped by categories
operations = [
    ["PRNT", "EOP"],                                        # group 0 - output and program termination
    ["MOV", "PUSH", "POP", "CALL", "RET", "SCAN", "DEF"],   # group 1 - data movement and stack operations
    ["JEQ", "JNE", "JLT", "JLE", "JGT", "JGE", "JMP"],      # group 2 - jump/conditonal
    ["MOD", "ADD", "SUB", "MUL", "DIV"],                    # group 3 - arithmetic
]


operationCodes = [
    ["00", "01", "10", "11"],                                 # Execute and Write bits
    ["000", "001", "010", "011", "100", "101", "110", "111"]  # Category codes
]

class Instruction:
    @staticmethod
    def preEncode(instrxns):
        result = []
        for inst in instrxns:
            if not isinstance(inst, list):
                inst = inst.split()
            
            if len(inst) == 0:
                continue
                
            if inst[0] == "DEV":                              # DEV treated same as MOV 
                if len(inst) >= 3:
                    result.append(["MOV", inst[1], inst[2]])
                else:
                    result.append(["MOV", inst[1], "0"])
            elif inst[0] == "DEF":                          # Handle DEF
                result.append(inst)                         # Keep DEF as is
            elif inst[0].startswith("J"):                   # Handle conditional jumps
                result.append(inst)
            elif len(inst) > 1 and isinstance(inst[1], list):  # Handle indexing
                result.append(inst)
            else:
                result.append(inst)
        return result

    @staticmethod
    def encode(inst):                                       # Encode a single instruction into 32-bit binary string
        if inst[0] == "FUNC":                               # FUNC treated same as EOP (end of program)
            return "0" * 32

        # Step 1: Find opcode (5 bits)
        opcode = "00000"                                    # default opcode

        if inst[0] == "DEF":                                # def treated as Mov to preserve DEF in metadata
            # Find MOV opcode
            for i, group in enumerate(operations):   
                if "MOV" in group:
                    opcode = operationCodes[0][i] + operationCodes[1][group.index("MOV")]
                    break
        else:
            # Normal opcode lookup for other instructions
            for i, group in enumerate(operations):
                if inst[0] in group:
                    # group code = 2 bits, instruction code = 3 bits
                    opcode = operationCodes[0][i] + operationCodes[1][group.index(inst[0])]
                    break

        # Initialize operand modes and addresses 
        op1_mode, op1_addr = "000", "00000000"
        op2_mode, op2_addr = "000", "00000000"

        # Encode operands if present
        if len(inst) > 1:
            op1_mode, op1_addr = Instruction.encodeOp(inst[1])
        if len(inst) > 2:
            op2_mode, op2_addr = Instruction.encodeOp(inst[2])

        # Compose 32-bit instruction binary string
        inst_code = opcode + op1_mode + op1_addr + op2_mode + op2_addr + "00000"  # total should be 32 bits

        # Ensure inst_code is exactly 32 bits
        inst_code = Length.addZeros(inst_code, 32)
        return inst_code

    @staticmethod
    def encodeOp(operand):
        """
        Addressing Modes:
        000 - Register Direct     (e.g., R1)
        001 - Register Indirect   (e.g., *R1)
        010 - Direct             (e.g., var)
        011 - Indirect           (e.g., *var)
        100 - Immediate          (e.g., #5)
        101 - Stack Push         (PUSH)
        110 - Stack Pop          (POP)
        """
        if not operand:
            return ("000", "00000000")

        if isinstance(operand, str):
            # Immediate value (e.g. "#5")
            if operand.startswith("#"):
                try:
                    value = int(operand[1:])
                    value_bin = Length.addZeros(bin(value)[2:], 8)
                    return ("111", value_bin)
                except ValueError:
                    return ("100", "00000000")

            # Register direct mode (e.g. "R1")
            if operand.startswith("R") and operand[1:].isdigit():
                reg_num_bin = Length.addZeros(bin(int(operand[1:]))[2:], 8)
                return ("000", reg_num_bin)

            # Register indirect mode (e.g. "*R1")
            elif operand.startswith("*R") and operand[2:].isdigit():
                reg_num_bin = Length.addZeros(bin(int(operand[2:]))[2:], 8)
                return ("001", reg_num_bin)

            # Stack operations
            elif operand == "PUSH":
                return ("101", "00000000")
            elif operand == "POP":
                return ("110", "00000000")

            # Convert string to number for immediate value
            elif operand.isdigit():
                value = int(operand)
                value_bin = Length.addZeros(bin(value)[2:], 8)
                return ("100", value_bin)

            # Indirect mode variable (e.g. "*var")
            elif operand.startswith("*") and not operand.startswith("*R"):
                try:
                    addr = storage.variable.load(operand[1:])
                    addr_bin = Length.addZeros(bin(int(addr))[2:], 8) if addr is not None else "00000000"
                    return ("011", addr_bin)
                except KeyError:
                    return ("011", "00000000")  # Default to zero address if variable not found

            # Direct addressing mode (variable name)
            else:
                try:
                    addr = storage.variable.load(operand)
                    addr_bin = Length.addZeros(bin(int(addr))[2:], 8) if addr is not None else "00000000"
                    return ("010", addr_bin)
                except KeyError:
                    # For undefined variables (like in DEF instructions), use address 0
                    return ("010", "00000000")

        # Indexed addressing mode (base and offset)
        elif isinstance(operand, list) and len(operand) == 2:
            try:
                base_addr = storage.variable.load(operand[0])
                base_int = int(base_addr) if base_addr is not None else 0
                offset = int(operand[1])
                combined = base_int + offset
                combined_bin = Length.addZeros(bin(combined)[2:], 8)
                return ("100", combined_bin)
            except KeyError:
                return ("100", "00000000")  # zero as default if var is not found

        return ("000", "00000000")          # Default mode

    @staticmethod
    def encodeProgram(program):
        pc = int(storage.register.load("PC"))
        encoded_program = Instruction.preEncode(program)

        print("[INFO] Encoding program instructions...")
        for inst in encoded_program:
            if inst[0] in ["DEF", "DEB"]:
                print(f"[DEBUG] Skipping {inst[0]} instruction")
                continue
            
            bin_code = Instruction.encode(inst)
            print(f"[DEBUG] Encoded {inst[0]}: {bin_code}")
            storage.memory.store(pc, bin_code)
            pc = int(pc + 1)

        storage.register.store("PC", int(pc))
        print("[INFO] Program encoding complete")
