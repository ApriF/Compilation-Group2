extern printf, atoi
section .data
argv: dq 0
a: dq 0
b: dq 0
x: dq 0
p: dq 0
q: dq 0
kk: dq 0
y: dq 0

fmt: db "%d", 10,0

section .rdata
float_3_14: dq 3.14
float_2_3: dq 2.3
float_3_e14: dq 3.e14
float_7_: dq 7.
float_2_7: dq 2.7


global main
section .text
main:
push rbp
mov [argv], rsi
mov rbx, [argv]
mov rdi, [rbx+8]
call atoi
mov [a], rax
mov rbx, [argv]
mov rdi, [rbx+16]
call atoi
mov [b], rax


movsd xmm0, QWORD [float_2_7]
movsd xmm1, xmm0
movsd xmm0, QWORD [float_2_3]
addsd xmm0, xmm1
movsd [x], xmm0

movsd xmm0, QWORD [float_3_14]
movsd [x], xmm0

movsd xmm0, QWORD [float_3_e14]
movsd [x], xmm0


mov r8, 3
mov [p], r8


mov r8, 4
mov [q], r8


pxor xmm0, xmm0
mov r8, [p]
cvtsi2sd xmm0, rax
movsd xmm1, xmm0
movsd xmm0, [x]
addsd xmm0, xmm1
movsd [kk], xmm0


movsd xmm0, [x]
movsd xmm1, xmm0
movsd xmm0, QWORD [float_7_]
mulsd xmm0, xmm1
movsd [y], xmm0

movsd xmm0, [x]
mov rdi, fmt
mov rsi, r8
xor rax, rax
call printf
pop rbp
ret