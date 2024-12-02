# PicoPong
import time
import random
from machine import Pin,SPI,PWM
import machine
import gc
import binascii
import framebuf
import os
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

LCD = LCD_1inch3()
#color BRG
LCD.fill(LCD.white)
LCD.show()

gc.collect()

keyA = Pin(15,Pin.IN,Pin.PULL_UP)
keyB = Pin(17,Pin.IN,Pin.PULL_UP)
keyX = Pin(19 ,Pin.IN,Pin.PULL_UP)
keyY = Pin(21 ,Pin.IN,Pin.PULL_UP)

up = Pin(2,Pin.IN,Pin.PULL_UP)
down = Pin(18,Pin.IN,Pin.PULL_UP)
left = Pin(16,Pin.IN,Pin.PULL_UP)
right = Pin(20,Pin.IN,Pin.PULL_UP)
ctrl = Pin(3,Pin.IN,Pin.PULL_UP)

SCREEN_WIDTH = LCD.width
SCREEN_HEIGHT = LCD.height

# ASCII Character Set Array (Font)
cmap = ['00000000000000000000000000000000000', #Space
        '00100001000010000100001000000000100', #!
        '01010010100000000000000000000000000', #"
        '01010010101101100000110110101001010', ##
        '00100011111000001110000011111000100', #$
        '11001110010001000100010001001110011', #%
        '01000101001010001000101011001001101', #&
        '10000100001000000000000000000000000', #'
        '00100010001000010000100000100000100', #(
        '00100000100000100001000010001000100', #)
        '00000001001010101110101010010000000', #*
        '00000001000010011111001000010000000', #+
        '000000000000000000000000000000110000100010000', #,
        '00000000000000011111000000000000000', #-
        '00000000000000000000000001100011000', #.
        '00001000010001000100010001000010000', #/
        '01110100011000110101100011000101110', #0
        '00100011000010000100001000010001110', #1
        '01110100010000101110100001000011111', #2
        '01110100010000101110000011000101110', #3
        '00010001100101011111000100001000010', #4
        '11111100001111000001000011000101110', #5
        '01110100001000011110100011000101110', #6
        '11111000010001000100010001000010000', #7
        '01110100011000101110100011000101110', #8
        '01110100011000101111000010000101110', #9
        '00000011000110000000011000110000000', #:
        '01100011000000001100011000010001000', #;
        '00010001000100010000010000010000010', #<
        '00000000001111100000111110000000000', #=
        '01000001000001000001000100010001000', #>
        '01100100100001000100001000000000100', #?
        '01110100010000101101101011010101110', #@
        '00100010101000110001111111000110001', #A
        '11110010010100111110010010100111110', #B
        '01110100011000010000100001000101110', #C
        '11110010010100101001010010100111110', #D
        '11111100001000011100100001000011111', #E
        '11111100001000011100100001000010000', #F
        '01110100011000010111100011000101110', #G
        '10001100011000111111100011000110001', #H
        '01110001000010000100001000010001110', #I
        '00111000100001000010000101001001100', #J
        '10001100101010011000101001001010001', #K
        '10000100001000010000100001000011111', #L
        '10001110111010110101100011000110001', #M
        '10001110011010110011100011000110001', #N
        '01110100011000110001100011000101110', #O
        '11110100011000111110100001000010000', #P
        '01110100011000110001101011001001101', #Q
        '11110100011000111110101001001010001', #R
        '01110100011000001110000011000101110', #S
        '11111001000010000100001000010000100', #T
        '10001100011000110001100011000101110', #U
        '10001100011000101010010100010000100', #V
        '10001100011000110101101011101110001', #W
        '10001100010101000100010101000110001', #X
        '10001100010101000100001000010000100', #Y
        '11111000010001000100010001000011111', #Z
        '01110010000100001000010000100001110', #[
        '10000100000100000100000100000100001', #\
        '00111000010000100001000010000100111', #]
        '00100010101000100000000000000000000', #^
        '00000000000000000000000000000011111', #_
        '11000110001000001000000000000000000', #`
        '00000000000111000001011111000101110', #a
        '10000100001011011001100011100110110', #b
        '00000000000011101000010000100000111', #c
        '00001000010110110011100011001101101', #d
        '00000000000111010001111111000001110', #e
        '00110010010100011110010000100001000', #f
        '000000000001110100011000110001011110000101110', #g
        '10000100001011011001100011000110001', #h
        '00100000000110000100001000010001110', #i
        '0001000000001100001000010000101001001100', #j
        '10000100001001010100110001010010010', #k
        '01100001000010000100001000010001110', #l
        '00000000001101010101101011010110101', #m
        '00000000001011011001100011000110001', #n
        '00000000000111010001100011000101110', #o
        '000000000001110100011000110001111101000010000', #p
        '000000000001110100011000110001011110000100001', #q
        '00000000001011011001100001000010000', #r
        '00000000000111110000011100000111110', #s
        '00100001000111100100001000010000111', #t
        '00000000001000110001100011001101101', #u
        '00000000001000110001100010101000100', #v
        '00000000001000110001101011010101010', #w
        '00000000001000101010001000101010001', #x
        '000000000010001100011000110001011110000101110', #y
        '00000000001111100010001000100011111', #z
        '00010001000010001000001000010000010', #{
        '00100001000010000000001000010000100', #|
        '01000001000010000010001000010001000', #}
        '01000101010001000000000000000000000' #}~
]

def color(R,G,B): # Convert RGB888 to RGB565
    return (((G&0b00011100)<<3) +((B&0b11111000)>>3)<<8) + (R&0b11111000)+((G&0b11100000)>>5)

def printchar(letter,xpos,ypos,size,c1,c2,c3):
    cc = color(c1,c2,c3)
    origin = xpos
    charval = ord(letter)
    #print(charval)
    index = charval-32 #start code, 32 or space
    #print(index)
    character = cmap[index] #this is our char...
    rows = [character[i:i+5] for i in range(0,len(character),5)]
    #print(rows)
    for row in rows:
        #print(row)
        for bit in row:
            #print(bit)
            if bit == '1':
                LCD.pixel(xpos,ypos,cc)
                if size==2:
                    LCD.pixel(xpos,ypos+1,cc)
                    LCD.pixel(xpos+1,ypos,cc)
                    LCD.pixel(xpos+1,ypos+1,cc)
                if size == 3:
                    LCD.pixel(xpos,ypos,cc)
                    LCD.pixel(xpos,ypos+1,cc)
                    LCD.pixel(xpos,ypos+2,cc)
                    LCD.pixel(xpos+1,ypos,cc)
                    LCD.pixel(xpos+1,ypos+1,cc)
                    LCD.pixel(xpos+1,ypos+2,cc)
                    LCD.pixel(xpos+2,ypos,cc)
                    LCD.pixel(xpos+2,ypos+1,cc)
                    LCD.pixel(xpos+2,ypos+2,cc)
            xpos+=size
        xpos=origin
        ypos+=size

# Spacing is in pixels, this tells the printchar function where to place the next pixel for the font.  Bigger you make it the nastier it looks so don't go big!
def prnt_st(string,xpos,ypos,size,c1,c2,c3):
    if size == 1:
        spacing = 14
    if size == 2:
        spacing = 16
    if size == 3:
        spacing = 19
    for i in string:
        printchar(i,xpos,ypos,size,c1,c2,c3)
        xpos+=spacing

# Output to Display the passed text
def output_display(tmptext,tmptext2,tmptext3,tmptext4,size,size2,size3,size4):
    # Write to display to set the background to white, the 'LCD.white' color is defined in common.py
    LCD.fill(LCD.white)
    LCD.show()
    
    # Set row height for text so we can center the text vertically
    row_height = size * 5 + 30
    
    if size2 != 0:
        row_height2 = size2 * 5 + -30
    if size3 != 0:
        row_height3 = size3 * 5 + -60
    if size4 != 0:
        row_height4 = size4 * 5 + -90

    text_y = (int(HEIGHT - row_height)) // 2 # Vertical centering of text
    if tmptext2 != "Empty":
        text_y2 = (int(HEIGHT - row_height2)) // 2 # Vertical centering of text
    if tmptext3 != "Empty":
        text_y3 = (int(HEIGHT - row_height3)) // 2 # Vertical centering of text
    if tmptext4 != "Empty":
        text_y4 = (int(HEIGHT - row_height4)) // 2 # Vertical centering of text

    # Grab font size so we can center the text horizontally
    if size == 1:
        w = 5*size+8
    elif size == 2:
        w = 5*size+6
    elif size == 3:
        w = 5*size+3
    
    # Adjust the math here if the pixel spacing is adjusted in the display output functions above to correct centering
    if size2 == 1:
        w2 = 5*size2+8
    elif size2 == 2:
        w2 = 5*size2+6
    elif size2 == 3:
        w2 = 5*size2+3
    
    if size3 == 1:
        w3 = 5*size3+8
    elif size3 == 2:
        w3 = 5*size3+6
    elif size3 == 3:
        w3 = 5*size3+3
        
    if size4 == 1:
        w4 = 5*size4+8
    elif size4 == 2:
        w4 = 5*size4+6
    elif size4 == 3:
        w4 = 5*size4+3

    # This is what actually handles the centering of the text horizontally
    text_x = int((240 - len(tmptext) * w)/2) # NOTICE HARDCODE SCREEN SIZE
    if tmptext2 != "Empty":
        text_x2 = int((240 - len(tmptext2) * w2)/2)
    if tmptext3 != "Empty":
        text_x3 = int((240 - len(tmptext3) * w3)/2)
    if tmptext4 != "Empty":
        text_x4 = int((240 - len(tmptext4) * w4)/2)
    
    # Print the text to the display
    # the format for the prnt_st is: prnt_st(text to be printed, X coordinate to start, Y coordinate to start, Font size (1 to 3), Red color, Green color, Blue color)
    # could use an a simpler method to handle multi-line printing but this is down and dirty
    prnt_st(tmptext,text_x,text_y,size,0,0,0) # Center text on display
    if tmptext2 != "Empty":
        prnt_st(tmptext2,text_x2,text_y2,size2,0,0,0) # Center text on display
    if tmptext3 != "Empty":
        prnt_st(tmptext3,text_x3,text_y3,size3,0,0,0) # Center text on display
    if tmptext4 != "Empty":
        prnt_st(tmptext4,text_x4,text_y4,size4,0,0,0) # Center text on display

    # Tell the display to update with the new text and background
    LCD.show()

gc.collect()

# Game parameters
BALL_SIZE = int(SCREEN_WIDTH/28)         # size of the ball size in pixels
PADDLE_WIDTH = int(SCREEN_WIDTH/4)       # size of the paddle in pixels
PADDLE_HEIGHT = int(SCREEN_HEIGHT/36)
PADDLE_Y = SCREEN_HEIGHT-2*PADDLE_HEIGHT # Vertical position of the paddle

# variables
ballX = 64     # ball position in pixels
ballY = 0
ballVX = 1.0    # ball velocity along x in pixels per frame
ballVY = 1.0    # ball velocity along y in pixels per frame

paddleX = int(SCREEN_WIDTH/2) # paddle  position in pixels
paddleVX = 6                  # paddle velocity in pixels per frame

score = 0

def game_reset():
    global paddleX, ballX, ballY, ballVX, ballVY, score
    paddleX = (SCREEN_WIDTH - PADDLE_WIDTH) // 2
    ballX = SCREEN_WIDTH // 2
    ballY = SCREEN_HEIGHT // 2
    ballVX = random.choice([-2, 2])
    ballVY = -2
    score = 0
    gc.collect()

game_reset()

prev_paddleX = paddleX
prev_ballX = ballX
prev_ballY = ballY

pressed = False

text = "GAME OVER"
row_height = 25
text_y = int((240 - row_height) / 2) # Vertical centering of text
w = 5*3+3
text_x = int((240 - len(text) * w)/2)

while True:
    gc.collect()
    
    if pressed:
        machine.soft_reset()
    
    # move the paddle when a button is pressed
    if right.value() == 0:
        # right button pressed
        paddleX += paddleVX
        if paddleX + PADDLE_WIDTH > SCREEN_HEIGHT:
            paddleX = SCREEN_HEIGHT - PADDLE_WIDTH
    elif left.value() == 0:
        # left button pressed
        paddleX -= paddleVX
        if paddleX < 0:
            paddleX = 0
    elif keyA.value() == 0:
        pressed = True
        machine.soft_reset()
        
    
    # move the ball
    if abs(ballVX) < 1:
        # do not allow an infinite vertical trajectory for the ball
        ballVX = 1

    ballX = int(ballX + ballVX)
    ballY = int(ballY + ballVY)
    
    # collision detection
    collision=False
    if ballX < 0:
        # collision with the left edge of the screen 
        ballX = 0
        ballVX = -ballVX
        collision = True
    
    if ballX + BALL_SIZE > SCREEN_WIDTH:
        # collision with the right edge of the screen
        ballX = SCREEN_WIDTH-BALL_SIZE
        ballVX = -ballVX
        collision = True

    if ballY+BALL_SIZE>PADDLE_Y and ballX > paddleX-BALL_SIZE and ballX<paddleX+PADDLE_WIDTH+BALL_SIZE:
        # collision with the paddle
        # => change ball direction
        ballVY = -ballVY
        ballY = PADDLE_Y-BALL_SIZE
        # increase speed!
        ballVY -= 0.2
        ballVX += (ballX - (paddleX + PADDLE_WIDTH/2))/10
        collision = True
        score += 10
        
    if ballY < 0:
        # collision with the top of the screen
        ballY = 0
        ballVY = -ballVY
        collision = True
        
    if ballY + BALL_SIZE > SCREEN_HEIGHT:
        # collision with the bottom of the screen
        # => Display Game Over
        LCD.fill(LCD.white)
        LCD.show()
        prnt_st(text, text_x, text_y, 3, 0, 0, 0)
        prnt_st(str(score), int((SCREEN_WIDTH - len(str(score)) * w) / 2), 5, 2, 0, 0, 0)
        LCD.show()
                
        # wait for a button
        while True:
            if right.value() == 0:
                game_reset()
                break
            elif left.value() == 0:
                game_reset()
                break
            elif up.value() == 0:
                game_reset()
                break
            elif down.value() == 0:
                game_reset()
                break
            elif ctrl.value() == 0:
                game_reset()
                break
            elif keyA.value() == 0:
                pressed = True
                machine.soft_reset
                break
            elif keyB.value() == 0:
                game_reset()
                break
            elif keyX.value() == 0:
                game_reset()
                break
            elif keyY.value() == 0:
                game_reset()
                break
            
            time.sleep(0.001)
            
    # Remember the current positions for the next frame
    prev_paddleX = paddleX
    prev_ballX = ballX
    prev_ballY = ballY
    
    # Clear the screen
    LCD.fill(LCD.white)

    # Draw the paddle
    LCD.fill_rect(paddleX, PADDLE_Y, PADDLE_WIDTH, PADDLE_HEIGHT, LCD.black)

    # Draw the ball
    LCD.fill_rect(ballX, ballY, BALL_SIZE, BALL_SIZE, LCD.black)

    # Display the score
    prnt_st(str(score), int((SCREEN_WIDTH - len(str(score)) * w) / 2), 5, 2, 0,0,0)

    # Update the display (only once per loop)
    LCD.show()
    
    gc.collect()

    time.sleep(0.01)
