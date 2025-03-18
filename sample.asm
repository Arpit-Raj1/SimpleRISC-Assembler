
    start:mov r1, 10 
    mov r2, 20 
    add r3, r1, r2
    sub r4, r3, 5
    mul r5, r4, 2 
    div r6, r5, 4
    mod r7, r6, 3 
    cmp r7, 1
    beq equal
    bgt greater
    b end


    equal:mov r8, 1 
    b end

    greater:mov r8, 2 
    b end


    end:hlt 