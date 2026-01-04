import sys
import time
import random

stack = []
ret_stack = []
variables = {
    '__version': '0.0.9-alpha',
    '__platform': sys.platform,
    'true': True, 
    'false': False,
    'null': None
}
fun_list = {}
imported_libs = {}
current_edit = None

builtins = {
    # Math
    '+': lambda a, b: a + b,
    '-': lambda a, b: a - b,
    '*': lambda a, b: a * b,
    '/': lambda a, b: a / b if b != 0 else 0,
    '%': lambda a, b: a % b if b != 0 else 0,
    'abs': lambda: stack.append(abs(check_for_var(stack.pop()))),
    # I/O
    'print': lambda: print(check_for_var(stack.pop())),
    'input': lambda: stack.append(input(stack.pop())),
    # Stack
    'dup': lambda: stack.append(stack[-1]),
    'swap': lambda: swap(),
    'over': lambda: stack.append(stack[-2]),
    'drop': lambda: stack.pop(),
    'depth': lambda: stack.append(len(stack)),
    'clear': lambda: stack.clear(),
    # Cool things
    'time': lambda: stack.append(time.time()),
    'wait': lambda: time.sleep(check_for_var(stack.pop())),
    'randint': lambda: stack.append(random.randint(stack.pop(), stack.pop())),
    '=': lambda: None,
    # Types
    'int': lambda: stack.append(int(stack.pop())),
    'str': lambda: stack.append(str(stack.pop())),
    # Return stack
    '>ret': lambda: ret_stack(stack.pop()),
    'ret>': lambda: stack.append(ret_stack.pop()),
    'ret@': lambda: stack.append(ret_stack[-1]),
    # Modes
    'fun': lambda: globals().__setitem__('current_edit', 'fun'),
    'if': lambda: globals().__setitem__('current_edit', 'if'),
    'for': lambda: globals().__setitem__('current_edit', 'for'),
    '""': lambda: globals().__setitem__('current_edit', 'string'),
    '//': lambda: globals().__setitem__('current_edit', 'comment'),
    # Py things
    'import': lambda: imported_libs.__setitem__(stack.pop(), __import__(stack.pop())),
    'pyexec': lambda: exec(stack.pop(), variables)
}

syntax_expr = {
    '<': lambda a, b: a < b,
    '>': lambda a, b: a > b,
    '==': lambda a, b: a == b,
    '!=': lambda a, b: a != b,
    '>=': lambda a, b: a >= b,
    '<=': lambda a, b: a <= b
}

def True_or_False(arg1, arg2, arg3):
    if arg3 in syntax_expr:
        try: return syntax_expr[arg3](int(arg1), int(arg2))
        except: return syntax_expr[arg3](arg1, arg2)

def check_for_var(arg):
    return variables.get(arg, arg)

def swap():
    obj1 = stack.pop()
    obj2 = stack.pop()
    stack.append(obj1)
    stack.append(obj2)

def execute(arg):
    global stack, variables, current_edit
    if current_edit == None:
        if arg == '=':
            name = stack.pop()
            variables[name] = check_for_var(stack.pop())
            stack.append(variables[name])
        elif arg in builtins:
            if len(arg) > 1:
                builtins[arg]()
            else:
                b = check_for_var(stack.pop())
                a = check_for_var(stack.pop())
                stack.append(builtins[arg](a, b))
        elif arg in fun_list:
            for fun_cmd in fun_list[arg]:
                execute(fun_cmd)
        else:
            try:
                stack.append(int(arg))
            except:
                if '|' in arg:
                    stack.append(' '.join(str(check_for_var(part)) for part in arg.split('|') if part))
                elif '.' in str(arg):
                    _arg = arg.split('.')
                    if hasattr(imported_libs[_arg[0]], f'_{check_for_var(_arg[1])}'):
                        stack = getattr(imported_libs[_arg[0]], f'_{check_for_var(_arg[1])}')(stack)
                else:
                    stack.append(variables.get(arg, arg))
    else:
        if arg == 'end':
            if current_edit == 'fun':
                new_fun_name = str(execute.fun_stack[0])
                execute.fun_stack.remove(new_fun_name)
                new_fun_body = list(map(str, execute.fun_stack))
                fun_list[new_fun_name] = new_fun_body
                execute.fun_stack = []; current_edit = None
            elif current_edit == 'if':
                new_if_body = execute.if_stack[3:]
                try: arg1 = check_for_var(int(execute.if_stack[0]))
                except: arg1 = check_for_var(execute.if_stack[0])
                try: arg2 = check_for_var(int(execute.if_stack[1]))
                except: arg2 = check_for_var(execute.if_stack[1])
                condition = True_or_False(arg1, arg2, execute.if_stack[2])
                execute.if_stack = []; current_edit = None
                if condition:
                    for cmd in new_if_body:
                        execute(cmd)
            elif current_edit == 'for':
                new_for_args = execute.for_stack[:3]
                new_for_body = execute.for_stack[3:]
                var_name = new_for_args[0]
                arg1 = check_for_var(new_for_args[0])
                arg2 = check_for_var(new_for_args[1])
                op = new_for_args[2]
                execute.for_stack = []; current_edit = None
                while True:
                    arg1 = variables.get(var_name, var_name)
                    if True_or_False(arg1, arg2, op) == False: break
                    for cmd in new_for_body:
                        execute(cmd)
        elif arg == '/"' and current_edit == 'string':
            final_stack = []
            for obj in execute.string_stack:
                obj = str(check_for_var(obj))
                final_stack.append(obj)
            stack.append(' '.join(final_stack))
            execute.string_stack = []; current_edit = None
        elif arg == '*/' and current_edit == 'comment':
            current_edit = None
        else:
            if current_edit == 'fun':
                execute.fun_stack.append(variables.get(arg, arg))
            elif current_edit == 'if':
                execute.if_stack.append(variables.get(arg, arg))
            elif current_edit == 'for':
                execute.for_stack.append(variables.get(arg, arg))
            elif current_edit == 'string':
                execute.string_stack.append(variables.get(arg, arg))

execute.fun_stack = []
execute.if_stack = []
execute.for_stack = []
execute.string_stack = []

def process_line(line):
    line = line.split()
    for cmd in line:
        execute(cmd)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python3 oshd.py <.oshd file>')
        sys.exit(1)
    with open(sys.argv[1], 'r') as file:
        for line in file:
            if not line.startswith('//'):
                process_line(line)
