

extern printf, atoi
section .data
argv: dq 0
x: dq 0
z: dq 0
c: dq 0
y: dq 0

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
mov rax, [c]
cmp rax, 0
jz at4
loop5: mov rax, [x]
cmp rax, 0
jz end5
mov rax, [x]
mov r8, 1
sub rax, r8
mov [x], rax
mov rax, [y]
mov r8, 3
add rax, r8
mov [y], rax
mov rax, [z]
add rax, [x]
mov r8, [z]
add rax, r8
mov [z], rax
mov rax, [x]
add rax, [y]
mov r8, [z]
add r8, [z]
mov r9, [x]
add r9, [y]
add r8, r9
mov r9, [z]
add r9, [z]
mov r10, [x]
add r10, [y]
add r9, r10
mov r10, [z]
add r10, [z]
mov r11, [x]
add r11, [y]
add r10, r11
mov r11, [z]
add r11, [z]
mov r12, [x]
add r12, [y]
add r11, r12
mov r12, [z]
add r12, [z]
mov r13, [x]
add r13, [y]
add r12, r13
mov r13, [z]
add r13, [z]
mov r14, [x]
add r14, [y]
add r13, r14
mov r14, [z]
add r14, [z]
mov r15, [x]
add r15, [y]
add r14, r15
add r13, r14
add r12, r13
add r11, r12
add r10, r11
add r9, r10
add r8, r9
add rax, r8
mov [y], rax
jmp loop5
end5: nop
jmp end4
at4: nop
end4: nop
mov rax, [z]
add rax, [z]
mov r8, [z]
add rax, r8
mov r8, [y]
add r8, [y]
add rax, r8
mov r8, [z]
add rax, r8
mov r8, [z]
add r8, [z]
mov r9, [z]
add r8, r9
mov r9, [y]
add r9, [y]
add r8, r9
mov r9, [z]
add r8, r9
mov r9, [z]
add r9, [z]
mov r10, [z]
add r9, r10
mov r10, [y]
add r10, [y]
add r9, r10
mov r10, [z]
add r9, r10
mov r10, [z]
add r10, [z]
mov r11, [z]
add r10, r11
mov r11, [y]
add r11, [y]
add r10, r11
mov r11, [z]
add r10, r11
mov r11, [z]
add r11, [z]
mov r12, [z]
add r11, r12
mov r12, [y]
add r12, [y]
add r11, r12
mov r12, [z]
add r11, r12
add r10, r11
add r9, r10
add r8, r9
add rax, r8
mov [z], rax
mov rax, [z]
mov rdi, fmt
mov rsi, rax
xor rax, rax
call printf
pop rbp
ret
