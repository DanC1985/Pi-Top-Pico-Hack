# This is a project to use a Pi-Top V1 laptop with any Raspberry Pi by freeing up the GPIO pins and controlling the Pi-Top Hub via a Raspberry Pi Pico.

<img width="5712" height="4284" alt="IMG_1895" src="https://github.com/user-attachments/assets/17ed4410-2ea0-4fbd-acfb-37dac80cbd45" />

The Pico will be connected to the Hub's GPIO and used to both trick the Hub to turn ON the screen, and to monitor and control the battery + screen contols.

To get these readings I plan to add a OLED display to the Pico to display battery info and screen brightness, and for screen brightness add a few buttons.

Currently for the buttons, I'm using the Adafruit NeoKey Socket Breakout for CHOC key switches, and have found these amazing examples on GitHub to use both the switches and NeoPixels via MicroPython:
https://github.com/blaz-r/pi_pico_neopixel/tree/main
https://github.com/ubidefeo/MicroPython-Button/blob/main/README.md

Orginal code to control the Screen and monitor the Battery came directly from the Pi-Top OS files, also can be found here:
https://www.m0ygh.co.uk/media/chris%20M0YGH/PiTop%20Hub%20Fix.zip

## Background:

So the Pi-Top V1 laptop was “announced in late 2014 and available from early 2015, the original pi-top, with the trackpad to the right-hand side, is to all intents and purposes, pi-top 1”.  This laptop is primarily a lime green plastic laptop shell, powered by, at the time, a Raspberry Pi 2B but would work natively with a 3B, however the original OS that came with this laptop would only first boot on a Pi2.

The Pi connects to the laptop directly to the Pi-Top Hub, that in turn is connected to the screen and battery for the unit.  This box comes with cables to connect either a Pi2 or Pi3 to the Hub with the following cables:
A short HDMI cable (standard HDMI on both sides) - for the display
Micro USB to USB-A cable - for powering the Pi
A custom 40 pin GPIO header to wiring harness - to connect to Pi’s GPIO to the Hub

The Pi-Top will accept and work with a Pi4 but will require changing the cables; I recommend the DIY HDMI cable set from ‘ThePiHub’ for the HDMI as this give nice clearance for the Pi4 when connecting the Micro HDMI and adds uses a flat ribbon cable to connect the two ends that fits nicely under the keyboard - 30cm worked nicely for me.

The issue is this works for the Pi4 but not the Pi5; something to do with the architecture of Pi5; believe this is partly down to the RP1 I/O chip, so won’t work with the Pi-Top.

## Basic Workaround:

By connecting a Raspberry Pi Pico to an adapter like the Red Robotics pico 2 pi adapter and connecting this to the Pi-Top Hub’s GPIO harness and powering the Pico via a USB cable (I simply connected this to the Pi’s USB-A port to daisy chain the power), this tricks the Pi-Top Hub into thinking a valid Pi is connected and thus turns on the display when powering on the laptop.  The down side to this of course is now you’ve lost access to controlling the screen brightness (within Pi-Top OS) or monitoring the battery levels (found on Pi-Top SDK files).
<img width="1200" height="596" alt="image_AAzidKp1q3" src="https://github.com/user-attachments/assets/0f6c7f08-0199-431d-b740-de8a5591a01b" />


## Goal:

To allow for any type of Pi, Single Board Computer or device with a HDMI to connect to the Pi-Top laptop and run any version of OS independent from the Pico and Pi-Top Hub, yet retain all GPIO pins on the Pi/SBC and monitoring/control of the Pi-Top battery & screen brightness.

## Pi’s GPIO pins vs Pico’s GP pins:

The Pi-Top hub connects to the Pi originally via the custom wiring harness, that blocks access to the remaining GPIO pins (useless you get yourself a Pi-Top PROTO board that breaks all GPIO back out again).

For the most part, the Hub is only using these pins to monitor the battery and control the screen brightness:

### I2C1:

GPIO 2 (SDA)

GPIO 3 (SCL)

### SPI0:

GPIO 10 (MOSI)

GPIO 9 (MISO)

GPIO 11 (SCLK)

GPIO 7 (CE)

<img width="501" height="491" alt="Screenshot 2026-06-22 at 17 05 57" src="https://github.com/user-attachments/assets/816149b9-dcf7-4ba6-8271-aec6153c7e62" />

(image from pinout.xyz)

Depending on if you're connection a Pico directly to the harness with wires, PROTO board or using an adaptor like the Red Robotics board that I've been using the GP pins used with need working out.  For the Red Robitics board and all the examples I've provided use the following pins:


## Pi - Pico

GPIO 2 - GP20

GPIO 3 - GP21

GPIO 10 - GP3

GPIO 9 - GP4

GPIO 11 - GP2

GPIO 7 - GP19


Boards like the Hard Stuff Pico to Pi Hat uses the following pinout:
## Pi - Pico

GPIO 2 - GP2

GPIO 3 - GP3

GPIO 10 - GP11

GPIO 9 - GP12

GPIO 11 - GP10

GPIO 7 - GP7

(please check you configuation & pins before connecting a Pico to the Hub).

## Code versions:

All codes were written for using the Pico 2 Pi adaptor from Red Robotics - if using a different adaptor then the GP pins will need changing to match your setup.  if wiring the Pico directly to the Hub I would recommend using the same pins as the examples as this is confirmed to work.

There are a few different scripts for testing your setup and different additions.

Good place to start would be 'battery_i2c' that will report back the battery levels on the Pi-Top and 'pi-top_screen_test.py'; this one is a simple test to see if you wiring is correct between the Pico & the Hub - the script will simply adjust the brightness throught 0% - 100%.

From there, 'pi-top_screen_buttons.py' adds two buttons for cotrolling the Brightness yourself - these are the NeoKey PCB that are used for Brightness Up & Down, plus adds LED feedback via the two NeoPixels on the NeoKey - White on both for normal operations, Red on the Brightness Down when the brightness is set to 0% and Green on the Brightness Up when the brightness is set to 100%.  Please note: You will need to add 'Neopixel.py' from the link above for this script to work.

'pi-top_oled.py' adds a OLED display (Waveshare 2.42" OLED set to I2C).  This too will need the 'neopixel.py' to work.  This screen will need both the i2c pins connected (SDA & SCL), but also the 'DC' pin (quirk of this model of screen).  This example keeps the same two button setup as before, but now includes information on the OLED like Battery level, current screen brightness, dharging status & temperture of the battery.

The final version - 'pi-top_screen_v1.py' is a revised version of the 'pi-top_oled.py' to include 4 NeoKey buttons.
These buttons control the following: 1. Brightness Up, 2. Brightness down, 3. Screen backlight Off / Screen On and 4. Toggling to a second page on the OLED for more status / debugging.

This was a real fun project to work out and get working - here's a nearly finished setup with 4 NeoKeys buttons soldered to a Pi-Top PROTO board, that's then connected to the Hub; just need to find somewhere to mount the screen...

<img width="1024" height="768" alt="134EAFF0-462F-4BEE-9269-F7C2524034C1_1_105_c" src="https://github.com/user-attachments/assets/042e4bd8-3365-4e2b-9e70-14a40ca845fa" />
