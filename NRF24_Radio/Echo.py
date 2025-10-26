from machine import Pin, SPI
import nrf24l01
from machine import Pin, SPI
from nrf24l01 import NRF24L01
import time
csn = Pin(1, mode=Pin.OUT, value=1)
ce = Pin(5, mode=Pin.OUT, value=0)

spi = SPI(0, baudrate=1_000_000, sck=Pin(2), mosi=Pin(3), miso=Pin(4))
radio = NRF24L01(spi, csn, ce, channel=90, payload_size=32)


print(hex(radio.reg_read(0x00)))  # Should print a nonzero config byte
radio.stop_listening()
radio.flush_tx()        # clear any old garbage

#radio.open_rx_pipe(0, b'node1')   # 5 bytes
#radio.open_tx_pipe(b'node2')      # 5 bytes
pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")
#radio.open_tx_pipe(pipes[0])
#radio.open_rx_pipe(1, pipes[1])
radio.open_tx_pipe(b'\xe1\xf0\xf0\xf0\xf0')   # TX address
radio.open_rx_pipe(1, b'\xd2\xf0\xf0\xf0\xf0') # RX address for echo
radio.start_listening()
ledToggle = True
led = Pin(25, mode=Pin.OUT, value=1)

#for i in range(10):
#    radio.stop_listening()
#    radio.send(b'hello')
#    radio.start_listening()
#    print('sent', i)
#    time.sleep_ms(300)

radio.start_listening()
while True:
    if radio.any():
        led.on(); time.sleep_ms(50); led.off()   # quick flash
        msg = radio.recv()
        print("[+] got something: ")
        print(msg)
        ce.low()
        radio.stop_listening()
        radio.flush_tx()
        try:
            ce.low()
            radio.stop_listening()
            radio.flush_tx()
            radio.send(msg)          # load FIFO  (CE must be LOW here)
            ce.high()                # fire RF
            time.sleep_us(15)
            ce.low()                 # back to standby
            print("echo ok")
        except OSError as e:
            # give detail
            print("echo fail:", e)
        radio.start_listening()
    time.sleep_ms(10)