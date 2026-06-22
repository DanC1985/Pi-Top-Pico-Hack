from machine import Pin, SPI
import time

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

        self.brightness = 7
        self.screen_blanked = 0
        self.shutdown = 0

    def parity_of(self, value):
        p = 0
        while value:
            p ^= (value & 1)
            value >>= 1
        return p

    def make_tx(self, brightness=None):
        if brightness is None:
            brightness = self.brightness

        br_parity = self.parity_of(brightness)
        state = (self.screen_blanked << 1) | self.shutdown
        state_parity = self.parity_of(state)

        return (
            (br_parity << 7)
            | (brightness << 3)
            | (state_parity << 2)
            | (self.screen_blanked << 1)
            | self.shutdown
        )

    def transceive(self, tx):
        rx = bytearray(1)
        self.cs.value(0)
        time.sleep_us(10)
        self.spi.write_readinto(bytes([tx]), rx)
        time.sleep_us(10)
        self.cs.value(1)
        return rx[0]

    def decode_rx(self, rx):
        return {
            "raw": rx,
            "bits": "{:08b}".format(rx),
            "parity_bit": (rx >> 7) & 0x01,
            "brightness": (rx >> 3) & 0x0F,
            "lid_open": (rx >> 2) & 0x01,
            "screen_blanked": (rx >> 1) & 0x01,
            "shutdown": rx & 0x01,
        }

hub = PiTopHubSPI()

print("Waiting 5 seconds...")
time.sleep(5)

for level in range(11):
    tx = hub.make_tx(level)
    rx = hub.transceive(tx)
    print("level", level, "TX", hex(tx), "RX", hex(rx), hub.decode_rx(rx))
    time.sleep(1)

