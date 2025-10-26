import socket
from machine import Pin, PWM
import utime

# Configuration
SERVER_IP = "192.168.0.222"
SERVER_PORT = 5000
WIFI_SSID = "BSSID NAME"
WIFI_PASSWORD = "PASSWORD"

X_SERVO_PIN = 16
Y_SERVO_PIN = 17

# Create servo objects
x_servo = PWM(Pin(X_SERVO_PIN))
y_servo = PWM(Pin(Y_SERVO_PIN))

# Function to move servo to a specific angle
#def move_servo(servo, angle):
#    # Calculate pulse width based on angle
#    pulse_width = int((angle / 180) * (2500 - 500) + 500)
#    servo.duty_ns(pulse_width * 1000)

def moveServo(command):
    # Split the command into components based on 'X' and 'Y'
    components = command.split('X')[1:]
    
    # Iterate over the components
    for component in components:
        # Split each component into 'X' and 'Y' values
        values = component.split('Y')
        
        # Extract the X and Y values
        x_value = int(values[0])
        y_value = int(values[1])
        
        # Map the X and Y values to servo angles (assuming a certain range)
        x_angle = mapValue(x_value, 0, 1023, 0, 180)
        y_angle = mapValue(y_value, 0, 1023, 0, 180)
        
        print(f"X Angle: {x_angle}, Y Angle: {y_angle}")
        
        # Move the servos to the calculated angles
        #x_servo.duty_u16(mapValue(x_angle, 0, 180, x_servo_range[0], x_servo_range[1]))
        #y_servo.duty_u16(mapValue(y_angle, 0, 180, y_servo_range[0], y_servo_range[1]))
        x_servo.duty_u16(mapValue(x_angle, 0, 180, 1200, 8600))
        y_servo.duty_u16(mapValue(y_angle, 0, 180, 1200, 8600))


def test():
    x_servo.duty_u16(500)
    utime.sleep_ms(500)
    x_servo.duty_u16(1500)
    utime.sleep_ms(500)
    x_servo.duty_u16(2400)
    utime.sleep_ms(500)
    x_servo.duty_u16(500)
    utime.sleep_ms(500)
    x_servo.duty_u16(1500)
    utime.sleep_ms(500)
    x_servo.duty_u16(2400)
    utime.sleep_ms(500)




def mapValue(value, from_low, from_high, to_low, to_high):
    #return int(to_low + (value - from_low) * (to_high - to_low) / (from_high - from_low)) # didnt seem to work for me
    return int(value + ((8600 - 1200)/2))

def connect_to_wifi():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print("Connecting to Wi-Fi...")
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while (not wlan.isconnected()):
        # Sometimes disconnecting frequently leaves ARP table errors.
        # really confuses the router when a device has power issues, so retrying a lot is neceissary. 
        utime.sleep(1)
        print("Connected to Wi-Fi.")


def handle_servo_command(command):
    if command.to_low().startswith("test"):
        test()
    if command.startswith("X"):
        x_angle = int(command[1:])
        move_servo(x_servo, x_angle)
        print(f"Moved X servo to {x_angle} degrees.")
    elif command.startswith("Y"):
        y_angle = int(command[1:])
        move_servo(y_servo, y_angle)
        print(f"Moved Y servo to {y_angle} degrees.")


def create_and_connect_socket():
    
    connect_to_wifi()

    server_address = (SERVER_IP, SERVER_PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    return sock


def main():
    print("Initializing.\n")
    x_servo.freq(50)
    y_servo.freq(50)

    test()
    sock = create_and_connect_socket()

    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break  # Connection closed by the server

            command = data.decode("utf-8").strip()

            #handle_servo_command(command)
            moveServo(command)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
