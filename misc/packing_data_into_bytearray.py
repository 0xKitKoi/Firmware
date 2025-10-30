import struct

data_buffer = bytearray(12)  # 3 floats * 4 bytes each = 12 bytes


# Example floats to send
float1 = 0
float2 = 1023/2
float3 = 1023

def normalize(adc_value): # -1 to 1
    #return (adc_value - (1023/2)) / (1023)
    return (adc_value - 0) / (1023 - 0) * 2 - 1


float1 = normalize(float1)
float2 = normalize(float2)
float3 = normalize(float3)
# Use struct to pack the floats into bytes
struct.pack_into('!f', data_buffer, 0, float1)  # Pack float1 into the byte array
struct.pack_into('!f', data_buffer, 4, float2)  # Pack float2 into the byte array
struct.pack_into('!f', data_buffer, 8, float3)  # Pack float3 into the byte array

print(data_buffer)

#while True:
    #if radio.available():
        # Read the received data
#received_data = radio.read(12)  # 12 bytes (3 floats)
        
        # Unpack the bytes back into floats
received_data = data_buffer
float1, = struct.unpack('!f', received_data[:4])
float2, = struct.unpack('!f', received_data[4:8])
float3, = struct.unpack('!f', received_data[8:12])
        
print("Received Floats:", float1, float2, float3)