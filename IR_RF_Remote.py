 # ECEN 2360 Project 2A: Stop Watch
 # Kevin Huang

.section .reset, "ax" 		#0x00000000
.global _start
.equ UART_DATA, 	0x1000
.equ UART_CTRL, 	0x1004
.equ SEG_DISPLAY_LO, 	0x20
.equ SEG_DISPLAY_HI, 	0x30
.equ BUTTON_DATA, 	0x50
.equ BUTTON_MASK, 	0x58
.equ BUTTON_CAPTURE, 	0x5C

_start:
	movia 	sp, 0x01000000 # 16MB stack
	movia 	gp, 0xff200000 # MMIO base address
	br 		main
	
.section .exceptions, "ax" # 0x00000020

# main() - Stop Watch main program
# Parameters: none
# Return: none
main:
	
	# Initialize values - stop watch value and state
	mov 	r16, r0 # Stop watch initial value
	mov 	r17, r0 #  boolean value, 1 if watch is stopped, 0 if it is running
	mov 	r18, r0 # Time continues to increase but display is stopped
	
	mov 	r19, r0 # Button 0 press state - 1 if pressed, 0 if not
	mov 	r20, r0 # Button 1 press state
	
	# initial time
	mov 	r4, r0
	call 	displayTime
  main_loop:
	
	movia 	r4, 1
	call 	delayNms 
	
	
	ldwio 	r2, BUTTON_DATA(gp) # Load current data for button
	
	# Check if button 0 is used
	andi 	r3, r2, 0b1
	bne 	r3, r0, process_button0_press # If button is currently pressed, branch
	br 		process_button0_release	 # depressed? 
	
  # if it is currently pressed down
  process_button0_press:
	movi 	r19, 1
	br 		end_button_press0

  process_button0_release	:
	bne 	r19, r0, toggle_stopwatch
	br 		end_button_press0
	
  # Toggle start/start for the watch
  toggle_stopwatch:
  	mov 	r19, r0
	bne 	r17, r0, start_watch
	br 		stop_watch
	
  start_watch:
  	mov 	r17, r0
	br 		end_button_press0
	
  stop_watch:
  	movi 	r17, 1
	br 		end_button_press0
  
  end_button_press0: 
  
  	# Check if button 1 (to reset) button is used
  	andi 	r3, r2, 0b10
	bne 	r3, r0, process_button1_press
	br 		process_button1_release	
  

  process_button1_press:
	movi 	r20, 1
	br 		end_button_press1

  
  process_button1_release	:
	bne 	r20, r0, toggle_freeze_or_reset
	br 		end_button_press1
	
  toggle_freeze_or_reset:
  	mov 	r20, r0
	bne 	r17, r0, reset_stopwatch # If watch is stopped, reset it
	bne 	r18, r0, resume_display
	br 		pause_display
	
  pause_display:
  	movi 	r18, 1
	br 		end_button_press1
    
  resume_display:
 	mov 	r18, r0
	br 		end_button_press1
	
  # Reset watch time to 00:00:00 and show updated time
  reset_stopwatch:
  	mov 	r16, r0
	mov 	r4, r16
  	call 	displayTime
	
  end_button_press1:
  
	
	# If watch is stopped, restart loop - skip time incrementation
	bne 	r17, r0, main_loop 
	
	addi 	r16, r16, 1
	
	bne 	r18, r0, main_loop # If watch is frozen, restart loop after time is incremented, 
							   # don't display updated time
	
	# beq frozen, 1, increment (doesn't display updated time, still increment time)
  	mov 	r4, r16
  	call 	displayTime
	
	br 		main_loop
	
# -- display time on the stop watch --
# -- convert from total centiseconds ellapsed (n) to minutes, seconds, centiseconds --

displayTime:
	# r4 contains number of centiseconds that have elapsed
	
	# Prologue
	subi 	sp, sp, 8
	stw 	ra, 4(sp)
    # Store total centiseconds
	stw 	r4, 0(sp) 
	
	# Display minutes elapsed
    # Divisor to obtain total number of minutes elapsed
	movia 	r5, 6000 
	div 	r4, r4, r5
	call 	display_minutes
	
	ldw 	r4, 0(sp) # restore centiseconds
	movia 	r5, 6000  # restore divisor values 
	mov 	r3, r0	  # resetting r3
	
	# Get time that has passed using modulus implementation
  	div 	r3, r4, r5  # r3 = r4 / 6000
	mul 	r3, r3, r5	# r3 = r3 * 6000
	sub 	r4, r4, r3   # r4 = r4 % 6000
	
	call 	display_seconds_and_centi
	
	ldw 	ra, 4(sp)
	addi 	sp, sp, 8
	
	ret
	
# -- display n on 7 segment display --
# -- Only affects segments 5-6 - minutes --

display_minutes:

	subi 	sp, sp, 4
	stw 	ra, 0(sp)

	call 	num2bits
	ori 	r2, r2, 0x80 
	
	# Display r4 value on 7 segment
	stwio 	r2, SEG_DISPLAY_HI(gp) 
	
	ldw 	ra, 0(sp)
	addi 	sp, sp, 4
	ret

# -- display n on 7 segment display --
# -- Only affects segments 1-4 - seconds and centiseconds --
display_seconds_and_centi:
	# Prologue
	subi 	sp, sp, 4
	stw 	ra, 0(sp)

	call 	num2bits 
    # Display decimal point after seconds
	orhi 	r2, r2, 0x80 
	
	stwio 	r2, SEG_DISPLAY_LO(gp) 	# Display r4 value on 7 segment

	
	ldw 	ra, 0(sp)
	addi 	sp, sp, 4
	ret

# convert from integer value n to binary 
#  sequence ofbits which can be displayed 

num2bits:
	# Preload necessary values
	movi 	r2, 0
	movi 	r10, 10
	movi 	r7, 4 
	
  # Loop until r7 == 0
  n2b_loop:
  # modulus 
	div 	r3, r4, r10
	mul 	r5, r3, r10
	sub		r5, r4, r5		# r5 = r4 % r5
	
	# Convert r4 integer value into binary representation for segment display
	ldbu 	r6, Bits7Seg(r5)
	or 		r2, r2, r6
    # Bit shift to reverse order of binary value
	roli 	r2, r2, 24 
	mov 	r4, r3
	subi 	r7, r7, 1
	bgt		r7, r0, n2b_loop
	
	ret
	
# void delayNms(int n) -- Delay N milliseconds
# Parameter: int n Number of milliseconds to delay
delayNms:
	movia 	r2, 33332 # Divide clock by 33332 * 3 ~ 100,000 cycles
	mul 	r2, r2, r4 # Multiply by n to obtain total millisecond delay
  delay_loop:
  	subi 	r2, r2, 1 # 1 clock cycle
	bne 	r2, r0, delay_loop # 2 clock cycles
	ret
	

# delay of 10ms
delay10ms:
	subi 	sp, sp, 4
	stw 	ra, 0(sp)
	
	movia 	r4, 10
	
	call 	delayNms
	
	ldw 	ra, 0(sp)
	addi 	sp, sp, 4
	
	ret
	

printNum:
	subi 	sp, sp, 8
	stw 	ra, 4(sp)
	
	bge 	r4, r0, not_neg
    # Make r4 negative
	sub 	r4, r0, r4 
	stw 	r4, 0(sp)
	movi 	r4, '-'
    # Print '-' character
	call 	putchar 
	ldw 	r4, 0(sp)
	
  not_neg:
	# Check if last character has been reached
  	movi 	r10, 10
	bge 	r4, r10, not_base
	addi 	r4, r4, '0'
	call 	putchar
	br 	printNum_done

  not_base:
  	# Modulus implementation
  	movi 	r10, 10
  	div 	r3, r4, r10  # r3 = r4 / 10
	mul 	r5, r3, r10
	sub 	r5, r4, r5   # r5 = r4 % 10
	
	stw 	r5, 0(sp)
	mov		r4, r3
	call	printNum	 # printNum(n / 10)
	ldw 	r5, 0(sp)
	addi 	r4, r5, '0'
	call 	putchar 		# putchar ('0' + n % 10)
  
  printNum_done:
  	# Epilogue
	ldw		ra, 4(sp)
	addi 	sp, sp, 8
	ret
	

# void putchar(char c) - Write char to UART
putchar:
	ldwio 	r2, UART_CTRL(gp) # Loading the data from UART control register
	srli 	r2, r2, 16 # Loading the upper 16 bits 
	beq 	r2, r0, putchar # Looping - no space to write
	stwio 	r4, UART_DATA(gp) # Write data
	
	ret
	
	
	
.data

Bits7Seg:
	.byte  0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6f

.end