"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # RAM
        self.ram = [0] * 256

        # General-purpose registers
        self.reg = [0] * 8  # R0 - R7
        self.pc = 0
        self.flag = 0

        # keep track of whether program is runnning 
        self.running = True

        #
        self.HLT = 0b00000001
        self.LDI = 0b10000010
        self.PRN = 0b01000111
        self.PUSH = 0b01000101
        self.POP = 0b01000110
        self.RET = 0b00010001
        self.CALL = 0b01010000
        self.CMP = 0b10100111
        self.JMP = 0b01010100
        self.JEQ = 0b01010101
        self.JNE = 0b01010110
        self.branchtable = {
            self.HLT: self.handle_halt,
            self.LDI: self.handle_ldi,
            self.PRN: self.handle_print,
            self.PUSH: self.handle_push,
            self.POP: self.handle_pop,
            self.CALL: self.handle_call,
            self.RET: self.handle_return,
            self.JMP: self.handle_jump,
            self.JEQ: self.handle_jeq,
            self.JNE: self.handle_jne,
        }
        self.SP = 7
        self.reg[self.SP] = 0xF4

    def load(self):
        """Load a program into memory."""

        address = 0
        program_filename = sys.argv[1]

        with open(program_filename) as f:
            for line in f:
                line = line.split("#")
                line = line[0].strip()

                if line == "":
                    continue

                self.ram[address] = int(line, 2)
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == 0b10100000:  # ADD
            self.reg[reg_a] += self.reg[reg_b]
        elif op == 0b10100010:  # MUL
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == 0b10100001:  # SUB
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == 0b10100011:  # DIV
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == 0b10100111:  # CMP
            if self.reg[reg_a] < self.reg[reg_b]:
                self.flag = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.flag = 0b00000010
            elif self.reg[reg_a] == self.reg[reg_b]:
                self.flag = 0b00000001
            else:
                self.flag = 0b00000000
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self, LABEL=str()):
        """
                        Handy function to print out the CPU state. You might want to call this
                        from run() if you need help debugging.
                        """

        print(
            f"{LABEL} TRACE --> PC: %02i | RAM: %03i %03i %03i | Register: "
            % (
                self.pc,
                # self.fl,
                # self.ie,
                self.ram_read(self.pc),
                self.ram_read(self.pc + 1),
                self.ram_read(self.pc + 2),
            ),
            end="",
        )
        for i in range(8):
            print(" %02i" % self.reg[i], end="")
        print(" | Stack:", end="")
        for i in range(240, 244):
            print(" %02i" % self.ram_read(i), end="")
        print()

    def ram_read(self, MAR):
        """Should accept the address to read and return the value stored there"""
        return self.ram[MAR]

    def ram_write(self, MDR, MAR):
        """Should accept a value to write, and the address to write it to."""
        self.ram[MAR] = MDR

    def handle_print(self, op_a=None, op_b=None):
        """ Print value from register """
        register_num = op_a
        value = self.reg[register_num]
        print(value)
        self.pc += 2

    def handle_halt(self, op_a=None, op_b=None):
        """ Stops program from running """
        self.running = False

    def handle_ldi(self, op_a=None, op_b=None):
        """ Store values in the register """
        register_num = op_a
        value = op_b

        self.reg[register_num] = value
        self.pc += 3

    def handle_push(self, op_a=None, op_b=None):
        # decrement the stack pointer
        self.reg[self.SP] -= 1  # address_of_the_top_of_stack -= 1

        # copy value from register into memory
        # reg_num = self.ram[self.pc + 1]
        reg_num = op_a

        value = self.reg[reg_num]  # this is what we want to push

        address = self.reg[self.SP]
        self.ram[address] = value  # store the value on the stack

        self.pc += 2

    def handle_pop(self, op_a=None, op_b=None):
        # copy value from memory into register
        address = self.reg[self.SP]
        value = self.ram[address]

        # reg_num = self.ram[self.pc + 1]
        reg_num = op_a

        self.reg[reg_num] = value

        # increment the stack pointer
        self.reg[self.SP] += 1

        self.pc += 2

    def handle_call(self, op_a=None, op_b=None):
        # Get the address directly after the call
        return_address = self.pc + 2

        # Push on the stack
        self.reg[self.SP] -= 1
        self.ram[self.reg[self.SP]] = return_address

        # Set the PC to the value in the given register
        reg_num = self.ram[self.pc + 1]
        dest_addr = self.reg[reg_num]

        self.pc = dest_addr

    def handle_return(self, op_a=None, op_b=None):
        # pop return address from top of stack
        return_addr = self.ram[self.reg[self.SP]]
        self.reg[self.SP] += 1

        # Set the pc
        self.pc = return_addr

    def handle_jump(self, op_a=None, op_b=None):
        # Jump to the address stored in the given register.
        # Set the PC to the address stored in the given register
        self.pc = self.reg[op_a]

    def handle_jeq(self, op_a=None, op_b=None):
        # If equal flag is set(true), jump to the address stored in the given register.
        # print("Flag:", self.flag)
        if self.flag & 0b00000001:
            self.pc = self.reg[op_a]
        else:
            self.pc += 2
        # self.flag = 0

    def handle_jne(self, op_a=None, op_b=None):
        # If E flag is clear (false, 0), jump to the address stored in the given register.
        # print("Flag:", self.flag)
        if self.flag != 0b00000001:
            self.pc = self.reg[op_a]
        else:
            self.pc += 2
        # self.flag = 0

    def run(self):
        """Run the CPU."""

        while self.running:
            # read the memory address that's stored in register PC and store that result in IR, Instruction Register
            IR = self.ram[self.pc]
            register_a = self.ram_read(self.pc + 1)
            register_b = self.ram_read(self.pc + 2)
            use_alu = (IR & 0b00100000) >> 5

            if use_alu:
                self.alu(IR, register_a, register_b)
                self.pc += 3
            elif self.branchtable.get(IR):
                self.branchtable[IR](register_a, register_b)
            else:
                print("Unknown instruction")
                self.running = False

            # self.trace()