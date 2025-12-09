import sys
import time
import random

stack=[]
fun_stack=[]
if_stack=[]
variables = {}
comment_stack = []
fun_list={}
main_edit = False
current_edit = None

def True_or_False(arg1, arg2, arg3):
    print(stack)
    arg1 = check_for_var(arg1); 
    arg2 = check_for_var(arg2)
    try: arg1 = int(arg1); arg2 = int(arg2)
    except: pass
    if arg3 == '>':
        return arg1 > arg2
    elif arg3 == '<':
        return arg1 < arg2
    elif arg3 == '==':
        return arg1 == arg2
    elif arg3 == '!=':
        return arg1 != arg2
    elif arg3 == '>=':
        return arg1 >= arg2
    elif arg3 == '<=':
        return arg1 <= arg2

def print_err(*args, **kwargs): print('', *args, **kwargs)

def check_for_var(arg, arg1=None):
    return variables.get(arg, arg)

def execute(arg):
    global variables, main_edit, current_edit, fun_stack, if_stack
    if not hasattr(execute, 'for_stack'): execute.for_stack = []
    if not hasattr(execute, 'comment_stack'): execute.comment_stack = []
    if main_edit == False:
        if arg == '+':
            b = check_for_var(stack.pop(), True)
            a = check_for_var(stack.pop(), True)
            stack.append(a + b)
        elif arg == '-':
            b = check_for_var(stack.pop(), True)
            a = check_for_var(stack.pop(), True)
            stack.append(a - b)
        elif arg == '*':
            b = check_for_var(stack.pop(), True)
            a = check_for_var(stack.pop(), True)
            stack.append(a * b)
        elif arg == '/':
            b = check_for_var(stack.pop())
            a = check_for_var(stack.pop())
            stack.append(a / b)
        elif arg == '=':
            name = stack.pop()
            value = stack.pop()
            try: value = int(value)
            except: pass
            variables[name] = value
            stack.append(check_for_var(value))
        elif arg == 'abs':
            stack.append(abs(check_for_var(stack.pop(), True)))
        elif arg == 'aiter':
            stack.append(aiter(stack.pop()))
        elif arg == 'print':
            print(check_for_var(stack.pop()))
        elif arg == 'get_inp':
            stack.append(input(stack.pop()))
        elif arg == 'read':
            file = check_for_var(stack.pop())
            try: 
                with open(file, 'r') as f:
                    stack.append(f.read())
            except Exception as e: 
                print_err(f'Failed to read file {file}: {e}')
        elif arg == 'write':
            file = check_for_var(stack.pop())
            content = check_for_var(stack.pop())
            try:
                with open(file, 'w') as f:
                    f.write(content)
            except:
                print_err(f'Failed to write content to {file}')
        elif arg == 'list':
            list1 = stack.copy()
            stack.clear()
            stack.append(list1)
        elif arg == 'dup':
            stack.append(stack[-1])
        elif arg == 'del':
            stack.pop()
        elif arg == 'time':
            stack.append(time.time())
        elif arg == 'wait':
            time.sleep(check_for_var(stack.pop()))
        elif arg == 'randint':
            stack.append(random.randint(1, 100))
        elif arg == 'fun':
            main_edit = True
            current_edit = 'fun'
        elif arg == 'if':
            main_edit = True
            current_edit = 'if'
        elif arg == 'for':
            main_edit = True
            current_edit = 'for'
        elif arg in fun_list:
            for fun_cmd in fun_list[arg].split():
                execute(fun_cmd)
        elif arg == '//':
            if main_edit == False:
                main_edit = True
                current_edit = 'comment'
            else:
                pass
        else:
            try:
                stack.append(int(arg))
            except:
                if '|' in arg:
                    parts = arg.split('|')
                    final_parts = []
                    for part in parts:
                        if part == '': continue
                        val = str(check_for_var(part))
                        final_parts.append(val)
                    stack.append(' '.join(final_parts))
                else:
                    try: stack.append(check_for_var(arg))
                    except: stack.append(arg)
    else:
        if arg == 'fun_end' and current_edit == 'fun':
            new_fun_name = fun_stack[0]
            fun_stack.remove(new_fun_name)
            new_fun_body = ' '.join(fun_stack)
            fun_list[new_fun_name] = new_fun_body
            fun_stack = []; main_edit = False; current_edit = None
        elif arg == 'if_end' and current_edit == 'if':
            new_if_body = if_stack[3:]
            try: arg1 = check_for_var(int(if_stack[0]))
            except: arg1 = check_for_var(if_stack[0])
            try: arg2 = check_for_var(int(if_stack[1]))
            except: arg2 = check_for_var(if_stack[1])
            op = if_stack[2]
            condition = True_or_False(arg1, arg2, op)
            if_stack = []; main_edit = False; current_edit = None
            if condition == True:
                for cmd in new_if_body:
                    execute(cmd)
        elif arg == 'for_end' and current_edit == 'for':
            new_for_args = execute.for_stack[:3]
            new_for_body = execute.for_stack[3:]
            var_name = new_for_args[0]
            arg1 = check_for_var(new_for_args[0], True)
            arg2 = check_for_var(new_for_args[1], True)
            op = new_for_args[2]
            execute.for_stack = []; main_edit = False; current_edit = None
            while True:
                arg1 = check_for_var(var_name, True)
                if not True_or_False(arg1, arg2, op): break
                for cmd in new_for_body:
                    execute(cmd)
                stack.pop()
        elif arg == '*/' and current_edit == 'comment':
            execute.comment_stack = []; main_edit = False; current_edit = None
        else:
            if current_edit == 'fun':
                fun_stack.append(arg)
            elif current_edit == 'if':
                if_stack.append(arg)
            elif current_edit == 'for':
                execute.for_stack.append(arg)
            elif current_edit == 'comment':
                execute.comment_stack.append(arg)
def process_line(line):
    line = line.strip()
    if line and not line.startswith('//'):
        commands = line.split()
        for cmd in commands:
            execute(cmd)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python3 oshd.py <.oshd file>')
        sys.exit(1)
    with open(sys.argv[1], 'r') as file:
        for line in file:
            process_line(line)
