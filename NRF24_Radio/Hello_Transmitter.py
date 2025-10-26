# transmitter Pico (USB)
from machine import Pin, SPI
from nrf24l01 import NRF24L01
import time
led = Pin(25, Pin.OUT)


spi  = SPI(0, sck=Pin(2), mosi=Pin(3), miso=Pin(0))
csn = Pin(5, mode=Pin.OUT, value=1)
ce = Pin(4, mode=Pin.OUT, value=0)

radio = NRF24L01(spi, csn, ce, channel=90, payload_size=32)

#pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")
#radio.open_rx_pipe(0, pipes[1])   # listen on TX-address
#radio.open_tx_pipe(pipes[0])      # reply on RX-address

# This is on the Battery Powered Pico. We swap these addresses.
#radio.open_tx_pipe(b'\xe1\xf0\xf0\xf0\xf0')   # TX address
#radio.open_rx_pipe(1, b'\xd2\xf0\xf0\xf0\xf0') # RX address for echo
radio.open_tx_pipe(b'\xd2\xf0\xf0\xf0\xf0')   # TX address 
radio.open_rx_pipe(1, b'\xe1\xf0\xf0\xf0\xf0') # RX address for echo

cnt = 0
while True:
    for _ in range(3): # flash led so i know its working
        led(1); time.sleep_ms(100); led(0); time.sleep_ms(100)
        
    ce(0)                      # CE low during write
    radio.stop_listening() # gotta stop_listening() to send data
    try:
        radio.send(b'hello')
        print('[+] Sent hello! Packet number: ', cnt)
    except OSError:
        print('[-] Packet was not Acked! Packet Number: ', cnt)
    radio.start_listening()
    cnt += 1
    time.sleep_ms(200)         # 5 packets per second
