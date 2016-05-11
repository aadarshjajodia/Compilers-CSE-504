	.text
	.align 4
	.globl main
C_1:
	subu $sp, $sp, 32
	sw $ra, 28($sp)
	sw $fp, 24($sp)
	addu $fp, $sp, 32
	li $t0, 11
	li $t1, 0
	sw $t0, 0($a0)
	lw $ra, 28($sp)
	lw $fp, 24($sp)
	addu $sp, $sp, 32
	jr $ra

M_fun1_7:
	subu $sp, $sp, 32
	sw $ra, 28($sp)
	sw $fp, 24($sp)
	addu $fp, $sp, 32
	li $t0, 0
	lw $t1, 0($a0)
	li $t0, 10
	sub $t1, $t1, $t0
	li $t0, 0
	sw $t1, 0($a0)
	lw $ra, 28($sp)
	lw $fp, 24($sp)
	addu $sp, $sp, 32
	jr $ra

M_fun_8:
	subu $sp, $sp, 32
	sw $ra, 28($sp)
	sw $fp, 24($sp)
	addu $fp, $sp, 32
	li $t0, 2
	mul $t1, $a1, $t0
	li $t0, 0
	lw $t0, 0($a0)
	add $t0, $t1, $t0
	li $t1, 0
	sw $t0, 0($a0)
	sw $a0, 40($sp)
	sw $a1, 36($sp)
	sw $t0, 32($sp)
	sw $t1, 28($sp)
	jal M_fun1_7
	lw $t1, 28($sp)
	lw $t0, 32($sp)
	lw $a1, 36($sp)
	lw $a0, 40($sp)
	move $t0, $v0
	li $t0, 69
	move $v0, $t0
	lw $ra, 28($sp)
	lw $fp, 24($sp)
	addu $sp, $sp, 32
	jr $ra

C_2:
	subu $sp, $sp, 32
	sw $ra, 28($sp)
	sw $fp, 24($sp)
	addu $fp, $sp, 32
	lw $ra, 28($sp)
	lw $fp, 24($sp)
	addu $sp, $sp, 32
	jr $ra

main: # this is my main_entry_point
	li $t0, 1
	mul $t0, $t0, 4
	sw $a0, 20($sp)
	move $a0, $t0
	li $v0, 9
	syscall
	lw $a0, 20($sp)
	move $t0, $v0
	sw $t0, 40($sp)
	move $a0, $t0
	jal C_1
	lw $t0, 40($sp)
	sw $t0, 40($sp)
	move $a0, $t0
	li $t1, 5
	move $a1, $t1
	jal M_fun_8
	lw $t0, 40($sp)
	move $t2, $v0
	li $t1, 0
	la $t1, static_data
	sw $t2, 0($t1)
	li $v0, 10 
	syscall

M_print_3:
	subu $sp, $sp, 32
	sw $ra, 28($sp)
	sw $fp, 24($sp)
	addu $fp, $sp, 32
	lw $ra, 28($sp)
	lw $fp, 24($sp)
	addu $sp, $sp, 32
	jr $ra

M_print_4:
	subu $sp, $sp, 32
	sw $ra, 28($sp)
	sw $fp, 24($sp)
	addu $fp, $sp, 32
	lw $ra, 28($sp)
	lw $fp, 24($sp)
	addu $sp, $sp, 32
	jr $ra

M_print_5:
	subu $sp, $sp, 32
	sw $ra, 28($sp)
	sw $fp, 24($sp)
	addu $fp, $sp, 32
	lw $ra, 28($sp)
	lw $fp, 24($sp)
	addu $sp, $sp, 32
	jr $ra

M_print_6:
	subu $sp, $sp, 32
	sw $ra, 28($sp)
	sw $fp, 24($sp)
	addu $fp, $sp, 32
	lw $ra, 28($sp)
	lw $fp, 24($sp)
	addu $sp, $sp, 32
	jr $ra

M_scan_int_1:
	subu $sp, $sp, 32
	sw $ra, 28($sp)
	sw $fp, 24($sp)
	addu $fp, $sp, 32
	lw $ra, 28($sp)
	lw $fp, 24($sp)
	addu $sp, $sp, 32
	jr $ra

M_scan_float_2:
	subu $sp, $sp, 32
	sw $ra, 28($sp)
	sw $fp, 24($sp)
	addu $fp, $sp, 32
	lw $ra, 28($sp)
	lw $fp, 24($sp)
	addu $sp, $sp, 32
	jr $ra

	.data
static_data: .space 4
