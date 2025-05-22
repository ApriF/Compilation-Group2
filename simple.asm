

extern printf, atoi
section .data
argv: dq 0
y: dq 0
c: dq 0
x: dq 0
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
jmp loop5
end5: nop
jmp end4
at4: nop
end4: nop
mov rax, [x]
add rax, [x]
mov r8, [x]
add rax, r8
mov r8, [y]
add r8, [y]
add rax, r8
mov r8, [z]
add rax, r8
mov r8, [x]
add r8, [x]
mov r9, [x]
add r8, r9
mov r9, [y]
add r9, [y]
add r8, r9
mov r9, [z]
add r8, r9
mov r9, [x]
add r9, [x]
mov r10, [x]
add r9, r10
mov r10, [y]
add r10, [y]
add r9, r10
mov r10, [z]
add r9, r10
mov r10, [x]
add r10, [x]
mov r11, [x]
add r10, r11
mov r11, [y]
add r11, [y]
add r10, r11
mov r11, [z]
add r10, r11
mov r11, [x]
add r11, [x]
mov r12, [x]
add r11, r12
mov r12, [y]
add r12, [y]
add r11, r12
mov r12, [z]
add r11, r12
mov r12, [x]
add r12, [x]
mov r13, [x]
add r12, r13
mov r13, [y]
add r13, [y]
add r12, r13
mov r13, [z]
add r12, r13
mov r13, [x]
add r13, [x]
mov r14, [x]
add r13, r14
mov r14, [y]
add r14, [y]
add r13, r14
mov r14, [z]
add r13, r14
mov r14, [x]
add r14, [x]
mov r15, [x]
add r14, r15
mov r15, [y]
add r15, [y]
add r14, r15
mov r15, [z]
add r14, r15
mov r15, [x]
add r15, [x]
mov rbx, [x]
add r15, rbx
mov rbx, [y]
add rbx, [y]
add r15, rbx
mov rbx, [z]
add r15, rbx
mov rbx, [x]
add rbx, [x]
push rbx
mov rbx, [x]
mov rcx, rbx
pop rbx
add rbx, rcx
push rbx
mov rbx, [y]
add rbx, [y]
mov rcx, rbx
pop rbx
add rbx, rcx
push rbx
mov rbx, [z]
mov rcx, rbx
pop rbx
add rbx, rcx
push rbx
mov rbx, [x]
add rbx, [x]
push rbx
mov rbx, [x]
mov rcx, rbx
pop rbx
add rbx, rcx
push rbx
mov rbx, [y]
add rbx, [y]
mov rcx, rbx
pop rbx
add rbx, rcx
push rbx
mov rbx, [z]
mov rcx, rbx
pop rbx
add rbx, rcx
mov rcx, rbx
pop rbx
add rbx, rcx
add r15, rbx
add r14, r15
add r13, r14
add r12, r13
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
