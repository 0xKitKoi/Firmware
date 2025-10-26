from machine import Pin, SPI
import time

# SPI INTERFACE
SCK_PIN  = 2
MOSI_PIN = 3
MISO_PIN = 4
CSN_PIN  = 1
CE_PIN   = 5



spi = SPI(0, baudrate=500_000, polarity=0, phase=0,  # slower speed for reliability
          sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN), miso=Pin(MISO_PIN))
csn = Pin(CSN_PIN, Pin.OUT, value=1)
ce  = Pin(CE_PIN, Pin.OUT, value=0)  # CE must stay LOW during register writes


def spi_transfer(cmd, read_len=1):
    """Send bytes and read response."""
    csn.value(0)
    spi.write(cmd)
    data = spi.read(read_len)
    csn.value(1)
    time.sleep_us(10)  # small delay after CSN high
    return data

def nop_status():
    """Send NOP (0xFF) to read STATUS byte."""
    csn.value(0)
    data = spi.read(1, 0xFF)
    csn.value(1)
    time.sleep_us(10)
    return data

def read_reg(reg):
    """Read a single nRF24 register."""
    R_REGISTER = 0x00
    csn.value(0)
    spi.write(bytes([R_REGISTER | (reg & 0x1F)]))
    val = spi.read(1)[0]
    csn.value(1)
    time.sleep_us(10)
    return val

def write_reg(reg, value):
    """Write a single nRF24 register."""
    W_REGISTER = 0x20
    ce.value(0)  # ensure CE is LOW
    csn.value(0)
    spi.write(bytes([W_REGISTER | (reg & 0x1F), value]))
    csn.value(1)
    time.sleep_us(10)  # small delay for module to catch up


# TESTS:

print("\n=== NRF24L01 Diagnostic Test v2 ===\n")

# 1 SPI Loop Test (NOP)
print("Test 1: NOP command (read STATUS)...")
for i in range(5):
    status = nop_status()
    print(f"  Try {i+1}: STATUS = {status}")
time.sleep(0.2)

# 2 Read CONFIG register
print("\nTest 2: Read CONFIG register...")
val = read_reg(0x00)
print(f"  CONFIG = 0x{val:02X}")

# 3 Write + Read CONFIG register loopback
print("\nTest 3: Write/Read CONFIG register loopback...")
old = val
test_val = 0x0A if old != 0x0A else 0x1E  # choose different test value
write_reg(0x00, test_val)
time.sleep(0.01)
new = read_reg(0x00)
print(f"  Old CONFIG: 0x{old:02X}, Test CONFIG: 0x{test_val:02X}, Read back: 0x{new:02X}")
write_reg(0x00, old)  # restore original
if new == test_val:
    print("  [+] Register write confirmed!")
else:
    print("  [-] Write failed, may need more decoupling or check 3.3V supply.")

# 4 CE Toggle Test
print("\nTest 4: CE toggle test...")
for i in range(3):
    ce.value(1)
    print("  CE HIGH")
    time.sleep(0.2)
    ce.value(0)
    print("  CE LOW")
    time.sleep(0.2)

# 5 SPI Speed Sweep Optional
print("\nTest 5: Optional SPI speed sweep...")
for speed in (100_000, 250_000, 500_000, 1_000_000, 2_000_000):
    spi.init(baudrate=speed)
    status = nop_status()
    print(f"  SPI {speed} Hz, STATUS={status}")

print("\n=== End of diagnostics ===")
print("Tips if write still fails:")
print(" - Ensure CE LOW during writes")
print(" - Add 0.1 µF ceramic capacitor near NRF24 VCC/GND (i have sucess with a 470µF cap")
print(" - Verify 3.3V is stable under load")
print(" - Keep SPI wires short (<10cm)")
