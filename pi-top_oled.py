from machine import Pin, SPI, I2C
from neopixel import Neopixel
import framebuf
import time


# =========================
# Pi-Top Hub SPI Brightness
# =========================
class PiTopHubSPI:
    def __init__(self, spi_id=0, sck=2, mosi=3, miso=4, cs=19, baudrate=9600):
        self.cs = Pin(cs, Pin.OUT, value=1)
        self.spi = SPI(
            spi_id,
            baudrate=baudrate,
            polarity=0,
            phase=0,
            bits=8,
            firstbit=SPI.MSB,
            sck=Pin(sck),
            mosi=Pin(mosi),
            miso=Pin(miso),
        )

        self.target_brightness = 7
        self.reported_brightness = 0
        self.lid_open = 0
        self.screen_blanked = 0
        self.shutdown = 0

    def parity_of(self, value):
        p = 0
        while value:
            p ^= (value & 1)
            value >>= 1
        return p

    def build_tx(self):
        b = self.target_brightness
        br_parity = self.parity_of(b)
        state = (self.screen_blanked << 1) | self.shutdown
        state_parity = self.parity_of(state)

        return (
            (br_parity << 7) |
            (b << 3) |
            (state_parity << 2) |
            (self.screen_blanked << 1) |
            self.shutdown
        )

    def transceive(self, tx):
        rx = bytearray(1)
        self.cs.value(0)
        time.sleep_us(10)
        self.spi.write_readinto(bytes([tx]), rx)
        time.sleep_us(10)
        self.cs.value(1)
        return rx[0]

    def sync(self):
        tx = self.build_tx()
        rx = self.transceive(tx)
        self.reported_brightness = (rx >> 3) & 0x0F
        self.lid_open = (rx >> 2) & 0x01
        self.screen_blanked = (rx >> 1) & 0x01
        self.shutdown = rx & 0x01
        return tx, rx

    def set_brightness(self, level):
        if level < 0:
            level = 0
        if level > 10:
            level = 10
        self.target_brightness = level
        return self.sync()

    def brightness_up(self):
        return self.set_brightness(self.target_brightness + 1)

    def brightness_down(self):
        return self.set_brightness(self.target_brightness - 1)


# =================
# Battery Monitor
# =================
class BatteryMonitor:
    BATTERY_ADDR = 0x0B

    def __init__(self, i2c_id=0, scl=21, sda=20, freq=100000):
        self.i2c = I2C(i2c_id, scl=Pin(scl), sda=Pin(sda), freq=freq)

    def read_word(self, register):
        data = self.i2c.readfrom_mem(self.BATTERY_ADDR, register, 2)
        return data[0] | (data[1] << 8)

    def read_signed_word(self, register):
        value = self.read_word(register)
        if value > 32767:
            value -= 65536
        return value

    def get_status(self, current_ma, threshold=50):
        if current_ma > threshold:
            return "Charging"
        elif current_ma < -threshold:
            return "Discharging"
        else:
            return "Idle"

    def read(self):
        percent = self.read_word(0x0D)
        voltage = self.read_word(0x09) / 1000
        current_ma = self.read_signed_word(0x0A)
        temp_k = self.read_word(0x08) / 10
        temp_c = temp_k - 273.15
        status = self.get_status(current_ma)

        return {
            "percent": percent,
            "voltage": voltage,
            "current_ma": current_ma,
            "temp_c": temp_c,
            "status": status,
        }


# ==========================
# Waveshare 2.42" SSD1309
# I2C mode + DC pin on GP14
# ==========================
class OLED_2inch42(framebuf.FrameBuffer):
    def __init__(self, sda=10, scl=11, dc=14, i2c_id=1, addr=0x3C):
        self.width = 128
        self.height = 64
        self.white = 1
        self.black = 0

        self.addr = addr
        self.dc = Pin(dc, Pin.OUT)
        self.dc(0)

        self.i2c = I2C(i2c_id, scl=Pin(scl), sda=Pin(sda), freq=400000)
        self.temp = bytearray(2)

        self.buffer = bytearray(self.height * self.width // 8)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)

        self.init_display()

    def write_cmd(self, cmd):
        self.temp[0] = 0x00
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)

    def write_data(self, buf):
        self.temp[0] = 0x40
        self.temp[1] = buf
        self.i2c.writeto(self.addr, self.temp)

    def init_display(self):
        self.write_cmd(0xAE)
        self.write_cmd(0x00)
        self.write_cmd(0x10)
        self.write_cmd(0x20)
        self.write_cmd(0x00)
        self.write_cmd(0xC8)
        self.write_cmd(0xA6)
        self.write_cmd(0xA8)
        self.write_cmd(0x3F)
        self.write_cmd(0xD3)
        self.write_cmd(0x00)
        self.write_cmd(0xD5)
        self.write_cmd(0x80)
        self.write_cmd(0xD9)
        self.write_cmd(0x22)
        self.write_cmd(0xDA)
        self.write_cmd(0x12)
        self.write_cmd(0xDB)
        self.write_cmd(0x40)
        self.write_cmd(0xA1)
        self.write_cmd(0xAF)

    def show(self):
        for page in range(8):
            self.write_cmd(0xB0 + page)
            self.write_cmd(0x04)
            self.write_cmd(0x00)
            for num in range(128):
                self.write_data(self.buffer[page * 128 + num])


# =================
# Debounced Button
# =================
class DebouncedButton:
    def __init__(self, pin, debounce_ms=40):
        self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.last_state = self.pin.value()
        self.last_change = time.ticks_ms()
        self.debounce_ms = debounce_ms

    def pressed(self):
        now = time.ticks_ms()
        state = self.pin.value()

        if state != self.last_state:
            if time.ticks_diff(now, self.last_change) >= self.debounce_ms:
                self.last_state = state
                self.last_change = now
                if state == 0:
                    return True
        return False


# =================
# Main Setup
# =================
hub = PiTopHubSPI()
battery = BatteryMonitor()
oled = OLED_2inch42(sda=10, scl=11, dc=14, i2c_id=1, addr=0x3C)

# Change these if your first two NeoKey switches are on different GPIOs
btn_down = DebouncedButton(6)
btn_up = DebouncedButton(7)

strip = Neopixel(2, 0, 0, "GRB")


def set_pixel(index, rgb):
    strip.set_pixel(index, rgb)


def update_leds(battery_data):
    # Brightness down key LED
    if hub.target_brightness > 0:
        set_pixel(0, (20, 20, 20))
    else:
        set_pixel(0, (20, 0, 0))

    # Brightness up key LED
    if hub.target_brightness < 10:
        set_pixel(1, (20, 20, 20))
    else:
        set_pixel(1, (0, 20, 0))

    strip.show()


def draw_main_screen(battery_data):
    oled.fill(0)

    oled.text("Battery: {}%".format(battery_data["percent"]), 0, 0, oled.white)
    oled.text("Bright : {}%".format(hub.target_brightness * 10), 0, 16, oled.white)
    oled.text("State  : {}".format(battery_data["status"]), 0, 32, oled.white)
    oled.text("Temp   : {:.1f}C".format(battery_data["temp_c"]), 0, 48, oled.white)

    oled.show()


print("Starting controller...")
time.sleep(2)

hub.sync()
battery_data = battery.read()
update_leds(battery_data)
draw_main_screen(battery_data)

last_spi_sync = time.ticks_ms()
last_battery_poll = time.ticks_ms()
last_screen_refresh = time.ticks_ms()

while True:
    changed = False

    if btn_down.pressed():
        hub.brightness_down()
        changed = True

    if btn_up.pressed():
        hub.brightness_up()
        changed = True

    now = time.ticks_ms()

    if time.ticks_diff(now, last_spi_sync) > 250:
        hub.sync()
        last_spi_sync = now

    if time.ticks_diff(now, last_battery_poll) > 1000:
        battery_data = battery.read()
        last_battery_poll = now
        changed = True

    if changed or time.ticks_diff(now, last_screen_refresh) > 1000:
        update_leds(battery_data)
        draw_main_screen(battery_data)
        last_screen_refresh = now

    time.sleep_ms(20)
