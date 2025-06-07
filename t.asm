    mov rax, [x]
    add rax, 8
    push rax
    mov rax, [y]
    sub rax, 3
    pop [y]
    add [y], rax