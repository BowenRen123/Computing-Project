from enum import Enum
from constants import *

INSTRUCTION = 255
DATA = INSTRUCTION + 1

TYPE_FLOAT = DATA + 1
TYPE_INTEGER = TYPE_FLOAT + 1
TYPE_STRING = TYPE_INTEGER + 1

class VirtualMachine:

    def __init__(self,memory_size = 100):
        self.memory = [{}] * memory_size
        # program counter
        self.pc = 0
        # general registers
        self.r1 = 0
        self.r2 = 0
        self.r3 = 0
        self.r4 = 0
        self.r5 = 0
        self.r6 = 0  
        # accumulator
        self.acc = 0
        self.stack = 0 
        self.memory_size = memory_size
        # program state
        self.running = False

    def __validate_instruction(self,instruction_type,operands):
        # ensure instruction is valid
        if instruction_type not in range(MAX + 1) or instruction_type == None or operands == None:
            return False
        # check for appropriate type
        for operand in operands:
            if type(operand) not in [int,float,str]:
                return False

        # ensure appropriate instruction length
        # bi-operand instruction
        return (instruction_type in [ADD,SUB,COMPARE,LOAD,STORE] and len(operands) == 2) or \
        (instruction_type == JUMP and len(operands) == 1) or (instruction_type in [INPUT,OUTPUT,HALT] and not operands)
    
    def memory_full(self):
        return self.stack >= self.memory_size
    
    def validate_modes(self,modes,instruction_type):
        for mode in modes:

            # prevent values from being loaded into a constant
            if instruction_type in [LOAD,STORE] and modes[0] == 'i':
                return False

            if mode not in ['i','d','id','r']:
                return False
        return True
    
    def add_instruction(self,instruction_type,operands,modes=None):

        if not modes:
            modes = ['i'] * len(operands) # set all operand to be immediate mode by default

        while len(modes) < len(operands): # prefill empty modes with immedidate
            modes.append('i')

        if not self.validate_modes(modes,instruction_type):  
            print("Invalid mode for instruction operand! ")
            return False

        if self.memory_full():
            print("Memory is full! ")
            return False

        if not self.__validate_instruction(instruction_type,operands):
            print("Invalid instruction")
            return False
        
        for i in range(len(operands)):
            operands[i] = self.clean_data(operands[i],modes[i])

        # add the instruction to memory and increment the stack counter to point to next free space
        instruction = {
        "type":instruction_type,
        "operands":operands,
        "location":self.stack,
        "purpose":INSTRUCTION,
        "addressing-modes":modes}
        self.memory[self.stack] = instruction
        self.stack += 1

        print("successfully added instruction")

        return True
    
    def name_exists(self,name):
        for data_dict in self.memory:
            if data_dict == {}: continue
            if data_dict['purpose'] == DATA:
                if data_dict['name'] == name:
                    return True
        return False
    
    def verify_data(self,name,data):

        # prevent clashing with existing register names
        if name in ['r1','r2','r3','r4','r5','r6','acc','pc']:
            print("name clashes with existing register names! ")
            return False

        # prevent duplication
        if self.name_exists(name):
            print("Name already exists! ")
            return False
        
        # check name starts with a letter
        if len(name) > 0:
            if not str(name[0]).isalpha():
                return False

        # check type is okay and no whitespace and variable isnt empty
        if len(name) == 0 or str(name).__contains__(' ') or type(name) != str:
            print("Invalid name! ")
            return False
        
        # check data is of appropriate 
        if type(data) not in [int,float,str] or data == None:
            print("Invalid data! ")
            return False

        return True

    def get_data_type(self,data_type):
        if data_type == int:
            return TYPE_INTEGER
        elif data_type == float:
            return TYPE_FLOAT
        elif data_type == str:
            return TYPE_STRING

    """
        addressing mode:
            i -> immediate addressing (default value is used + default mode for add_data function)
            d -> direct addressing (value at the address of 'name' is used)
            r -> register (value is a register name) 
    """


    # convert the symbolic addressing into integer addressing! 
    def clean_data(self,data,mode):
        # uses constant 
        if mode == 'i':
            return data
        # returns an addresses
        if mode == 'd':
            if str(data).isdigit():
                return data
                # check that data exists
           
            if not self.name_exists(data):
                print(f'Error variable name: {data} does not exist! ')
                return None

            for data1 in self.memory:
                if data1 == {}:
                    continue
                
                if data1['purpose'] == DATA: 
                    if data1['name'] == data:
                        return data1['location'] 
             
            return None
        # value of a register
        if mode == 'r':
            if data not in ['r1','r2','r3','r4','r5','r6','acc','pc']:
                print("Error! data is not a register! ")
                return None
            
            return data

    def add_data(self,name,data,mode='i'): 
        # check if addressing mode is correct
        if mode.lower() not in ['i','d','r']:
            print("Invalid addressing mode! ")
            return False       
        
        # check if memory is full
        if self.memory_full():
            print("Memory is full! ")
            return False

        # verify the data
        if not self.verify_data(name,data):
            print(f"Invalid name!: {name} ")
            return False

        selected_type = self.get_data_type(type(data))
        data = self.clean_data(data,mode) 
        if data == None:
            print("data is invalid! ")
            return False

        # add the data to memory and increment the stack counter to point to next free space
        data_dict = {
        "name":name,
        "type":selected_type,
        "value":data,
        "location":self.stack,
        "purpose":DATA,
        "addressing-mode":mode.lower()}
        self.memory[self.stack] = data_dict
        self.stack += 1

        print("Successfully added data")

        return True

    # fetch an instruction/returns none is end of program is reached:
    def next_instruction(self):
        i = self.pc
        while i < self.memory_size:
            current,purpose = self.get_data(i)
            if current == {} or purpose == None:
                i += 1
                continue

            if purpose == INSTRUCTION:
                self.pc = i
                return current

            i += 1

        return None

    def run(self):
        
        self.running = True
        current_instruction = None
        while self.running:
            # fetch an instruction
            current_instruction = self.next_instruction()
             
            if current_instruction: 
                self.exec(current_instruction)
                self.increment_pc()
            else:
                self.stop()

    def increment_pc(self):
        self.pc += 1
        if self.pc >= self.memory_size:
            self.stop()

    # copy data from dest to src provided that src is not a literal
    def copy(self,src,dest,modes):
        if len(modes) != 2:
            print("Cannot load/store values between storage locations as modes length is not 2! ")
            return
        
        if modes[0] == 'd':
            self.set_data(src,dest)
        if modes[0] == 'r':
            self.set_register_value(src,dest)


    def exec(self,instruction):
    #     return (instruction_type in [ADD,SUB,COMPARE,LOAD,STORE] and len(operands) == 2) or \
    #     (instruction_type == JUMP and len(operands) == 1) or (instruction_type in [INPUT,OUTPUT,HALT] and not operands)
        opcode,operands,modes = instruction['type'],instruction['operands'],instruction['addressing-modes']
        print(f'operand data: {operands}')
        operands = self.parse_operands(operands,modes,opcode) # get the data of all operands

        if opcode in [ADD,SUB,COMPARE,LOAD,STORE]:
            if opcode == ADD:
                self.acc = operands[0] + operands[1]
            if opcode == SUB:
                self.acc = operands[0] - operands[1]
            if opcode == COMPARE:
                self.acc = operands[0] == operands[1]
            if opcode == LOAD:
                self.copy(operands[0],operands[1],modes)

        elif opcode == JUMP:
            pass
        elif opcode in [INPUT,OUTPUT,HALT]:
            if opcode == INPUT:
                self.acc = float(input())
            elif opcode == OUTPUT:
                print(self.acc)
            elif opcode == HALT:
                self.stop()

    def get_data_val(self,data,mode):
        if mode == 'i':
            return data
        if mode == 'd':
            pass
    
    def get_operand_data(self,operand):
        data,_ = self.get_data(operand)
        curr_mode = data['addressing-mode']

        while curr_mode == 'd':
            data,_ = self.get_data(data['value'])
            curr_mode = data['addressing-mode']

        if data['addressing-mode'] == 'i':
            return data['value']
        elif data['addressing-mode'] == 'r':
            return self.get_register_data(data['value'])


    def parse_operands(self,operands,modes,opcode):
        
        for i in range(len(operands)):
            
            operand = operands[i]
            mode = modes[i]

            # get data
            data = None
            if mode == 'd':
                # preserve first operand if instruction involves moving data
                data = self.get_operand_data(operand) if (opcode not in [LOAD,STORE] or i >= 1) else data
            elif mode == 'i':
                data = operand
            elif mode == 'r':
                # preserve first operand if instruction involves moving data
                data = self.get_register_data(operand) if (opcode not in [LOAD,STORE] or i >= 1) else data 

            operands[i] = data
        return operands    

    # get the value of a data in a memory cell based on its writing mode
   
    def get_register_data(self,operand):
        if operand == "r1":
            return self.r1
        if operand == "r2":
            return self.r2
        if operand == "r3":
            return self.r3
        if operand == "r4":
            return self.r4
        if operand == "r5":
            return self.r5
        if operand == "r6":
            return self.r6
        if operand == "acc":
            return self.acc
        if operand == "pc":
            return self.pc
        
    def set_register_value(self,operand,data):

        if operand == "r1":
            self.r1 = data
        if operand == "r2":
            self.r2 = data
        if operand == "r3":
            self.r3 = data
        if operand == "r4":
            self.r4 = data
        if operand == "r5":
            self.r5 = data
        if operand == "r6":
            self.r6 = data
        if operand == "acc":
            self.acc = data
        if operand == "pc":
            self.pc = data


    def stop(self):
        self.running = False

    def get_instruction_str(self,instruction_code):
        if instruction_code == ADD:
            return "add"
        if instruction_code == SUB:
            return "sub"
        if instruction_code == LOAD:
            return "load"
        if instruction_code == STORE:
            return "store"
        if instruction_code == COMPARE:
            return "compare"
        if instruction_code == JUMP:
            return "jump"
        if instruction_code == OUTPUT:
            return "output"
        if instruction_code == INPUT:
            return "input"
        if instruction_code == HALT:
            return "halt"
        
    def get_data_type_str(self,data_type):
        if data_type == TYPE_INTEGER:
            return 'int'
        if data_type == TYPE_FLOAT:
            return 'float'
        if data_type == TYPE_STRING:
            return 'string'
    
    def get_purpose_str(self,purpose):
        if purpose == DATA:
            return "data"
        elif purpose == INSTRUCTION:
            return "instruction"
        
    def __str__(self):
        my_str = f"\nregisters\npc: {self.pc} \nacc: {self.acc} \nr1: {self.r1}\nr2:"\
        f" {self.r2}\nr3: {self.r3}\nr4: {self.r4}\nr5: {self.r5}\nr6: {self.r6}\npc: {self.pc}\n"

        my_str += "\nmemory status \n"
        for data in self.memory:
            if data == {}:
                continue

            is_data = data['purpose'] == DATA
            if is_data:
                my_str += f'name: {data['name']}\n'
                my_str += f'type: {self.get_data_type_str(data['type'])}\n'
                my_str += f'data: {data['value']}\n'
                my_str += f'addressing-mode: {data['addressing-mode']}\n'
            else:
                my_str += f'Generic Instruction\n'
                my_str += f'type: {self.get_instruction_str(data['type'])}\n'
                my_str += f'operands: {data["operands"]}\n'
                my_str += f'addressing-modes: {data['addressing-modes']}\n'
 
            my_str += f'location: {data['location']}\n'
            my_str += f'purpose: {self.get_purpose_str(data['purpose'])}\n'
            my_str += "\n"

        return my_str

    def print_memory(self): 
        for data in self.memory:
            if data == {}:
                continue

            is_data = data['purpose'] == DATA
            if is_data:
                print(f'name: {data['name']}')
                print(f'type: {self.get_data_type_str(data['type'])}')
                print(f'data: {data['value']}')
                print(f'addressing-mode: {data['addressing-mode']}')
            else:
                print(f'Generic Instruction')
                print(f'type: {self.get_instruction_str(data['type'])}')
                print(f'operands: {data["operands"]}')
                print(f'addressing-modes: {data['addressing-modes']}')
 
            print(f'location: {data['location']}')
            print(f'purpose: {self.get_purpose_str(data['purpose'])}')
            print()

    def get_data(self,location):
        if location not in range(self.memory_size):
            print(f"Invalid location: {location}/{self.memory_size}")
            return (None,None)

        data_dict = self.memory[location]
        if data_dict == {}: return (data_dict,None)
        return (data_dict,data_dict["purpose"])
    
    def set_data(self,location,value):
        data_dict,purpose = self.get_data(location)
        if purpose == DATA:
            data_dict['value'] = value
            return True
        
        return False