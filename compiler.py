import storage
from addressing import Access, AddressingMode
from convert import Length, Precision, Value

# Operation grouping by Execute and Write bits
operations = [
    ["PRNT", "EOP"],  # 00 - Print operations
    ["MOV", "PUSH", "POP", "CALL", "RET", "SCAN", "DEF"],  # 01 - Data/Control operations
    ["JEQ", "JNE", "JLT", "JLE", "JGT", "JGE", "JMP"],  # 10 - Conditional jumps
    ["MOD", "ADD", "SUB", "MUL", "DIV"]  # 11 - Arithmetic
]

# Corresponding binary codes: [Execute+Write bits, Category bits]
operationCodes = [
    ["00", "01", "10", "11"],
    ["000", "001", "010", "011", "100", "101", "110", "111"]
]

class Instruction:

    @staticmethod
    def preEncode(instrxns):
        """Handles special pre-encoding cases like DEF, JEQ, etc."""
        result = []
        for instr in instrxns:
            if instr[0] in ["JEQ", "JNE", "JLT", "JLE", "JGT", "JGE"]:
                # Conditional jumps use SUB then change to JMP if condition met
                result.append(["SUB", instr[1], instr[2]])  # Compare
                result.append([instr[0], instr[3]])         # Conditional jump
            else:
                result.append(instr)
        return result

    @staticmethod
    def encodeOp(operand):
        """Encodes operand addressing mode and address into binary."""
        # Determine addressing mode
        if operand.startswith("R"):
            mode = "000"
            addr = operand
        elif operand.startswith("@R"):
            mode = "001"
            addr = operand[1:]  # skip '@'
        elif operand.startswith("*"):
            mode = "011"
            addr = operand[1:]
        elif operand.startswith("#"):
            mode = "100"  # Indexed, assume I1 or I2 is used in run-time
            addr = operand[1:]
        elif operand == "push":
            mode = "101"
            addr = "0"
        elif operand == "pop":
            mode = "110"
            addr = "0"
        else:
            mode = "010"  # Direct
            addr = operand

        # Get binary address from variable or assume it's already numeric
        try:
            address = storage.variable.load(addr)
        except:
            address = int(addr)

        # Pad binary address to 8 bits
        bin_addr = bin(address)[2:].zfill(Length.opAddr)
        return mode + bin_addr  # Combined 11-bit operand (mode + address)

    @staticmethod
    def encode(inst):
        """Encodes a single instruction into a 32-bit binary string."""
        op = inst[0]

        # Find operation group and category index
        EWC = ""
        Cat = ""
        for i, group in enumerate(operations):
            if op in group:
                EWC = operationCodes[0][i]
                Cat = operationCodes[1][group.index(op)]
                break

        # First 5 bits: 2 bits E/W + 3 bits category
        opCode = EWC + Cat

        # Encode operands (max 2)
        if len(inst) == 3:
            op1 = Instruction.encodeOp(inst[1])
            op2 = Instruction.encodeOp(inst[2])
        elif len(inst) == 2:
            op1 = Instruction.encodeOp(inst[1])
            op2 = "00000000000"  # empty second operand
        else:
            op1 = "00000000000"
            op2 = "00000000000"

        # Pad extra bits (5 bits)
        extra = "00000"

        # Final 32-bit instruction
        full_instr = opCode + op1 + op2 + extra
        return full_instr

    @staticmethod
    def encodeProgram(program):
        """Encodes each instruction in the program and stores them in memory starting at PC."""
        pc = int(storage.register.load("PC"))
        for instr in program:
            encoded = Instruction.encode(instr)
            storage.memory.store(pc, encoded)
            pc += 1
        storage.register.store("PC", pc)  # update PC after loading program
