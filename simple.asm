

extern printf, atoi
section .data
argv: dq 0
y: dq 0
x: dq 0

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

loop1: mov rax, [x]
cmp rax, 0
jz end1
mov rax, [x]
mov r8, 1
sub rax, r8
mov [x], rax
mov rax, [y]
mov r8, 3
add rax, r8
mov [y], rax
jmp loop1
end1: nop
mov rax, [y]
mov rdi, fmt
mov rsi, rax
xor rax, rax
call printf
pop rbp
ret
