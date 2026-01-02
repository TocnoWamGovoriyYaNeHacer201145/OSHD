import sys
import time
import random

stack = []
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
init_stacks = False

builtins = {
    '+': lambda a, b: a + b,
    '-': lambda a, b: a - b,
    '*': lambda a, b: a * b,
    '/': lambda a, b: a / b if b != 0 else 0,
    '%': lambda a, b: a % b if b != 0 else 0,
    '=': lambda: None,
    'import': lambda: imported_libs.__setitem__(stack.pop(), __import__(stack.pop())),
    'abs': lambda: stack.append(abs(check_for_var(stack.pop(), True))),
    'aiter': lambda: stack.append(aiter(stack.pop())),
    'print': lambda: print(check_for_var(stack.pop())),
    'get_inp': lambda: stack.append(input(stack.pop())),
    'dup': lambda: stack.append(stack[-1]),
    'del': lambda: stack.pop(),
    'time': lambda: stack.append(time.time()),
    'wait': lambda: time.sleep(check_for_var(stack.pop())),
    'randint': lambda: stack.append(random.randint(stack.pop(), stack.pop())),
    'pyexec': lambda: exec(stack.pop(), variables),
    'int': lambda: stack.append(int(stack.pop())),
    'str': lambda: stack.append(str(stack.pop())),
    'fun': lambda: globals().__setitem__('current_edit', 'fun'),
    'if': lambda: globals().__setitem__('current_edit', 'if'),
    'for': lambda: globals().__setitem__('current_edit', 'for'),
    '"': lambda: globals().__setitem__('current_edit', 'string'),
    '//': lambda: globals().__setitem__('current_edit', 'comment'),
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
    try: arg1 = int(check_for_var(arg1))
    except: arg1 = check_for_var(arg1)
    try: arg2 = int(check_for_var(arg2))
    except: arg2 = check_for_var(arg2)
    if arg3 in syntax_expr:
        return syntax_expr[arg3](arg1, arg2)

def check_for_var(arg, arg1=None):
    return variables.get(arg, arg)

def execute(arg):
    global stack, variables, init_stacks, current_edit
    will_pass = False
    if init_stacks == False:
        if not hasattr(execute, 'fun_stack'): execute.fun_stack = []
        if not hasattr(execute, 'if_stack'): execute.if_stack = []
        if not hasattr(execute, 'for_stack'): execute.for_stack = []
        if not hasattr(execute, 'string_stack'): execute.string_stack = []
        if not hasattr(execute, 'comment_stack'): execute.comment_stack = []
        init_stacks = True
    else: pass
    if current_edit == None:
        if arg == '=':
            name = stack.pop()
            value = check_for_var(stack.pop())
            try: value = int(value)
            except: value = str(value)
            variables[name] = value
            stack.append(variables[name])
        elif arg in builtins:
            if len(arg) > 1:
                builtins[arg]()
            else:
                b = check_for_var(stack.pop())
                a = check_for_var(stack.pop())
                stack.append(builtins[arg](a, b))
        elif arg in fun_list:
            for fun_cmd in fun_list[arg].split():
                execute(fun_cmd)
        else:
            try:
                stack.append(int(arg))
            except:
                if '|' in arg:
                    parts = arg.split('|')
                    final_parts = []
                    for part in parts:
                        if part == '': continue
                        final_parts.append(str(check_for_var(part)))
                    stack.append(' '.join(final_parts))
                elif '.' in str(arg):
                    _arg = arg.split('.')
                    if hasattr(imported_libs[_arg[0]], f'_{check_for_var(_arg[1])}'):
                        stack = getattr(imported_libs[_arg[0]], f'_{check_for_var(_arg[1])}')(stack)
                else:
                    try: stack.append(check_for_var(arg))
                    except: stack.append(arg)
    else:
        if arg == 'end':
            if current_edit == 'fun':
                new_fun_name = str(execute.fun_stack[0])
                execute.fun_stack.remove(new_fun_name)
                new_fun_body = ' '.join(str(item) for item in execute.fun_stack)
                fun_list[new_fun_name] = new_fun_body
                execute.fun_stack = []; current_edit = None
            elif current_edit == 'if':
                new_if_body = execute.if_stack[3:]
                try: arg1 = check_for_var(int(execute.if_stack[0]))
                except: arg1 = check_for_var(execute.if_stack[0])
                try: arg2 = check_for_var(int(execute.if_stack[1]))
                except: arg2 = check_for_var(execute.if_stack[1])
                op = execute.if_stack[2]
                condition = True_or_False(arg1, arg2, op)
                execute.if_stack = []; current_edit = None
                if condition == True:
                    for cmd in new_if_body:
                        execute(cmd)
            elif current_edit == 'for':
                new_for_args = execute.for_stack[:3]
                new_for_body = execute.for_stack[3:]
                var_name = new_for_args[0]
                arg1 = check_for_var(new_for_args[0], True)
                arg2 = check_for_var(new_for_args[1], True)
                op = new_for_args[2]
                execute.for_stack = []; current_edit = None
                while len(stack) > 0: stack.pop()
                while True:
                    arg1 = check_for_var(var_name, True)
                    if not True_or_False(arg1, arg2, op): break
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
            execute.comment_stack = []; current_edit = None
        else:
            if current_edit == 'fun':
                execute.fun_stack.append(check_for_var(arg))
            elif current_edit == 'if':
                execute.if_stack.append(check_for_var(arg))
            elif current_edit == 'for':
                execute.for_stack.append(check_for_var(arg))
            elif current_edit == 'string':
                execute.string_stack.append(check_for_var(arg))
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
