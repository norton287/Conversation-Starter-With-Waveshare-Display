# Press A to reboot the pico back to the main menu
import time
import random
import machine
from machine import Pin,SPI,PWM
import gc
import binascii
import framebuf
import os
import math
from common import LCD_1inch3

BL = 13
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9
    
pwm = PWM(Pin(BL))
pwm.freq(1000)
pwm.duty_u16(32768)#max 65535

keyA = Pin(15,Pin.IN,Pin.PULL_UP)
keyB = Pin(17,Pin.IN,Pin.PULL_UP)
keyX = Pin(19 ,Pin.IN,Pin.PULL_UP)
keyY= Pin(21 ,Pin.IN,Pin.PULL_UP)

up = Pin(2,Pin.IN,Pin.PULL_UP)
down = Pin(18,Pin.IN,Pin.PULL_UP)
left = Pin(16,Pin.IN,Pin.PULL_UP)
right = Pin(20,Pin.IN,Pin.PULL_UP)
ctrl = Pin(3,Pin.IN,Pin.PULL_UP)

WHITE = 255, 255, 255
BLACK = 0, 0, 0
PINK = 214, 28, 78
ORANGE_1 = 247, 126, 33
ORANGE_2 = 250, 194, 19
UN_SELECTED = 80, 80, 100
SELECTED = 128, 132, 32

LCD = LCD_1inch3()

WIDTH = LCD.width
HEIGHT = LCD.height

def color(R,G,B): # Convert RGB888 to RGB565
    return (((G&0b00011100)<<3) +((B&0b11111000)>>3)<<8) + (R&0b11111000)+((G&0b11100000)>>5)

def circle(x,y,r,c):
    LCD.hline(x-r,y,r*2,c)
    for i in range(1,r):
        a = int(math.sqrt(r*r-i*i)) # Pythagoras!
        LCD.hline(x-a,y+i,a*2,c) # Lower half
        LCD.hline(x-a,y-i,a*2,c) # Upper half

# We're creating 100 balls with their own individual colour and 1 BG colour
# for a total of 101 colours, which will all fit in the custom 256 entry palette!
class Ball:
    def __init__(self, x, y, r, dx, dy, RGB):
        self.x = x
        self.y = y
        self.r = r
        self.dx = dx
        self.dy = dy
        self.RGB = RGB  # Store the RGB value

# initialise shapes
balls = []
for i in range(0, 100):
    r = random.randint(0, 10) + 3
    balls.append(
        Ball(
            random.randint(r, r + (WIDTH - 2 * r)),
            random.randint(r, r + (HEIGHT - 2 * r)),
            r,
            (14 - r) / 2,
            (14 - r) / 2,
            (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),  # Pass a tuple as RGB
        )
    )

NBG = 40,40,40

while True:
    if keyA.value() == 0:
        # Perform a soft reset
        machine.soft_reset()

    R,G,B=NBG
    LCD.fill(color(R,G,B))

    for ball in balls:
        ball.x += ball.dx
        ball.y += ball.dy

        xmax = WIDTH - ball.r
        xmin = ball.r
        ymax = HEIGHT - ball.r
        ymin = ball.r

        if ball.x < xmin or ball.x > xmax:
            ball.dx *= -1

        if ball.y < ymin or ball.y > ymax:
            ball.dy *= -1
        L,G,B=ball.RGB
        circle(int(ball.x), int(ball.y), int(ball.r),color(L,G,B))

    LCD.show()  # Update the display only once per loop iteration
    time.sleep(0.01)
