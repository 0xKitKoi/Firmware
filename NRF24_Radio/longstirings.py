import time

def send_long_string(nrf, message, payload_size=32):
    """
    Splits any string into 32-byte max packets and sends them sequentially.
    Uses a 2-byte header: [sequence_number, is_last_packet]
    """
    # Convert entire string to bytes
    raw_bytes = message.encode('utf-8')
    
    # 2 bytes are used for header, leaving remaining for text data
    max_chunk_size = payload_size - 2 
    
    # Calculate how many chunks we need
    chunks = [raw_bytes[i:i + max_chunk_size] for i in range(0, len(raw_bytes), max_chunk_size)]
    total_chunks = len(chunks)
    
    nrf.stop_listening()
    
    for idx, chunk in enumerate(chunks):
        sequence_num = idx & 0xFF  # Wraps around 255 if message is massive
        is_last = 1 if (idx == total_chunks - 1) else 0
        
        # Build the packet: Header (2 bytes) + Chunk Data
        header = bytes([sequence_num, is_last])
        packet = header + chunk
        
        # Pad packet to match fixed payload size if dynamic payloads are disabled
        if len(packet) < payload_size:
            packet += b'\x00' * (payload_size - len(packet))
            
        # Retry logic until the chunk successfully transmits
        success = False
        while not success:
            try:
                nrf.send(packet)
                success = True
            except OSError:
                # Target missed or ACK dropped; retry after a short delay
                time.sleep_ms(10)
                
    nrf.start_listening()
    print(f"Successfully sent {total_chunks} packets.")


def receive_long_string(nrf):
    """
    Blocks until a full multi-packet sequential string is received and reconstructed.
    """
    received_chunks = {}
    is_complete = False

    print("Awaiting sequential transmission...")

    while not is_complete:
        if nrf.any():
            # Retrieve the 32-byte raw packet buffer
            packet = nrf.recv()

            # Extract header metadata
            sequence_num = packet[0]
            is_last = packet[1]

            # Extract data content (strip trailing padding null bytes)
            data_content = packet[2:].rstrip(b'\x00')

            # Save the chunk indexed by its sequence position to ensure ordered reconstruction
            received_chunks[sequence_num] = data_content

            # Check if this was signaled as the final packet
            if is_last == 1:
                is_complete = True
        else:
            time.sleep_ms(2) # Prevent pinning the CPU

    # Reassemble chunks sequentially in order of sequence index keys
    full_byte_stream = b""
    for seq in sorted(received_chunks.keys()):
        full_byte_stream += received_chunks[seq]

    try:
        return full_byte_stream.decode('utf-8')
    except UnicodeError:
        return "[Error: Data corruption occurred during packet transmission]"





import time

def send_long_string(nrf, message, payload_size=32):
    """
    Splits any string into packets and sends them sequentially.
    Uses a 3-byte header: [sequence_number, is_last, data_length]
    """
    raw_bytes = message.encode('utf-8')

    # 3 bytes reserved for header metadata
    max_chunk_size = payload_size - 3

    # Split text bytes into chunks
    chunks = [raw_bytes[i:i + max_chunk_size] for i in range(0, len(raw_bytes), max_chunk_size)]
    total_chunks = len(chunks)

    # Handle empty string edge case safely
    if total_chunks == 0:
        chunks = [b""]
        total_chunks = 1

    nrf.stop_listening()

    for idx, chunk in enumerate(chunks):
        sequence_num = idx & 0xFF
        is_last = 1 if (idx == total_chunks - 1) else 0
        chunk_len = len(chunk)

        # Build packet: 3-byte Header + Chunk Data
        header = bytes([sequence_num, is_last, chunk_len])
        packet = header + chunk

        # Pad with null bytes only to satisfy fixed-size hardware requirements
        if len(packet) < payload_size:
            packet += b'\x00' * (payload_size - len(packet))

        # Retry mechanism for reliable delivery
        success = False
        while not success:
            try:
                nrf.send(packet)
                success = True
            except OSError:
                time.sleep_ms(10)  # Short delay before re-attempting dropped ACK

    nrf.start_listening()




import time

def receive_long_string(nrf):
    """
    Blocks until a full sequential transmission is completed,
    reconstructing the string using exact byte lengths.
    """
    received_chunks = {}
    is_complete = False

    while not is_complete:
        if nrf.any():
            packet = nrf.recv()

            # Unpack the 3-byte header
            sequence_num = packet[0]
            is_last = packet[1]
            data_length = packet[2]

            # Slice EXACTLY the number of payload bytes transmitted, ignoring padding
            data_content = packet[3:3 + data_length]

            # Save chunk indexed by sequence to guarantee sorted order
            received_chunks[sequence_num] = data_content

            if is_last == 1:
                is_complete = True
        else:
            time.sleep_ms(2)  # Yield CPU focus

    # Assemble chunks sequentially
    full_byte_stream = b""
    for seq in sorted(received_chunks.keys()):
        full_byte_stream += received_chunks[seq]

    try:
        return full_byte_stream.decode('utf-8')
    except UnicodeError:
        return "[Error: Packet corruption detected during stream parsing]"

