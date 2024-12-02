from WIFI_CONFIG import SSID,SSID2,PSK
import gc
import utime
import time
import usocket
import struct
from machine import Pin,SPI,PWM,soft_reset
import framebuf
import binascii
import network
import rp2
import urequests
import os
from os import listdir
from common import LCD_1inch3

BL = 13
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9

# Set to current hardware time
rtc = machine.RTC()

# Set Country Code Time Zone
rp2.country('US')

global last, set_clock, cursor, year, month, day, hour, minute, second, current, selected, buttonPressed, net, net2, cset

cset = False
net = False
net2 = "Empty"
text = "Empty"
text2 = "Empty"

pwm = PWM(Pin(13))
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
selected_pen = 142, 141, 241
unselected_pen = 18, 18, 18
background_pen = 50, 50, 70
shadow_pen = 0, 0, 0

GRID_SIZE = 25
DISPLAY_SIZE = 250

LCD = LCD_1inch3()

WIDTH = LCD.width
HEIGHT = LCD.height

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
    text_x = int((240 - len(text) * w)/2) # NOTICE HARDCODE SCREEN SIZE
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
    
# Script name logo
LCD.fill(color(255,239,205))
dtext = "IanOS"
row_height = 3 * 5 + 20
text_y = (int(HEIGHT - row_height)) // 2 # Vertical centering of text
w = 5*3+3
text_x = int((240 - len(dtext) * w)/2) # NOTICE HARDCODE SCREEN SIZE
prnt_st(dtext,text_x,text_y,3,224,224,224)
prnt_st(dtext,text_x+3,text_y,3,128,0,128)
LCD.show()
utime.sleep(5)

# Poor man's NTP module, the existing one does not allow for a timeout to be set FFS.
# Change the NTP server queried in the calling statement as well as the timeout adjustment
def get_ntp_time(host="pool.ntp.org", timeout=10):
    NTP_DELTA = 2208988800  # Time difference between 1970 and 1900
    ntp_query = b'\x1b' + 47 * b'\0'

    addr = usocket.getaddrinfo(host, 123)[0][-1]
    s = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
    s.settimeout(timeout)
    
    try:
        s.sendto(ntp_query, addr)
        msg, _ = s.recvfrom(48)
    except OSError as e:
        text = "NTP Error!"
        output_display(text, "Empty", "Empty", "Empty", 3, 0, 0, 0)
        utime.sleep(3)
        print(f"Error querying NTP server: {e}")
        return None
    finally:
        s.close()

    val = struct.unpack("!I", msg[40:44])[0]
    return val - NTP_DELTA

# Determine if DST is active or not
def is_dst(year, month, day):
    """
    Determine if a given date falls within DST for the US Central Time Zone.
    DST starts on the second Sunday of March and ends on the first Sunday of November.
    """
    # Determine the second Sunday in March
    march_start = 8  # Second Sunday must be at least the 8th
    march_sunday = march_start + (6 - utime.localtime(utime.mktime((year, 3, march_start, 0, 0, 0, 0, 0)))[6])
    
    # Determine the first Sunday in November
    november_start = 1  # First Sunday is at least the 1st
    november_sunday = november_start + (6 - utime.localtime(utime.mktime((year, 11, november_start, 0, 0, 0, 0, 0)))[6])
    
    # Check if the current date is within DST range
    dst_start = utime.mktime((year, 3, march_sunday, 2, 0, 0, 0, 0))  # DST starts at 2 AM
    dst_end = utime.mktime((year, 11, november_sunday, 2, 0, 0, 0, 0))  # DST ends at 2 AM
    now = utime.mktime((year, month, day, 0, 0, 0, 0, 0))  # Current date at midnight
    
    return dst_start <= now < dst_end

# Connect to wifi and synchronize the RTC time from NTP
def sync_time():
    global cset, year, month, day, wd, hour, minute, second, text, text2

    year, month, day, wd, hour, minute, second, _ = rtc.datetime()

#    if year >= 2024:
#        cset = True
#        text = "Time Set"
#        output_display(text, "Empty", "Empty", "Empty", 3, 0, 0, 0)
#        utime.sleep(2)
#        texta = f'{month}-{day}-{year}'
#        textb = f'{hour}:{minute}:{second}'
#        output_display(texta, textb, "Empty", "Empty", 3, 3, 0, 0)
#        utime.sleep(2)
#        print("Clock looks correct not setting time")
#        return

    text = "Setting Time"
    output_display(text, "Empty", "Empty", "Empty", 3, 0, 0, 0)
    utime.sleep(3)

    try:
        rtc.datetime((2023, 1, 1, 0, 0, 0, 0, 0))  # Reset to a known good time
        year, month, day, wd, hour, minute, second, _ = rtc.datetime()
        if not all(isinstance(x, int) for x in [year, month, day, wd, hour, minute, second]):
            raise ValueError("Invalid time values in RTC")
    except (ValueError, OSError) as e:
        print(f"RTC reset required: {e}")
        rtc.datetime((2023, 1, 1, 0, 0, 0, 0, 0))  # Reset to a known good time

    if not net:
        text = "No WiFi"
        text2 = "Time Not Set"
        output_display(text, text2, "Empty", "Empty", 3, 3, 0, 0)
        utime.sleep(2)
        return

    if net:
        while not cset:
            text = "Contacting NTP"
            text2 = "Time Not Set"
            output_display(text, text2, "Empty", "Empty", 2, 2, 0, 0)
            utime.sleep(2)

            try:
                # Adjust the timeout appropriately to your WiFi connection, may need to be longer or shorter
                ntp_time = get_ntp_time(timeout=30)
                if ntp_time:
                    cset = True
                else:
                    cset = False
            except OSError as e:
                cset = False
                text = "NTP Error!"
                output_display(text, "Empty", "Empty", "Empty", 3, 0, 0, 0)
                utime.sleep(3)
                print(f'Exception setting time {e}')
                pass
            
            if cset:
                text = "Time Set"
                output_display(text, "Empty", "Empty", "Empty", 3, 0, 0, 0)
                utime.sleep(1)
                print("Time set")

    # Get the current time in UTC
    y, mnth, d, h, m, s, wkd, yearday = utime.localtime(ntp_time)

    if is_dst(y, mnth, d):
        utc_offset = -5  # CDT (Daylight Saving Time)
    else:
        utc_offset = -6  # CST (Standard Time)

    # Adjust time
    h += utc_offset
    if h < 0:
        h += 24
        d -= 1
        if d == 0:
            mnth -= 1
            if mnth == 0:
                mnth = 12
                y -= 1
            d = [31, 29 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][mnth - 1]
    elif h >= 24:
        h -= 24
        d += 1
        # Handle end-of-month transitions
        days_in_month = [31, 29 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][mnth - 1]
        if d > days_in_month:
            d = 1
            mnth += 1
            if mnth > 12:
                mnth = 1
                y += 1

    # Update RTC with the corrected time
    if not (1 <= mnth <= 12 and 1 <= d <= 31 and 0 <= wkd <= 6 and 0 <= h <= 23 and 0 <= m <= 59 and 0 <= s <= 59):
        print("Invalid time values detected, skipping RTC update")
    else:
        try:
            print(f'Hour is: {h}')
            rtc.datetime((y, mnth, d, wkd, h, m, s, 0))
        except Exception as e:
            print(f'Exception setting time: {e}')

    year, month, day, wd, hour, minute, second, _ = rtc.datetime()
    
    texta = f'{month}-{day}-{year}'
    textb = f'{hour}:{minute}:{second}'
    output_display(texta, textb, "Empty", "Empty", 3, 3, 0, 0)
    utime.sleep(2)
    
    print(f'Month: {mnth}, Day: {d}, WkDay: {wkd}, Hour: {h}, Minute: {m}, Second: {s}')
    print(f'Year = {year}, Month = {month}, Day = {day}, Hour = {hour}, Minute = {minute}, Second = {second}')
    print("Time set in sync_time function!")
   
# Connect to WiFi via the router first and then try the mobile hotspot
def connect_net():
    global net, cset, text, text2

    # Display connection status
    text = "Configuring"
    text2 = "WiFi"
    output_display(text, text2,"Empty","Empty",3,3,0,0)
    utime.sleep(2)

    # Wifi Network Info
    ssids = [SSID, SSID2]
    passwords = [PSK, PSK]
    ssid_index = 0  # Start with the primary SSID
    attempts = 0    # Track connection attempts

    # Activate Thrusters
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # If already connected, return
    if wlan.isconnected():
        print("WiFi is already connected.")
        net = True
        status = wlan.ifconfig()
        print('ip = ' + status[0])
        text = "IP Already Set"
        text2 = f'{status[0]}'
        output_display(text, text2,"Empty","Empty",2,2,0,0)
        utime.sleep(2)
        if not cset:
            sync_time()
        return

    while not wlan.isconnected() and ssid_index < len(ssids):
        ssid = ssids[ssid_index]
        password = passwords[ssid_index]

        qtext = "Connecting"
        qtext2 = "To Wifi"
        output_display(qtext, qtext2,"Empty","Empty",3,3,0,0)
        wlan.connect(ssid, password)
        utime.sleep(2)

        # Wait for connect or fail
        max_wait = 30
        while max_wait > 0 and not wlan.isconnected():
            attempts += 1
            print(f"Attempt {attempts} to connect to {ssid}")

            if not wlan.isconnected():  # Check for errors
                print(f"Error connecting to WiFi (status {wlan.status()})")
                if attempts >= 15 and ssid_index < len(ssids) - 1:
                    print(f"Switching to SSID2 after {attempts} attempts.")
                    text = "WiFi Error!"
                    text2 = "Enabling Hotspot!"
                    output_display(text, text2,"Empty","Empty",3,2,0,0)
                    utime.sleep(2)
                    ssid_index += 1  # Switch to the secondary SSID
                    attempts = 0      # Reset attempts for the new SSID
                    break
                else:
                    text = "Retrying"
                    text2 = "WiFi"
                    output_display(text, text2,"Empty","Empty",3,3,0,0)
                    utime.sleep(1)

            max_wait -= 1
            wlan.connect(ssid, password)
            utime.sleep(1)

    if wlan.isconnected():
        net = True
        status = wlan.ifconfig()
        print('ip = ' + status[0])
        text = "WiFi Link Up!"
        text2 = f'{status[0]}'
        output_display(text, text2,"Empty","Empty",2,2,0,0)
        utime.sleep(3)
        if not cset:
            sync_time()
    else:
        # Write to Display
        text = "No WiFi!"
        text2 = "Try Rebooting!"
        output_display(text, text2,"Empty","Empty",3,2,0,0)
        utime.sleep(2)
        print("Failed to connect to any WiFi network.")
        
    gc.collect()
    
try:
    if not net:
        while not net:
            if net:
                print("In outer net_connect() loop")
                print("Breaking net connect loop!")
                break
            max_tries = 10
            while max_tries > 0:
                if net:
                    print("In inner net_connect() loop")
                    print("Breaking net connect loop!")
                    break

                connect_net()
                max_tries -= 1
        
        gc.collect()
except Exception as e:
    # Write to Display
    if not net:
        text = "No WiFi!"
        text2 = "Try Rebooting!"
        output_display(text,text2,"Empty","Empty",3,2,0,0)
        utime.sleep(2)
    print(f'Error configuring WiFi or setting time {e}')

def hsv_to_rgb(h: float, s: float, v: float) -> tuple[float, float, float]:
    if s == 0.0:
        return v, v, v
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    v = int(v * 255)
    t = int(t * 255)
    p = int(p * 255)
    q = int(q * 255)
    i = i % 6
    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    if i == 2:
        return p, v, t
    if i == 3:
        return p, q, v
    if i == 4:
        return t, p, v
    if i == 5:
        return v, p, q
    
    gc.collect()


def get_applications() -> list[dict[str, str]]:
    print("Getting Apps from Storage!")
    applications = []
    for file in listdir():
        if file.endswith(".mpy") and file != "main.py" and file != "WIFI_CONFIG.py" and file != "common.mpy":
            title = " ".join([v[:1].upper() + v[1:] for v in file[:-4].split("_")])
            applications.append(
                {
                    "file": file[:-4],  # exclude the '.py' extension
                    "title": title
                }
            )
    gc.collect()
    return sorted(applications, key=lambda x: x["title"])

def prepare_for_launch() -> None:
    print("In Prepare for Launch")
    for k in locals().keys():
        if k not in ("__name__",
                     "application_file_to_launch",
                     "gc"):
            del locals()[k]
    gc.collect()

def menu() -> str:
    applications = get_applications()
    selected_item = 2
    scroll_position = 2
    target_scroll_position = 2

    # Reduce the calls to gc.collect(); only trigger it when really necessary
    gc.collect()  

    last_button_check = utime.ticks_ms()  # Keep track of the last button check time
    
    while True:
        t = utime.ticks_ms() / 1000.0

        ## Check buttons only periodically (e.g., every 20ms)
        if utime.ticks_ms() - last_button_check > 20:
            if up.value() == 0:
                target_scroll_position = (target_scroll_position - 1) % len(applications)

            if down.value() == 0:
                target_scroll_position = (target_scroll_position + 1) % len(applications)

            # If key A is pressed, return the selected application's file
            if keyA.value() == 0:
                return applications[selected_item]["file"]

            last_button_check = utime.ticks_ms()

        # Smooth scrolling position
        scroll_position += (target_scroll_position - scroll_position) / 5

        # Only calculate the grid and color changes if necessary
        time_factor = int(t * 5)
        for y in range(0, DISPLAY_SIZE // GRID_SIZE):
            for x in range(0, DISPLAY_SIZE // GRID_SIZE):
                h = (x + y + time_factor) / 50.0
                r, g, b = hsv_to_rgb(h, 0.5, 1)
                LCD.fill_rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE, color(r, g, b))

        # Determine the closest item to the scroll position
        selected_item = round(scroll_position)

        # Draw the list of applications
        for list_index, application in enumerate(applications):
            distance = list_index - scroll_position
            text_size = 4 if selected_item == list_index else 3
            row_height = text_size * 5 + 20

            # Center the list items vertically
            text_y = int(120 + distance * row_height - (row_height / 2))
            
            w = 5*3+3
            
            # This is what actually handles the centering of the text horizontally
            text_x = int((240 - len(application["title"]) * w)/2) # NOTICE HARDCODE SCREEN SIZE

            # Draw the text, adding shadow to the selected item
            if selected_item == list_index:
                R,G,B = shadow_pen
                prnt_st(application["title"], text_x + 1, text_y + 2, 3, R, G, B)

            text_pen = selected_pen if selected_item == list_index else unselected_pen
            R,G,B = text_pen
            prnt_st(application["title"], text_x, text_y, 3, R, G, B)

        LCD.show()

        # Perform garbage collection less frequently, e.g., every few iterations
        if t % 10 == 0:
            gc.collect()

# The application we will be launching. This should be our only global, so we can
# drop everything else.
print("Getting Apps!")
application_file_to_launch = menu()

# Run whatever we've set up to.
prepare_for_launch()

__import__(application_file_to_launch)
