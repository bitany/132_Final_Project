# run(inc).py - Executes the program

import storage
from compiler import Instruction
from addressing import Access, AddressingMode
from convert import Precision, Length

class Except:
    def __init__(self, msg, occur=True):
        self.msg = msg
        self.occur = occur
        self.returnValue = None

    def dispMSG(self):
        print(f"[Exception]: {self.msg}")

    def isOccur(self):
        return self.occur

    def setReturn(self, val):
        self.returnValue = val

    def getReturn(self):
        return self.returnValue


class Program:
    def __init__(self, program):
        # Encode the program to memory
        if "PC" not in storage.register.data:
            storage.register.store("PC", 0)
        parsed = [[part.strip(',') for part in instr.split()] for instr in program]
        self.program = Instruction.preEncode(parsed)
        Instruction.encodeProgram(self.program)

    @staticmethod
    def exception(name, value):
        if name == "DivByZero" and value == 0:
            return Except("Division by zero error")
        return Except("No Exception", occur=False)

    def getOp(self, code):
        mode = code[:Length.opMode]
        addr = int(code[Length.opMode:], 2)

        if mode == "000":  # Register
            val = AddressingMode.register(f"R{addr}")
        elif mode == "001":  # Register indirect
            val = AddressingMode.register_indirect(f"R{addr}")
        elif mode == "010":  # Direct
            val = AddressingMode.direct(addr)
        elif mode == "011":  # Indirect
            val = AddressingMode.indirect(addr)
        elif mode == "100":  # Indexed
            val = AddressingMode.indexed(addr)
        elif mode == "101":  # Stack push
            val = AddressingMode.stack("push")
        elif mode == "110":  # Stack pop
            val = AddressingMode.stack("pop")
        else:
            val = 0
        return val

    def write(self, dest_code, src_val, movcode):
        mode = dest_code[:Length.opMode]
        addr = int(dest_code[Length.opMode:], 2)

        if mode == "000":  # Register
            storage.register.store(f"R{addr}", src_val)
        elif mode == "001":  # Register indirect
            reg_addr = storage.register.load(f"R{addr}")
            storage.memory.store(reg_addr, src_val)
        elif mode == "010":  # Direct
            storage.memory.store(addr, src_val)
        elif mode == "011":  # Indirect
            indirect_addr = storage.memory.load(addr)
            storage.memory.store(indirect_addr, src_val)
        elif mode == "101":  # Stack push
            push_addr = AddressingMode.stack("push")
            storage.memory.store(push_addr, src_val)
        # Pop is not written to, it fetches only

    def execute(self, result, opcode):
        if opcode == "ADD":
            return result[0] + result[1]
        elif opcode == "SUB":
            return result[0] - result[1]
        elif opcode == "MUL":
            return result[0] * result[1]
        elif opcode == "DIV":
            ex = self.exception("DivByZero", result[1])
            if ex.isOccur():
                ex.dispMSG()
                return 0
            return result[0] / result[1]
        elif opcode == "MOD":
            return result[0] % result[1]
        return 0

    def run(self):
        pc = int(storage.register.load("PC"))

        while True:
            code = storage.memory.load(pc, isCode=True)
            pc += 1
            storage.register.store("PC", pc)

            # Decode opcode and operands
            opcode_bin = code[:5]
            op1_code = code[5:16]  # 3 + 8 bits
            op2_code = code[16:27]  # 3 + 8 bits
            # extra = code[27:] (unused)

            # Decode operation name from opcode_bin
            op_group = int(opcode_bin[:2], 2)
            cat_index = int(opcode_bin[2:], 2)
            opcode = operations[op_group][cat_index]

            # Get operands
            if opcode in ["ADD", "SUB", "MUL", "DIV", "MOD"]:
                op1_val = self.getOp(op1_code)
                op2_val = self.getOp(op2_code)
                result = self.execute((op1_val, op2_val), opcode)
                self.write(op1_code, result, opcode)

            elif opcode == "MOV":
                op1_val = self.getOp(op2_code)
                self.write(op1_code, op1_val, opcode)

            elif opcode == "PUSH":
                val = self.getOp(op1_code)
                push_addr = AddressingMode.stack("push")
                storage.memory.store(push_addr, val)

            elif opcode == "POP":
                val = AddressingMode.stack("pop")
                self.write(op1_code, val, opcode)

            elif opcode == "JMP":
                target = self.getOp(op1_code)
                storage.register.store("PC", int(target))

            elif opcode in ["JEQ", "JNE", "JLT", "JLE", "JGT", "JGE"]:
                op1_val = self.getOp(op1_code)
                op2_val = self.getOp(op2_code)
                target = int(storage.register.load("PC"))

                cond = False
                if opcode == "JEQ": cond = op1_val == op2_val
                if opcode == "JNE": cond = op1_val != op2_val
                if opcode == "JLT": cond = op1_val < op2_val
                if opcode == "JLE": cond = op1_val <= op2_val
                if opcode == "JGT": cond = op1_val > op2_val
                if opcode == "JGE": cond = op1_val >= op2_val

                if cond:
                    target = self.getOp(code[5:16])  # jump address in op1
                    storage.register.store("PC", int(target))

            elif opcode == "EOP":
                print("[Program Terminated]")
                break

if __name__ == "__main__":
    try:
        # Access file with group extension (replace 'isk' with your group shortcut)
        filename = "isk.inc"  # Change this to your group's file extension
        
        print(f"[INFO] Loading program from {filename}...")
        
        with open(filename, "r") as f:
            lines = f.readlines()
            # Convert text from file as list of instructions
            instructions = []
            for line in lines:
                # Remove comments and whitespace
                clean_line = line.split(";")[0].strip()
                if clean_line:  # Only add non-empty lines
                    instructions.append(clean_line)
        
        print(f"[INFO] Loaded {len(instructions)} instructions")
        
        # Pass instructions to Program class
        program = Program(instructions)
        
        # Program class calls run
        program.run()

        # Display final state
        print("\n" + "="*50)
        print("FINAL SYSTEM STATE")
        print("="*50)
        
        print("\nFinal Register State:")
        storage.register.dispStorage()

        print("\nMemory Contents (Instructions + Data):")
        storage.memory.dispStorage()

    except FileNotFoundError:
        print(f"[ERROR] Instruction file not found. Please ensure the file exists with your group's extension.")
        print("Expected filename format: [group_shortcut].inc")
    except Exception as e:
        file_exception = Program.exception("FileError", str(e))
        file_exception.dispMSG()
