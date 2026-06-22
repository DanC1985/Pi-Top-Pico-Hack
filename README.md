This is a project to use a Pi-Top V1 laptop with any Raspberry Pi by freeing up the GPIO pins and controlling the Pi-Top Hub via a Raspberry Pi Pico.

<img width="5712" height="4284" alt="IMG_1895" src="https://github.com/user-attachments/assets/17ed4410-2ea0-4fbd-acfb-37dac80cbd45" />

The Pico will be connected to the Hub's GPIO and used to both trick the Hub to turn ON the screen, and to monitor and control the battery + screen contols.

To get these readings I plan to add a OLED display to the Pico to display battery info and screen brightness, and for screen brightness add a few buttons.

Current for the buttons, I'm using the Adafruit NEoKey Socket Breakout for CHOC key switches, and have found these amazing examples on GitHub to use both the switches and NeoPixels via MicroPython:
https://github.com/blaz-r/pi_pico_neopixel/tree/main
https://github.com/ubidefeo/MicroPython-Button/blob/main/README.md

Orginal code to control the Screen and monitor the Battery came directly from the Pi-Top OS files, also can be found here:
https://www.m0ygh.co.uk/media/chris%20M0YGH/PiTop%20Hub%20Fix.zip
