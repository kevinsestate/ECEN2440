import machine, ir_rx, time
from machine import Pin
from ir_rx.nec import NEC_8 # Use the NEC 8-bit class
from ir_rx.print_error import print_error # for debugging

# Define the RF Receiver pins with normal state '0' or 'Low'
RF_D0 = Pin(7, Pin.IN, Pin.PULL_DOWN)
RF_D1 = Pin(6, Pin.IN, Pin.PULL_DOWN)
RF_D2 = Pin(5, Pin.IN, Pin.PULL_DOWN)
RF_D3 = Pin(4, Pin.IN, Pin.PULL_DOWN)

# Define LED Pins
LED0 = Pin(22, Pin.OUT, Pin.PULL_DOWN)
LED1 = Pin(20, Pin.OUT, Pin.PULL_DOWN)
LED2 = Pin(18, Pin.OUT, Pin.PULL_DOWN)
LED3 = Pin(16, Pin.OUT, Pin.PULL_DOWN)


# Function to turn off all LEDs
def turn_off_leds():
    LED0.value(0)
    LED1.value(0)
    LED2.value(0)
    LED3.value(0)


# Interrupt functions
def d0_interrupt(pin):
    RF_D0.irq(handler=None)  # Temporarily disable interrupt
    turn_off_leds()
    print("D0 Received")
    LED0.value(1)
    time.sleep_ms(200)  # Debounce delay
    RF_D0.irq(handler=d0_interrupt)  # Re-enable interrupt

def d1_interrupt(pin):
    RF_D1.irq(handler=None)  # Temporarily disable interrupt
    turn_off_leds()
    print("D1 Received")
    LED1.value(1)
    time.sleep_ms(200)  # Debounce delay
    RF_D1.irq(handler=d1_interrupt)  # Re-enable interrupt

def d2_interrupt(pin):
    RF_D2.irq(handler=None)  # Temporarily disable interrupt
    turn_off_leds()
    print("D2 Received")
    LED2.value(1)
    time.sleep_ms(200)  # Debounce delay
    RF_D2.irq(handler=d2_interrupt)  # Re-enable interrupt

def d3_interrupt(pin):
    RF_D3.irq(handler=None)  # Temporarily disable interrupt
    turn_off_leds()
    print("D3 Received")
    LED3.value(1)
    time.sleep_ms(200)  # Debounce delay
    RF_D3.irq(handler=d3_interrupt)  # Re-enable interrupt


# Attach interrupt handlers to each pin, triggering on falling edge 
RF_D0.irq(trigger=Pin.IRQ_FALLING, handler=d0_interrupt)
RF_D1.irq(trigger=Pin.IRQ_FALLING, handler=d1_interrupt)
RF_D2.irq(trigger=Pin.IRQ_FALLING, handler=d2_interrupt)
RF_D3.irq(trigger=Pin.IRQ_FALLING, handler=d3_interrupt)

# Callback function to execute when an IR code is received
def ir_callback(data, addr, _):
    print(f"Received NEC command! Data: 0x{data:02X}, Addr: 0x{addr:02X}") 
    if data == 0x01:
        turn_off_leds()
        LED0.value(1)
    elif data == 0x02:
        turn_off_leds()
        LED1.value(1)
    elif data == 0x03:
        turn_off_leds()
        LED2.value(1)
    elif data == 0x04:
        turn_off_leds()
        LED3.value(1)
        time.sleep_ms(500)
        LED3.value(0)   # Turn off LED connected to pin 0

        
    
# Setup the IR receiver
ir_pin = Pin(26, Pin.IN, Pin.PULL_UP) # Adjust the pin number based on your wiring
ir_receiver = NEC_8(ir_pin, callback=ir_callback)

# Optional: Use the print_error function for debugging
ir_receiver.error_function(print_error)
    
    
# Main function of the program
while True:
    # Sleep to not overload CPU
    time.sleep_ms(100)
    