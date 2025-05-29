MOV R1, 5          ; R1 = 5
MOV R2, 10         ; R2 = 10
ADD R1, R2         ; R1 = 15
SUB R1, R2         ; R1 = 5
MUL R1, R2         ; R1 = 50
DIV R1, R2         ; R1 = 5

PUSH R1            ; Push 5 to stack
MOV R3, POP        ; Pop to R3 => R3 = 5

MOV A1, 100        ; A1 points to mem[100]
MOV I1, 2          ; I1 index = 2
MOV 102, 42        ; store 42 at mem[100+2]
MOV R4, #2         ; Indexed: R4 = mem[A1 + I1] => 42

MOV R5, 5
MOV R6, 5
JEQ 20, R5, R6     ; If R5 == R6, jump to line 20
MOV R7, 0          ; Will be skipped if JEQ is true
JMP 21             ; Skip next MOV
MOV R7, 1          ; Will execute only if jump didn't happen

EOP                ; End of Program
