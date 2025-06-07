

extern printf, atoi
section .data
argv: dq 0
e: dq 0
x: dq 0
d: dq 0
c: dq 0
y: dq 0
z: dq 0

fmt: db "%d", 10,0

global main
section .text
main:
push rbp ; heap: ['rbp']
mov [argv], rsi ; [argv]:['rsi']
mov rbx, [argv] ; rbx:['[argv]', 'rsi']
mov rdi, [rbx+8] ; rdi:['[rbx+8]']
call atoi
mov [x], rax ; [x]:['rax']
mov rbx, [argv] ; rbx:['[argv]', 'rsi']
mov rdi, [rbx+16] ; rdi:['[rbx+16]', '[rbx+8]']
call atoi
mov [y], rax ; [y]:['rax']
mov rbx, [argv] ; rbx:['[argv]', 'rsi']
mov rdi, [rbx+24] ; rdi:['[rbx+24]', '[rbx+16]', '[rbx+8]']
call atoi
mov [z], rax ; [z]:['rax']

mov rax, 0 ; rax=0, rax:[]
mov [c], rax ; [c]:['rax']
mov rax, 0 ; rax=0, rax:[]
mov [d], rax ; [d]:['rax']
mov rax, 5 ; rax=5, rax:[]
mov [e], rax ; [e]:['rax']
mov rax, [c] ; rax:['[c]', 'rax']
cmp rax, 0 ; rax:['[c]', 'rax']
jz at9
mov rax, [x] ; rax:['[c]', 'rax', '[x]']
mov r8, 1 ; r8=1, r8:[]
add rax, r8 ; rax:['r8', '[c]', 'rax', '[x]']
mov [x], rax ; [x]:['[c]', 'rax', '[x]', 'r8']
jmp end9
at9: mov rax, [x]
add rax, [x] ; rax:['[c]', 'rax', '[x]', 'r8']
mov [x], rax ; [x]:['[c]', 'rax', '[x]', 'r8']
end9: nop
mov rax, [d] ; rax:['[d]', '[c]', 'rax', '[x]', 'r8']
cmp rax, 0 ; rax:['[d]', '[c]', 'rax', '[x]', 'r8']
jz at13
mov rax, 10 ; rax=10, rax:[]
mov [z], rax ; [z]:['rax']
jmp end13
at13: nop
end13: nop
loop15: mov rax, [x]
cmp rax, 0 ; rax=10, rax:[]
jz end15
mov rax, [x] ; rax:['r8', '[c]', 'rax', '[x]']
mov r8, 1 ; r8=1, r8:[]
sub rax, r8 ; rax:['r8', '[c]', 'rax', '[x]']
mov [x], rax ; [x]:['[c]', 'rax', '[x]', 'r8']
mov rax, [y] ; rax:['[y]', '[c]', 'rax', '[x]', 'r8']
mov r8, 3 ; r8=3, r8:[]
add rax, r8 ; rax:['[y]', '[c]', 'rax', '[x]', 'r8']
mov [y], rax ; [y]:['[y]', '[c]', 'rax', '[x]', 'r8']
mov rax, [z] ; rax:['[y]', '[z]', '[c]', 'rax', '[x]', 'r8']
add rax, [z] ; rax:['[y]', '[z]', '[c]', 'rax', '[x]', 'r8']
mov [z], rax ; [z]:['[y]', '[z]', '[c]', 'rax', '[x]', 'r8']
mov rax, [c] ; rax:['[y]', '[z]', '[c]', 'rax', '[x]', 'r8']
mov r8, 5 ; r8=5, r8:[]
add rax, r8 ; rax:['[y]', '[z]', '[c]', 'rax', '[x]', 'r8']
mov [c], rax ; [c]:['[y]', '[z]', '[c]', 'rax', '[x]', 'r8']
mov rax, [d] ; rax:['[y]', '[z]', '[c]', 'rax', '[d]', '[x]', 'r8']
mov r8, 1 ; r8=1, r8:[]
sub rax, r8 ; rax:['[y]', '[z]', '[c]', 'rax', '[d]', '[x]', 'r8']
mov [d], rax ; [d]:['[y]', '[d]', '[z]', '[c]', 'rax', '[x]', 'r8']
jmp loop15
end15: nop
mov rax, [x] ; rax:['[y]', '[d]', '[z]', '[c]', 'rax', '[x]', 'r8']
add rax, [y] ; rax:['[y]', '[d]', '[z]', '[c]', 'rax', '[x]', 'r8']
mov r8, [z] ; r8:['[y]', '[z]', '[c]', 'rax', '[x]', 'r8']
add rax, r8 ; rax:['[y]', '[d]', '[z]', '[c]', 'rax', '[x]', 'r8']
mov r8, [d] ; r8:['[y]', '[d]', '[z]', '[c]', 'rax', '[x]', 'r8']
add r8, [d] ; r8:['[y]', '[d]', '[z]', '[c]', 'rax', '[x]', 'r8']
mov r9, [d] ; r9:['[y]', '[z]', '[c]', '[d]', 'rax', '[x]', 'r8']
add r8, r9 ; r8:['[y]', '[d]', '[z]', '[c]', 'rax', '[x]', 'r9', 'r8']
add rax, r8 ; rax:['[y]', '[d]', '[z]', '[c]', 'rax', '[x]', 'r9', 'r8']
mov [z], rax ; [z]:['[y]', '[d]', '[z]', '[c]', 'rax', '[x]', 'r9', 'r8']
mov rax, [y] ; rax:['[y]', '[d]', '[z]', '[c]', 'rax', '[x]', 'r9', 'r8']
add rax, [e] ; rax:['[y]', '[d]', '[z]', '[c]', 'rax', '[x]', '[e]', 'r9', 'r8']
mov [y], rax ; [y]:['[y]', '[d]', '[z]', '[c]', 'rax', '[x]', '[e]', 'r9', 'r8']
mov rax, [z] ; rax:['[y]', '[d]', '[z]', '[c]', 'rax', '[x]', '[e]', 'r9', 'r8']
mov rdi, fmt ; rdi:['fmt', '[rbx+24]', '[rbx+16]', '[rbx+8]']
mov rsi, rax ; rsi:['[y]', '[d]', '[z]', '[c]', 'rax', '[x]', '[e]', 'r9', 'r8']
xor rax, rax
call printf
pop rbp ; rbp:['rbp']
ret