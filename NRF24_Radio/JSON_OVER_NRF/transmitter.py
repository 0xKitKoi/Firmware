import json
import time
from machine import Pin, SPI
from nrf24l01 import NRF24L01

# --- SPI Configuration (Adjust pins for your board) ---
# Example for Raspberry Pi Pico: SPI(0), SCK=18, MOSI=19, MISO=16
spi = SPI(0, baudrate=4000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
csn = Pin(17, Pin.OUT, value=1)
ce = Pin(14, Pin.OUT, value=0)

# --- Initialize nRF24L01 ---
pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")
nrf = NRF24L01(spi, csn, ce, payload_size=32)
nrf.open_tx_pipe(pipes[0])  # Use pipe 0 for sending
nrf.open_rx_pipe(1, pipes[1])

def send_long_string(nrf, message, payload_size=32):
    raw_bytes = message.encode('utf-8')
    max_chunk_size = payload_size - 3 
    chunks = [raw_bytes[i:i + max_chunk_size] for i in range(0, len(raw_bytes), max_chunk_size)]
    total_chunks = len(chunks)
    
    if total_chunks == 0:
        chunks = [b""]
        total_chunks = 1
        
    nrf.stop_listening()
    for idx, chunk in enumerate(chunks):
        sequence_num = idx & 0xFF
        is_last = 1 if (idx == total_chunks - 1) else 0
        chunk_len = len(chunk)
        
        packet = bytes([sequence_num, is_last, chunk_len]) + chunk
        if len(packet) < payload_size:
            packet += b'\x00' * (payload_size - len(packet))
            
        success = False
        while not success:
            try:
                nrf.send(packet)
                success = True
            except OSError:
                time.sleep_ms(10)
    nrf.start_listening()

# --- Main Loop ---
reading_id = 0

while True:
    reading_id += 1
    
    # 1. Build your structured data
    sensor_data = {
        "id": reading_id,
        "device": "Weather Station Node 01",
        "timestamp": time.time(),
        "metrics": {
            "temp_c": 23.5,
            "humidity": 45.2,
            "pressure_hpa": 1013.25
        },
        "status": "OPERATIONAL_NORMAL"
    }
    
    # 2. Serialize dictionary to a JSON string
    json_string = json.dumps(sensor_data)
    
    print(f"Sending JSON payload (Length: {len(json_string)} chars)...")
    
    # 3. Transmit using the multi-packet sequencer
    send_long_string(nrf, json_string)
    
    print("Sent successfully. Waiting 5 seconds...")
    time.sleep(5)

