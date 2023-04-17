# SPDX-FileCopyrightText: 2023 JG for Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

"""
`thermalcameralite`
================================================================================
PyGamer/PyBadge Thermal Camera Lite Project
"""

import time
import gc
import board
import keypad
import busio
from ulab import numpy as np
import displayio
import neopixel
from digitalio import DigitalInOut
from simpleio import map_range, tone
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font
from adafruit_display_shapes.rect import Rect
import adafruit_amg88xx
from index_to_rgb.iron import index_to_rgb
from thermalcamera_converters import celsius_to_fahrenheit, fahrenheit_to_celsius
from thermalcamera_config import MIN_RANGE_F, MAX_RANGE_F, SELFIE


# Instantiate the integral display and define its size
display = board.DISPLAY
display.brightness = 1.0
WIDTH = display.width
HEIGHT = display.height

# Load the text font from the fonts folder
font_0 = bitmap_font.load_font("/fonts/OpenSans-9.bdf")

# Enable the speaker
DigitalInOut(board.SPEAKER_ENABLE).switch_to_output(value=True)

# Instantiate and clear the NeoPixels
pixels = neopixel.NeoPixel(board.NEOPIXEL, 5, pixel_order=neopixel.GRB)
pixels.brightness = 0.25
pixels.fill(0x000000)

# Initialize ShiftRegisterKeys to read PyGamer/PyBadge buttons
panel = keypad.ShiftRegisterKeys(
    clock=board.BUTTON_CLOCK,
    data=board.BUTTON_OUT,
    latch=board.BUTTON_LATCH,
    key_count=8,
    value_when_pressed=True,
)

# Define front panel button event values
BUTTON_FOCUS = 0  # button B
BUTTON_SET = 2  # START button
BUTTON_HOLD = 1  # button A

# Initiate the AMG8833 Thermal Camera
i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
amg8833 = adafruit_amg88xx.AMG88XX(i2c)

# Display splash graphics
splash = displayio.Group(scale=display.width // 160)
bitmap = displayio.OnDiskBitmap("/thermalcamera_splash.bmp")
splash.append(displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader))
board.DISPLAY.show(splash)

# Thermal sensor grid axis size; AMG8833 sensor is 8x8
SENSOR_AXIS = 8

# Display grid parameters
GRID_AXIS = (2 * SENSOR_AXIS) - 1  # Number of cells per axis
GRID_SIZE = HEIGHT  # Axis size (pixels) for a square grid
GRID_X_OFFSET = WIDTH - GRID_SIZE  # Right-align grid with display boundary
CELL_SIZE = GRID_SIZE // GRID_AXIS  # Size of a grid cell in pixels
PALETTE_SIZE = 100  # Number of display colors in spectral palette (must be > 0)

# Set up the 2-D sensor data narray
SENSOR_DATA = np.array(range(SENSOR_AXIS**2)).reshape((SENSOR_AXIS, SENSOR_AXIS))
# Set up and load the 2-D display color index narray with a spectrum
GRID_DATA = np.array(range(GRID_AXIS**2)).reshape((GRID_AXIS, GRID_AXIS)) / (
    GRID_AXIS**2
)

# Convert default min/max range values from config file
MIN_RANGE_C = fahrenheit_to_celsius(MIN_RANGE_F)
MAX_RANGE_C = fahrenheit_to_celsius(MAX_RANGE_F)

# Default colors for temperature value sidebar
BLACK = 0x000000
RED = 0xFF0000
YELLOW = 0xFFFF00
CYAN = 0x00FFFF
BLUE = 0x0000FF
WHITE = 0xFFFFFF

# Text colors for setup helper's on-screen parameters
SETUP_COLORS = [("ALARM", WHITE), ("RANGE", RED), ("RANGE", CYAN)]


# ### Helpers ###
def play_tone(freq=440, duration=0.01):
    """Play a tone over the speaker"""
    tone(board.A0, freq, duration)


def flash_status(text="", duration=0.05):
    """Flash status message once"""
    status_label.color = WHITE
    status_label.text = text
    time.sleep(duration)
    status_label.color = BLACK
    time.sleep(duration)
    status_label.text = ""


def update_image_frame(selfie=False):
    """Get camera data and update display"""
    for _row in range(0, GRID_AXIS):
        for _col in range(0, GRID_AXIS):
            if selfie:
                color_index = GRID_DATA[GRID_AXIS - 1 - _row][_col]
            else:
                color_index = GRID_DATA[GRID_AXIS - 1 - _row][GRID_AXIS - 1 - _col]
            color = index_to_rgb(round(color_index * PALETTE_SIZE, 0) / PALETTE_SIZE)
            if color != image_group[((_row * GRID_AXIS) + _col)].fill:
                image_group[((_row * GRID_AXIS) + _col)].fill = color


def ulab_bilinear_interpolation():
    """2x bilinear interpolation to upscale the sensor data array; by @v923z
    and @David.Glaude."""
    GRID_DATA[1::2, ::2] = SENSOR_DATA[:-1, :]
    GRID_DATA[1::2, ::2] += SENSOR_DATA[1:, :]
    GRID_DATA[1::2, ::2] /= 2
    GRID_DATA[::, 1::2] = GRID_DATA[::, :-1:2]
    GRID_DATA[::, 1::2] += GRID_DATA[::, 2::2]
    GRID_DATA[::, 1::2] /= 2


play_tone(440, 0.1)  # Musical note A4
play_tone(880, 0.1)  # Musical note A5

# ### Define the display group ###
mkr_t0 = time.monotonic()  # Time marker: Define Display Elements
image_group = displayio.Group(scale=1)

# Define the foundational thermal image grid cells; image_group[0:224]
#   image_group[#] = image_group[ (row * GRID_AXIS) + column ]
for row in range(0, GRID_AXIS):
    for col in range(0, GRID_AXIS):
        cell_x = (col * CELL_SIZE) + GRID_X_OFFSET
        cell_y = row * CELL_SIZE
        cell = Rect(
            x=cell_x,
            y=cell_y,
            width=CELL_SIZE,
            height=CELL_SIZE,
            fill=None,
            outline=None,
            stroke=0,
        )
        image_group.append(cell)

# Define labels and values
status_label = Label(font_0, text="", color=None)
status_label.anchor_point = (0.5, 0.5)
status_label.anchored_position = ((WIDTH // 2) + (GRID_X_OFFSET // 2), HEIGHT // 2)
image_group.append(status_label)  # image_group[225]

max_label = Label(font_0, text="max", color=RED)
max_label.anchor_point = (0, 0)
max_label.anchored_position = (1, 21)
image_group.append(max_label)  # image_group[226]

max_value = Label(font_0, text=str(MAX_RANGE_F), color=RED)
max_value.anchor_point = (0, 0)
max_value.anchored_position = (1, 10)
image_group.append(max_value)  # image_group[227]

ave_label = Label(font_0, text="ave", color=YELLOW)
ave_label.anchor_point = (0, 0)
ave_label.anchored_position = (1, 62)
image_group.append(ave_label)  # image_group[228]

ave_value = Label(font_0, text="---", color=YELLOW)
ave_value.anchor_point = (0, 0)
ave_value.anchored_position = (1, 51)
image_group.append(ave_value)  # image_group[229]

min_label = Label(font_0, text="min", color=CYAN)
min_label.anchor_point = (0, 0)
min_label.anchored_position = (1, 104)
image_group.append(min_label)  # image_group[230]

min_value = Label(font_0, text=str(MIN_RANGE_F), color=CYAN)
min_value.anchor_point = (0, 0)
min_value.anchored_position = (1, 93)
image_group.append(min_value)  # image_group[231]

# ###--- PRIMARY PROCESS SETUP ---###
mkr_t1 = time.monotonic()  # Time marker: Primary Process Setup
# pylint: disable=no-member
mem_fm1 = gc.mem_free()  # Monitor free memory
DISPLAY_HOLD = False  # Active display mode; True to hold display
DISPLAY_FOCUS = False  # Standard display range; True to focus display range

# pylint: disable=invalid-name
orig_max_range_f = 0  # Establish temporary range variables
orig_min_range_f = 0

# Activate display, show preloaded sample spectrum, and play welcome tone
display.show(image_group)
update_image_frame()
flash_status("IRON", 0.75)
play_tone(880, 0.010)  # Musical note A5

# ###--- PRIMARY PROCESS LOOP ---###
while True:
    mkr_t2 = time.monotonic()  # Time marker: Acquire Sensor Data
    if DISPLAY_HOLD:
        flash_status("-HOLD-", 0.25)
    else:
        sensor = amg8833.pixels  # Get sensor_data data
    # Put sensor data in array; limit to the range of 0, 80
    SENSOR_DATA = np.clip(np.array(sensor), 0, 80)

    # Update and display max, min, and ave stats
    mkr_t4 = time.monotonic()  # Time marker: Display Statistics
    v_max = np.max(SENSOR_DATA)
    v_min = np.min(SENSOR_DATA)
    v_ave = np.mean(SENSOR_DATA)

    max_value.text = str(celsius_to_fahrenheit(v_max))
    min_value.text = str(celsius_to_fahrenheit(v_min))
    ave_value.text = str(celsius_to_fahrenheit(v_ave))

    # Normalize temperature to index values and interpolate
    mkr_t5 = time.monotonic()  # Time marker: Normalize and Interpolate
    SENSOR_DATA = (SENSOR_DATA - MIN_RANGE_C) / (MAX_RANGE_C - MIN_RANGE_C)
    GRID_DATA[::2, ::2] = SENSOR_DATA  # Copy sensor data to the grid array
    ulab_bilinear_interpolation()  # Interpolate to produce 15x15 result

    # Display image
    mkr_t6 = time.monotonic()  # Time marker: Display Image
    update_image_frame(selfie=SELFIE)

    # See if a panel button is pressed
    buttons = panel.events.get()
    if buttons and buttons.pressed:
        if buttons.key_number == BUTTON_HOLD:
            # Toggle display hold (shutter)
            play_tone(1319, 0.030)  # Musical note E6
            DISPLAY_HOLD = not DISPLAY_HOLD

        if buttons.key_number == BUTTON_FOCUS:  # Toggle display focus mode
            play_tone(698, 0.030)  # Musical note F5
            DISPLAY_FOCUS = not DISPLAY_FOCUS
            if DISPLAY_FOCUS:
                # Set range values to image min/max for focused image display
                orig_min_range_f = MIN_RANGE_F
                orig_max_range_f = MAX_RANGE_F
                MIN_RANGE_F = celsius_to_fahrenheit(v_min)
                MAX_RANGE_F = celsius_to_fahrenheit(v_max)
                # Update range min and max values in Celsius
                MIN_RANGE_C = v_min
                MAX_RANGE_C = v_max
                flash_status("FOCUS", 0.2)
            else:
                # Restore previous (original) range values for image display
                MIN_RANGE_F = orig_min_range_f
                MAX_RANGE_F = orig_max_range_f
                # Update range min and max values in Celsius
                MIN_RANGE_C = fahrenheit_to_celsius(MIN_RANGE_F)
                MAX_RANGE_C = fahrenheit_to_celsius(MAX_RANGE_F)
                flash_status("ORIG", 0.2)

    mkr_t7 = time.monotonic()  # Time marker: End of Primary Process
    gc.collect()
    mem_fm7 = gc.mem_free()

    # Print frame performance report
    print("*** PyBadge/Gamer Performance Stats ***")
    print(f"  define display: {(mkr_t1 - mkr_t0):6.3f} sec")
    print(f"  free memory:    {mem_fm1 / 1000:6.3f} Kb")
    print("")
    print("                          rate")
    print(f" 1) acquire: {(mkr_t4 - mkr_t2):6.3f} sec  ", end="")
    print(f"{(1 / (mkr_t4 - mkr_t2)):5.1f}  /sec")
    print(f" 2) stats:   {(mkr_t5 - mkr_t4):6.3f} sec")
    print(f" 3) convert: {(mkr_t6 - mkr_t5):6.3f} sec")
    print(f" 4) display: {(mkr_t7 - mkr_t6):6.3f} sec")
    print("             =======")
    print(f"total frame: {(mkr_t7 - mkr_t2):6.3f} sec  ", end="")
    print(f"{(1 / (mkr_t7 - mkr_t2)):5.1f}   /sec")
    print(f"           free memory:   {mem_fm7 / 1000:6.3f} Kb")
    print("")
