import storage
from convert import Precision

class Access:
    @staticmethod
    def data(addr, flow=["var", "register", "memory"]):
        # Try to load data from storage based on the flow priority.
        for scope in flow:
            try:
                if scope == "var":
                    return storage.variable.load(addr)
                elif scope == "register":
                    return storage.register.load(addr)
                elif scope == "memory":
                    return storage.memory.load(addr)
            except:
                continue
        raise Exception(f"Address {addr} not found in storage.")

    @staticmethod
    def store(scope, addr, value):
        # Store value in the specified storage scope (register or memory).
        if scope == "register":
            storage.register.store(addr, value)
        elif scope == "memory":
            storage.memory.store(addr, value)
        elif scope == "var":
            storage.variable.store(addr, value)
        else:
            raise Exception(f"Invalid storage scope: {scope}")

class AddressingMode:
    @staticmethod
    def register(reg_addr):
        # Register addressing mode (returns value stored in register).
        return storage.register.load(reg_addr)

    @staticmethod
    def register_indirect(reg_addr):
        # Register indirect addressing (get address from register, then load from memory).
        addr = storage.register.load(reg_addr)
        return storage.memory.load(int(addr))

    @staticmethod
    def direct(var_addr):
        # Direct memory access by address.
        return storage.memory.load(int(var_addr))

    @staticmethod
    def indirect(var_addr):
        # Indirect memory access: fetch address from memory, then load value.
        addr = storage.memory.load(int(var_addr))
        return storage.memory.load(int(addr))

    @staticmethod
    def indexed(displace):
        # Indexed mode: use I1 or I2 to compute address offset.
        base = int(storage.register.load("I1"))
        return storage.memory.load(base + int(displace))

    @staticmethod
    def autoinc(reg_addr):
        # Auto-increment: get value from address, then increment register.
        addr = storage.register.load(reg_addr)
        value = storage.memory.load(int(addr))
        storage.register.store(reg_addr, int(addr) + 1)
        return value

    @staticmethod
    def autodec(reg_addr):
        # Auto-decrement: decrement register, then get value from new address.
        addr = int(storage.register.load(reg_addr)) - 1
        storage.register.store(reg_addr, addr)
        return storage.memory.load(addr)

    @staticmethod
    def stack(stack_option):
        # Stack operations using SPR (Stack Pointer Register) and TSP (Top Stack Pointer).
        spr = int(storage.register.load("SPR"))
        tsp = int(storage.register.load("TSP"))

        if stack_option == "push":
            # Store value at TSP, then i
