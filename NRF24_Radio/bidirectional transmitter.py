from machine import Pin, SPI, UART
from nrf24l01 import NRF24L01
import time
from machine import Pin
led = Pin(25, Pin.OUT)


spi  = SPI(0, sck=Pin(2), mosi=Pin(3), miso=Pin(0))
csn = Pin(5, mode=Pin.OUT, value=1)
ce = Pin(4, mode=Pin.OUT, value=0)
radio = NRF24L01(spi, csn, ce, channel=90, payload_size=32)

radio.open_tx_pipe(b'\xd2\xf0\xf0\xf0\xf0')   # TX address
radio.open_rx_pipe(1, b'\xe1\xf0\xf0\xf0\xf0') # RX address for echo
uart = UART(0, 115200)

cnt = 0
while True:
    for _ in range(3):
        led(1); time.sleep_ms(100); led(0); time.sleep_ms(100)
    msg = b'test%03d' % cnt
    radio.stop_listening()
    try:
        radio.send(msg)
        print('TX ok  ', end='')
    except OSError:
        print('TX to', end='')
    #sys.stdout.flush()          # force USB serial to emit now
    radio.start_listening()

    if radio.any():
        echo = radio.recv()
        print(' RX:', echo.rstrip(b'\0'), end='')
        #sys.stdout.flush()

    print()                     # final newline
    cnt += 1
    time.sleep(2)