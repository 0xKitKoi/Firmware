import json
import time
from machine import Pin, SPI
from nrf24l01 import NRF24L01

# --- SPI Configuration (Adjust pins for your board) ---
spi = SPI(0, baudrate=4000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
csn = Pin(17, Pin.OUT, value=1)
ce = Pin(14, Pin.OUT, value=0)

# --- Initialize nRF24L01 ---
pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")
nrf = NRF24L01(spi, csn, ce, payload_size=32)
nrf.open_tx_pipe(pipes[1])
nrf.open_rx_pipe(1, pipes[0])  # Listen on the pipeline the transmitter is using
nrf.start_listening()

def receive_long_string(nrf):
    received_chunks = {}
    is_complete = False
    
    while not is_complete:
        if nrf.any():
            packet = nrf.recv()
            sequence_num = packet[0]
            is_last = packet[1]
            data_length = packet[2]
            
            data_content = packet[3:3 + data_length]
            received_chunks[sequence_num] = data_content
            
            if is_last == 1:
                is_complete = True
        else:
            time.sleep_ms(2)
            
    full_byte_stream = b""
    for seq in sorted(received_chunks.keys()):
        full_byte_stream += received_chunks[seq]
        
    try:
        return full_byte_stream.decode('utf-8')
    except UnicodeError:
        return None

# --- Main Loop ---
print("Receiver ready. Waiting for incoming telemetry JSON stream...")

while True:
    # 1. Blocks until a full, sequenced multi-packet string is parsed
    raw_json_str = receive_long_string(nrf)
    
    if raw_json_str:
        try:
            # 2. Parse the string directly back into a usable Python dictionary
            data = json.loads(raw_json_str)
            
            # 3. Read and print your variables directly out of the dictionary
            print("\n=== New Data Packet Received ===")
            print(f"Node Name:  {data['device']}")
            print(f"Reading ID: {data['id']}")
            print(f"Temp / Hum: {data['metrics']['temp_c']}°C / {data['metrics']['humidity']}%")
            print(f"Status Flag:{data['status']}")
            print("================================\n")
            
        except (ValueError, KeyError) as e:
            print("Error parsing incoming string payload as clean JSON structure:", e)
    else:
        print("Dropped transmission due to data corruption.")

