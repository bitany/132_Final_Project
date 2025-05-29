MOV R1, 5          ; R1 = 5
MOV R2, 10         ; R2 = 10
ADD R1, R2         ; R1 = 15
SUB R1, R2         ; R1 = 5
MUL R1, R2         ; R1 = 50
DIV R1, R2         ; R1 = 5

PUSH R1            ; Push 5 to stack
MOV R3, POP        ; Pop to R3 => R3 = 5

MOV A1, 100        ; A1 points to mem[100]
MOV I1, 2          ; I1 = 2
MOV 102, 42        ; Store 42 at mem[102]
MOV R4, #2         ; R4 = mem[A1 + I1] => 42

MOV R5, 5
MOV R6, 5
JEQ 24, R5, R6     ; If equal, jump to MOV R7, 1
MOV R7, 0          ; Will be skipped if JEQ is true
JMP 25             ; Skip next MOV
MOV R7, 1          ; Will execute only if jump didn't happen

MOV R8, 200        ; Store to memory[200]
MOV 200, 99        ; Direct write
MOV R9, *200       ; Indirect: R9 = mem[mem[200]] = mem[99] (if 200 = 99)

MOV R10, 0         ; R10 = 0
MOV SPR, 120       ; Set stack pointer
MOV TSP, 120       ; Top of stack pointer
MOV R11, 888       ; Test value

PUSH R11           ; Push to stack
MOV R12, POP       ; Pop into R12 => 888

MOV R13, 4
MOV R14, 0
ADD R14, R13       ; R14 = 4
AUTODEC R14        ; Dec R14 (use as address), load from it

MOV R15, 3
AUTOINC R15        ; Use R15 as address, load from it, then inc R15

CALL FUNC          ; Call function (PC pushed)
MOV R0, 123        ; Will execute after return
EOP                ; End of program

FUNC:
MOV R0, 321        ; Set R0
RET                ; Return (pop PC)
