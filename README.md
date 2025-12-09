# What is OSHD?
OSHD is a stack-oriented programming language, with Polish reverse notation. 
In it, you can check conditions, add functions, and make loops. 
Overall, I just wanted to do something better than U# and RANDG. 
And so it really happened. Soon it will be more optimized, or will be rewritten in Rust, Go, or C. 
But okay, here's what "Hello, world!" would look like in this language: 
``` 
Hello,|world! print
```
In this language, "|" serve as spaces, just a function that divides code into arguments and cuts them into "". 
This language stores all variables directly in builtins, so I wouldn't recommend doing anything dangerous, 
it would break Python itself. 
Here's also what functions and so on look like in this language: 
```
10 aa =
0 i =
fun print_aa
  aa print
fun_end

print_aa // function call */

if 2 2 ==
  2|equals|2 print
if_end

for i 10 <
  i 1 + i =
  i print
for_end
```
## Usage:

```
python3 oshd.py <your oshd file>
```

##License
OSHD licensed under MIT License
