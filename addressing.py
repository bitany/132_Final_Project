import storage
from convert import Precision

class Access:
    @staticmethod
    def data(addr, flow=["var", "reg", "mem"]):
        # Try to load data from storage based on the flow priority.
        for scope in flow:
            try:
                if scope == "var":
                    return storage.variable.load(addr)
                elif scope == "reg":
                    return storage.register.load(addr)
                elif scope == "mem":
                    return storage.memory.load(addr)
            except:
                continue
        raise Exception(f"Address {addr} not found in storage.")

    @staticmethod
    def store(scope, addr, value):
        # Store value in the specified storage scope (reg or mem).
        if scope == "reg":
            storage.register.store(addr, value)
        elif scope == "mem":
            storage.memory.store(addr, value)
        elif scope == "var":
            storage.variable.store(addr, value)
        else:
            raise Exception(f"Invalid storage scope: {scope}")

class AddressingMode:
    @staticmethod
    def register(reg_addr):
        # Register addressing mode (returns value stored in register)
        return Access.data(reg_addr, ["reg"])

    @staticmethod
    def register_indirect(reg_addr):
        # Register indirect addressing (get address from register, then load from memory)
        mem_addr = Access.data(reg_addr, ["reg"])
        return Access.data(int(mem_addr), ["mem"])

    @staticmethod
    def direct(var_addr):
        # Direct memory access by address
        return Access.data(int(var_addr), ["mem"])

    @staticmethod
    def indirect(var_addr):
        # Indirect memory access: fetch address from memory, then load value.
        addr = Access.data(int(var_addr), ["mem"])
        return Access.data(int(addr), ["mem"])

    @staticmethod
    def indexed(displace):
        # Indexed mode: use I1 or I2 to compute address offset.
        base = int(Access.data("I1", ["reg"]))
        return Access.data(base + int(displace), ["mem"])

    @staticmethod
    def autoinc(reg_addr):
        # Auto-increment: get value from address, then increment register
        mem_addr = Access.data(reg_addr, ["reg"])
        value = Access.data(int(mem_addr), ["mem"])
        Access.store("reg", reg_addr, int(mem_addr) + 1)
        return value

    @staticmethod
    def autodec(reg_addr):
        # Auto-decrement: decrement register, then get value from new address
        mem_addr = int(Access.data(reg_addr, ["reg"])) - 1
        Access.store("reg", reg_addr, mem_addr)
        return Access.data(mem_addr, ["mem"])

    @staticmethod
    def stack(stack_option):
        # Stack operations using SPR (Stack Pointer Register) and TSP (Top Stack Pointer)."""
        spr = int(Access.data("SPR", ["reg"]))
        tsp = int(Access.data("TSP", ["reg"]))

        if stack_option == "push":
            # Store value at TSP, then increment TSP
            return_address = tsp
            Access.store("reg", "TSP", tsp + 1)
            return return_address  # Caller should write to this address
        elif stack_option == "pop":
            # Decrement TSP, then return the popped value
            Access.store("reg", "TSP", tsp - 1)
            return Access.data(tsp - 1, ["mem"])
        elif stack_option == "top":
            # Return value at current top
            return Access.data(tsp - 1, ["mem"])
        else:
            raise Exception("Invalid stack option. Use 'push', 'pop', or 'top'.")
