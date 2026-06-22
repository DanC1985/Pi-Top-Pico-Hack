from machine import I2C, Pin
import time

i2c = I2C(0, scl=Pin(21), sda=Pin(20), freq=100000)

BATTERY_ADDR = 0x0B

def read_word(register):
    data = i2c.readfrom_mem(BATTERY_ADDR, register, 2)
    return data[0] | (data[1] << 8)

def read_signed_word(register):
    value = read_word(register)
    if value > 32767:
        value -= 65536
    return value

def get_charge_status(current_ma, threshold=50):
    # Small deadband avoids flickering between charging/discharging
    if current_ma > threshold:
        return "Charging"
    elif current_ma < -threshold:
        return "Discharging"
    else:
        return "Idle"

while True:
    percent = read_word(0x0D)
    voltage = read_word(0x09) / 1000
    current_ma = read_signed_word(0x0A)
    temp_k = read_word(0x08) / 10
    temp_c = temp_k - 273.15

    status = get_charge_status(current_ma)

    print("--------------------")
    print(f"Battery : {percent}%")
    print(f"Voltage : {voltage:.2f}V")
    print(f"Current : {current_ma}mA")
    print(f"Temp    : {temp_c:.1f}C")
    print(f"Status  : {status}")

    time.sleep(5)

