# run(inc).py - Executes the program

import storage
from compiler import Instruction, operations    #operation was imported from compiler.py
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
        # Initialize PC to 8 (start of instruction memory)
        storage.register.storeRegisterValue("PC", 8)
        storage.register.storeRegisterValue("IR", 8)
        storage.register.storeRegisterValue("BR", 8)
        
        # Parse and encode instructions
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
            return int(storage.register.loadRegisterValue(f"R{addr}"))
        elif mode == "001":  # Register indirect
            reg_val = int(storage.register.loadRegisterValue(f"R{addr}"))
            return int(storage.memory.load(reg_val))
        elif mode == "010":  # Direct
            return int(storage.memory.load(addr))
        elif mode == "011":  # Indirect
            try:
                # First load the address from memory
                addr_value = int(storage.memory.load(addr))
                print(f"[DEBUG] Indirect addressing: First load from memory[{addr}] = {addr_value}")
                # Then load the value from that address
                final_value = int(storage.memory.load(addr_value))
                print(f"[DEBUG] Indirect addressing: Then load from memory[{addr_value}] = {final_value}")
                return final_value
            except Exception as e:
                print(f"[ERROR] Indirect addressing failed: {str(e)}")
                return 0
        elif mode == "100":  # Immediate value
            return addr  # Return the value directly
        elif mode == "101":  # Stack push
            sp = storage.register.getStackPointer()
            storage.register.updateStackPointer(sp + 1)
            return sp
        elif mode == "110":  # Stack pop
            sp = storage.register.getStackPointer()
            if sp > 0:
                val = int(storage.memory.load(sp - 1))
                storage.register.updateStackPointer(sp - 1)
                return val
        return 0

    def write(self, dest_code, src_val, movcode):
        mode = dest_code[:Length.opMode]
        addr = int(dest_code[Length.opMode:], 2)

        try:
            if mode == "000":  # Register
                storage.register.storeRegisterValue(f"R{addr}", int(src_val))
                print(f"[DEBUG] Wrote {src_val} to R{addr}")
            elif mode == "001":  # Register indirect
                reg_addr = int(storage.register.loadRegisterValue(f"R{addr}"))
                storage.memory.store(reg_addr, int(src_val))
                print(f"[DEBUG] Wrote {src_val} to memory[{reg_addr}]")
            elif mode == "010":  # Direct
                storage.memory.store(addr, int(src_val))
                print(f"[DEBUG] Wrote {src_val} to memory[{addr}]")
            elif mode == "011":  # Indirect
                indirect_addr = int(storage.memory.load(addr))
                storage.memory.store(indirect_addr, int(src_val))
                print(f"[DEBUG] Wrote {src_val} to memory[{indirect_addr}]")
            elif mode == "101":  # Stack push
                sp = storage.register.getStackPointer()
                storage.memory.store(sp, int(src_val))
                storage.register.updateStackPointer(sp + 1)
                print(f"[DEBUG] Pushed {src_val} to stack at {sp}")
        except Exception as e:
            print(f"[ERROR] Write failed: {str(e)}")

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
        pc = 8  # Start at instruction memory
        print("\n[INFO] Starting program execution...")

        while pc < 72:  # Only execute within instruction memory range
            try:
                code = storage.memory.loadInstruction(pc)
                if not code or all(bit == '0' for bit in code):
                    break

                print(f"\n[DEBUG] Executing instruction at PC={pc}")
                print(f"[DEBUG] Instruction code: {code}")
                
                # Decode opcode and operands
                opcode_bin = code[:5]
                op1_code = code[5:16]
                op2_code = code[16:27]
                
                # Get operation name
                op_group = int(opcode_bin[:2], 2)
                cat_index = int(opcode_bin[2:], 2)
                
                try:
                    opcode = operations[op_group][cat_index]
                except (IndexError, KeyError):
                    pc += 1
                    continue

                print(f"[DEBUG] Operation: {opcode}")

                # Execute instruction
                if opcode == "MOV":
                    val = self.getOp(op2_code)  # Source
                    print(f"[DEBUG] Moving value {val}")
                    self.write(op1_code, val, opcode)  # Destination
                elif opcode in ["ADD", "SUB", "MUL", "DIV"]:
                    op1_val = self.getOp(op1_code)
                    op2_val = self.getOp(op2_code)
                    print(f"[DEBUG] {opcode}: {op1_val} {opcode} {op2_val}")
                    
                    if opcode == "ADD": result = op1_val + op2_val
                    elif opcode == "SUB": result = op1_val - op2_val
                    elif opcode == "MUL": result = op1_val * op2_val
                    elif opcode == "DIV" and op2_val != 0: result = op1_val / op2_val
                    else: result = 0
                    
                    print(f"[DEBUG] Result: {result}")
                    self.write(op1_code, result, opcode)
                elif opcode == "PUSH":
                    val = self.getOp(op1_code)
                    print(f"[DEBUG] Pushing value {val}")
                    self.write("101" + "0"*8, val, opcode)
                elif opcode == "POP":
                    sp = storage.register.getStackPointer()
                    if sp > 0:
                        val = storage.memory.load(sp - 1)
                        print(f"[DEBUG] Popping value {val}")
                        self.write(op1_code, val, opcode)
                        storage.register.updateStackPointer(sp - 1)
                elif opcode == "JMP":
                    target = self.getOp(op1_code)
                    print(f"[DEBUG] Jump target: {target}")
                    if 8 <= target < 72:  # Stay within instruction memory
                        pc = target
                        continue
                elif opcode == "EOP":
                    break

                pc += 1
                storage.register.storeRegisterValue("PC", pc)

            except Exception as e:
                print(f"[ERROR] at PC={pc}: {str(e)}")
                pc += 1

        print("\n[Program Terminated]")

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
                if clean_line and not clean_line.isspace():  # Only add non-empty lines
                    instructions.append(clean_line)
        
        print(f"[INFO] Loaded {len(instructions)} instructions")
        print("\nInstructions to execute:")
        for i, inst in enumerate(instructions):
            print(f"{i}: {inst}")
        
        # Initialize storage
        print("\n[INFO] Initializing storage...")
        storage.register.store("SPR", 120)  # Set stack pointer
        storage.register.store("TSP", 120)  # Set top of stack pointer
        
        # Pass instructions to Program class
        print("\n[INFO] Creating program...")
        program = Program(instructions)
        
        # Program class calls run
        print("\n[INFO] Running program...")
        program.run()

        # Display final state
        print("\n" + "="*50)
        print("FINAL SYSTEM STATE")
        print("="*50)
        
        # Use new display methods
        storage.register.dispRegisters()
        storage.memory.dispInstructionMemory()
        storage.memory.dispDataMemory()

    except FileNotFoundError:
        print(f"[ERROR] Instruction file not found. Please ensure the file exists with your group's extension.")
        print("Expected filename format: [group_shortcut].inc")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
