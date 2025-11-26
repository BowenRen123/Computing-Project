from virtual_machine import VirtualMachine
import constants as cs

def test_instruction_operands(do_print=True):
    machine = VirtualMachine()

    testing_data = [list(range(x+1)) for x in range(3)]
    testing_data.insert(0,[])
    print("Testing double operand instructions")
    for data in testing_data:
        if do_print:
          print(data)
          print(f"testing for {len(data)} operands")
        machine.add_instruction(cs.ADD,data)
        machine.add_instruction(cs.SUB,data)
        machine.add_instruction(cs.COMPARE,data)
        machine.add_instruction(cs.LOAD,data)
        machine.add_instruction(cs.STORE,data)  

    print()
    print("Testing single operand instruction")
    machine.add_instruction(cs.JUMP,testing_data[1])
    print()
    print("Testing no operand instruction")
    for data in testing_data:
        if do_print:
            print(data)
            print(f"testing for {len(data)} operands")
        machine.add_instruction(cs.INPUT,data)
        machine.add_instruction(cs.OUTPUT,data)
        machine.add_instruction(cs.HALT,data)

    machine.print_memory()

def test_data_appending():
    print("testing integers: ")
    data = [i for i in range(10)]
    machine = VirtualMachine()
    for number in data:
        machine.add_data(f"variable_{number}",number)

    machine.print_memory()

    print("testing strings: ")
    data = [f'str_{i}' for i in range(10)]
    machine = VirtualMachine()
    for number in data:
        print(f"a_{number}")
        machine.add_data(f"a_{number}",number)

    machine.print_memory()

    print("testing floats")
    data = [float(i) for i in range(10)]
    machine = VirtualMachine()
    for number in data:
        machine.add_data(f"variable_{number}",number)

    machine.print_memory()

def test_name_duplication():
    machine = VirtualMachine(memory_size=4)
    machine.add_data(f'1',2)

    machine.add_data(f'b',2)

    machine.add_data(f'c',2)

    machine.add_data(f'd',2)
    print('=' * 12)
    machine.print_memory() 

# test_name_duplication()

# test_data_appending()
#test_instruction_operands(do_print=False)

def test_execution():
    vm = VirtualMachine()
    
    vm.add_data('x',50,mode='i',notes=0)      
    vm.add_data('y',25,mode='i',notes=1)
    vm.add_data('z','y',mode='d',notes=2)
    vm.add_data('t','r1',mode='r',notes=3)
    vm.add_data('y1','r1',mode='r',notes=4)
    # vm.add_instruction(cs.ADD,[5,2],['i','i'])
    # vm.add_instruction(cs.SUB,[2,3],['i','i'])
    vm.add_instruction(cs.LOAD,['r1','x'],['r','d'],notes=5)
    vm.add_instruction(cs.JUMP,[8],notes=6)
    vm.add_instruction(cs.SUB,['x','y'],['d','d'],notes=7)
    vm.add_instruction(cs.OUTPUT,notes=8)
    vm.add_instruction(cs.COMPARE,['y','r1'],['d','r'],notes=9)
    vm.add_instruction(cs.LOAD,['acc','x'],['r','d'],notes=5)

    print('=' * 12) 
    vm.run(True) 
    print(vm)
    
test_execution()