

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
push rbp
mov [argv], rsi
mov rbx, [argv]
mov rdi, [rbx+8]
call atoi
mov [x], rax
mov rbx, [argv]
mov rdi, [rbx+16]
call atoi
mov [y], rax
mov rbx, [argv]
mov rdi, [rbx+24]
call atoi
mov [z], rax

mov rax, 0
mov [c], rax
mov rax, 0
mov [d], rax
mov rax, 5
mov [e], rax
mov rax, [c]
cmp rax, 0
jz at9
mov rax, [x]
mov r8, 1
add rax, r8
mov [x], rax
jmp end9
at9: mov rax, [x]
add rax, [x]
mov [x], rax
end9: nop
mov rax, [d]
cmp rax, 0
jz at13
mov rax, 10
mov [z], rax
jmp end13
at13: nop
end13: nop
loop15: mov rax, [x]
cmp rax, 0
jz end15
mov rax, [x]
mov r8, 1
sub rax, r8
mov [x], rax
mov rax, [y]
mov r8, 3
add rax, r8
mov [y], rax
mov rax, [z]
add rax, [z]
mov [z], rax
mov rax, [c]
mov r8, 5
add rax, r8
mov [c], rax
mov rax, [d]
mov r8, 1
sub rax, r8
mov [d], rax
jmp loop15
end15: nop
mov rax, [x]
add rax, [y]
mov r8, [z]
add rax, r8
mov r8, [d]
add r8, [d]
mov r9, [d]
add r8, r9
add rax, r8
mov [z], rax
mov rax, [y]
add rax, [e]
mov [y], rax
mov rax, [z]
mov rdi, fmt
mov rsi, rax
xor rax, rax
call printf
pop rbp
ret
