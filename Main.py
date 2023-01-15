# Imports
import pygame as pg
import json
from json import JSONDecodeError
from os import path

# Pygame setup
pg.init()

# Functions called before window made

# Creates outline for text. Not my code, so uncommented

_circle_cache = {}


def _circlepoints(r):
    r = int(round(r))
    if r in _circle_cache:
        return _circle_cache[r]
    x, y, e = r, 0, 1 - r
    _circle_cache[r] = points = []
    while x >= y:
        points.append((x, y))
        y += 1
        if e < 0:
            e += 2 * y - 1
        else:
            x -= 1
            e += 2 * (y - x) - 1
    points += [(y, x) for x, y in points if x > y]
    points += [(-x, y) for x, y in points if x]
    points += [(x, -y) for x, y in points if y]
    points.sort()
    return points


def outline_render(text, font, gfcolor, ocolor, opx=2):
    textsurface = font.render(text, True, gfcolor).convert_alpha()
    w = textsurface.get_width() + 2 * opx
    h = font.get_height()

    osurf = pg.Surface((w, h + 2 * opx)).convert_alpha()
    osurf.fill((0, 0, 0, 0))

    surf = osurf.copy()

    osurf.blit(font.render(text, True, ocolor).convert_alpha(), (0, 0))

    for dx, dy in _circlepoints(opx):
        surf.blit(osurf, (dx + opx, dy + opx))

    surf.blit(textsurface, (opx, opx))
    return surf


# End borrowed code

# Saves display settings
def save_display_config(full_in, screen_width_in, screen_height_in, display_number_in, framerate_in, frame_counter_in):
    # Wrap input settings in JSON format
    display_config = {
        "Fullscreen (0 for full, 1 for windowed, 2 for borderless windowed)": full_in,
        "Screen Width (in px)": screen_width_in,
        "Screen Height (in px)": screen_height_in,
        "Display Number (0 for primary monitor)": display_number_in,
        "Framerate (in fps)": framerate_in,
        "Frame Counter On (true or false)": frame_counter_in
    }
    # Save to file
    with open("config.json", "w") as write:
        json.dump(display_config, write, indent=2)


# Creates and saves default display settings
def create_default_display_config(fullscreen_in = 0, display_number_in = 0, framerate_number_in = 60, frame_counter_in = False):
    # Attempts to read system for defaults
    resolution_out = pg.display.get_desktop_sizes()[0]
    fullscreen_out = fullscreen_in
    screen_width_out = resolution_out[0]
    screen_height_out = resolution_out[1]
    display_number_out = display_number_in
    framerate_number_out = framerate_number_in
    frame_counter_out = frame_counter_in

    # Checks that system defaults are valid
    try:
        # If the gathered display information is of an incorrect type, falls back to 720p
        if not (type(screen_width_out) or type(screen_height_out) is int) or (
                screen_height_out < 1 or screen_width_out < 0):
            raise TypeError("Given invalid resolution")

        # If the gathered refresh rate information is of an incorrect type, falls back on 120fps
        if not type(framerate_number_out) is int or framerate_number_out < 1:
            raise TypeError("Given invalid framerate")

    # Error for if resolution is invalid
    except TypeError("Given invalid resolution"):
        print("Error 5: Could not parse display information, defaulting to 720p")
        screen_width_out = 1280
        screen_height_out = 720

    # Error for if framerate is invalid
    except TypeError("Given invalid framerate"):
        print("Error 4: Could not parse framerate, defaulting to 60fps")
        framerate_number_out = 60

    # Saves display information for the future
    save_display_config(fullscreen_out, screen_width_out, screen_height_out, display_number_out, framerate_number_out,
                        frame_counter_out)

    return fullscreen_out, screen_width_out, screen_height_out, display_number_out, \
        framerate_number_out, frame_counter_out


# Loads fonts based on passed height
def font_size_change(window_size):
    # Set scale used (height of the window / 100)
    object_scale = window_size / 100

    # Load fonts, scaled with window size
    scaled_small_font = pg.font.SysFont(pg.font.get_default_font(), int(5 * object_scale))

    scaled_medium_font = pg.font.SysFont(pg.font.get_default_font(), int(8 * object_scale))

    scaled_large_font = pg.font.SysFont(pg.font.get_default_font(), int(12 * object_scale))

    scaled_huge_font = pg.font.SysFont(pg.font.get_default_font(), int(25 * object_scale))

    # Output fonts
    return scaled_small_font, scaled_medium_font, scaled_large_font, scaled_huge_font, object_scale


def frame_counter_function():
    if frame_counter:
        fps_text = ScreenText(str(int(frame_clock.get_fps())), 0, 0, font=small_font)
        fps_text.render(x_off=True, y_off=True)


# Attempts to read configuration file
try:

    # If there's no path to the file, raises OS error
    if not path.exists("config.json"):
        raise OSError()

    # Opens configuration file
    with open("config.json", "r") as openfile:

        # Reads file and saves values
        loaded_config = json.load(openfile)

    # Assigns configuration variables to python variables for later use
    loaded_fullscreen = loaded_config["Fullscreen (0 for full, 1 for windowed, 2 for borderless windowed)"]
    loaded_screen_width = loaded_config["Screen Width (in px)"]
    loaded_screen_height = loaded_config["Screen Height (in px)"]
    loaded_display_number = loaded_config["Display Number (0 for primary monitor)"]
    loaded_framerate = loaded_config["Framerate (in fps)"]
    loaded_frame_counter = loaded_config["Frame Counter On (true or false)"]

    # Raises a TypeError if the read configuration variables are invalid data types
    if not (type(loaded_fullscreen) or type(loaded_screen_width) or type(loaded_screen_height) or type(loaded_display_number) or
            type(loaded_framerate) is int) or (loaded_screen_height < 1 or loaded_screen_width < 0 or loaded_framerate < 1 or
                                        type(loaded_frame_counter) is not bool):
        raise TypeError

    # Changes resolution ONLY if resolution is too big

    fullscreen, screen_width, screen_height, display_number, framerate, frame_counter = create_default_display_config(loaded_fullscreen, loaded_display_number,loaded_framerate ,loaded_frame_counter)
    if loaded_screen_height > screen_height or loaded_screen_width > screen_width:
        print("Error 6: Loaded resolution too big! Changing resolution to something that your mighty monitor can handle")

    else:
        screen_width = loaded_screen_width
        screen_height = loaded_screen_height

# If the config file doesn't exist, recreates the file and sets values to default
except OSError:
    print("No configuration file found! Creating from scratch")
    fullscreen, screen_width, screen_height, display_number, framerate, frame_counter = create_default_display_config()

# If the config file contained invalid data, recreates the file and sets values to default
except TypeError:
    print("Error 2: Invalid configuration file, recreating from scratch")
    fullscreen, screen_width, screen_height, display_number, framerate, frame_counter = create_default_display_config()

# If the config file couldn't be read, recreates the file and sets values to default
except JSONDecodeError:
    print("Error 3: Unreadable configuration file, recreating from scratch")
    fullscreen, screen_width, screen_height, display_number, framerate, frame_counter = create_default_display_config()

# TODO: Create logic for changing window when new display is added
# Create window
if fullscreen == 0:
    screen = pg.display.set_mode(size=(screen_width, screen_height), flags=pg.FULLSCREEN,
                                 display=display_number, vsync=1)
elif fullscreen == 1:
    screen = pg.display.set_mode(size=(screen_width * 0.8, screen_height * 0.8),
                                 vsync=1)
else:
    screen = pg.display.set_mode(size=(screen_width, screen_height), flags=pg.NOFRAME, vsync=1)

# Variables after screen renders

# Set Window name
pg.display.set_caption("Test")

# Flag game state
state = 1

# Stores initial window size
width, height = pg.display.get_window_size()

# Load some colours
grey_one = pg.Color("#2e3440")
grey_two = pg.Color("#3b4252")
grey_three = pg.Color("#434c5e")
grey_four = pg.Color("#4c566a")
white_one = pg.Color("#eceff4")
white_two = pg.Color("#e5e9f0")
white_three = pg.Color("#d8dee9")
blue = pg.Color("#5e81ac")
light_blue = pg.Color("#81a1c1")
teal = pg.Color("#8fbcbb")
sky_blue = pg.Color("#88c0d0")
red = pg.Color("#bf616a")
orange = pg.Color("#d08770")
yellow = pg.Color("#ebcb8b")
green = pg.Color("#a3be8c")
purple = pg.Color("#b48ead")

# Loads fonts based on starting height
small_font, medium_font, large_font, huge_font, scale = font_size_change(height)

# Sets up movement and framerate titles
frame_clock = pg.time.Clock()

move_clock = pg.time.Clock()


# Used classes
# TODO: Create shape button

# Class for more easily printing text directly to the screen
# Follows (Text input, x position, y position, main colour of the text, font used)
class ScreenText:
    def __init__(self, text, x, y, colour=sky_blue, font=large_font):

        # Loads all input properties as object properties
        self.x = x
        self.y = y
        self.text = text
        self.colour = colour
        self.font = font

    # Function to call for the text to be rendered. x_off and y_off being false result in the x/y coordinates being the
    # centre of the text rather than the top right corner
    def render(self, x_off=False, y_off=False):

        # Loads text and correctable x/y coordinates
        render_text = self.font.render(self.text, True, self.colour)
        x_adjustable = self.x
        y_adjustable = self.y

        # Logic to centre each coordinate if enabled
        if not x_off:
            x_adjustable -= render_text.get_rect()[2] / 2

        if not y_off:
            y_adjustable -= render_text.get_rect()[3] / 2

        # Renders text
        screen.blit(render_text, (x_adjustable, self.y))


# Subclass of ScreenText that can be clicked like a button.
# Follows (Text input, x position, y position, main colour of the text, highlight colour for when text is hovered,
# click colour for while text is pressed, font used)
class ClickText(ScreenText):
    def __init__(self, text, x, y, colour=blue, highlight_colour=green, click_colour=teal, font=large_font):

        # Loads parent class properties and additional properties
        super().__init__(text, x, y)
        self.colour = colour
        self.highlight_colour = highlight_colour
        self.click_colour = click_colour
        self.font = font
        self.prior_pressed = False
        self.toggled = False

    # Function to render text that can be clicked and activates continuously and immediately upon pressing
    def render_click(self, x_off=False, y_off=False):

        # Loads function properties
        colour = self.colour
        currently_clicking = False
        render_text = self.font.render(self.text, True, self.colour)
        render_text_hitbox = render_text.get_rect()
        render_text_hitbox.x += self.x
        render_text_hitbox.y += self.y
        x_adjustable = self.x
        y_adjustable = self.y

        # Logic to centre each coordinate if enabled
        if not x_off:
            x_adjustable -= render_text.get_rect()[2] / 2

        if not y_off:
            y_adjustable -= render_text.get_rect()[3] / 2

        # If mouse isn't over text, render it like normal text
        if not render_text_hitbox.collidepoint(mouse):
            screen.blit(render_text, (x_adjustable, y_adjustable))

        # If mouse is currently over text, deliberate further
        else:

            # If mouse is also pressed, return that mouse is clicking and change the button colour
            if pg.mouse.get_pressed()[0]:
                currently_clicking = True
                colour = self.click_colour

            # Render the text
            screen.blit(outline_render(self.text, self.font, colour, self.highlight_colour),
                        (x_adjustable, y_adjustable))

        return currently_clicking

    # Similar to above function, but stores if it has or hasn't been pressed once, like a toggle
    def render_toggle(self, x_off=False, y_off=False):

        # If the clickable text has been clicked on, save that info
        if self.render_click(x_off, y_off):
            self.prior_pressed = True

        # If the mouse has clicked then unclicked the text, change toggle status of the button and reset prior pressed
        if self.prior_pressed and not pg.mouse.get_pressed()[0]:
            self.toggled = not self.toggled
            self.prior_pressed = False

        return self.toggled

    # Similar to above function, but it only returns a result once
    def single_render_click(self, x_off=False, y_off=False):

        # Determines if button has been pressed than released
        activated = False

        # If the clickable text has been clicked on, save that info
        if self.render_click(x_off, y_off):
            self.prior_pressed = True

        # If the mouse has clicked then unclicked the text, report this press and reset prior pressed
        if self.prior_pressed and not pg.mouse.get_pressed()[0]:
            activated = True
            self.prior_pressed = False

        return activated


# Objects on title screen

# Title for main screen
title = ScreenText("Title!", width / 2, scale, font=huge_font)

# Title for settings screen
title_settings = ScreenText("Settings", width / 2, scale, font=huge_font)

# Square used to test motion
test_square = pg.Rect(0, 0, 10 * scale, 10 * scale)

# Spacing distance between text
text_space_title = 12 * scale

# Spacing distance from left side
text_location_title = 18 * scale

# Example begin button (By default moves the test box)
begin_button = ClickText("Launch", text_location_title, 2 * text_space_title)

# Example toggle button (By default toggles visibility of the test box)
toggle_button = ClickText("Toggle Visibility", text_location_title, 3 * text_space_title)

# Configure button (goes to settings when clicked)
configure_button = ClickText("Configure", text_location_title, 4 * text_space_title)

# Quit button (exits the program)
quit_button = ClickText("Exit", text_location_title, 5 * text_space_title)

# Objects on config screen
back_button = ClickText("Back", text_location_title, 2 * text_space_title)

# Basic program loop
while state != 0:
    # Basic program loop setup

    # Sets Framerate
    frame_clock.tick(framerate)

    # Sets program speed

    dt = move_clock.tick() * (1.012)

    # Unit of velocity (travels the height of the screen in a bit more than one second)
    VU = (scale / 10) * dt

    # Gets mouse coordinates
    mouse = pg.mouse.get_pos()

    # Checks if user hits close in window
    for event in pg.event.get():
        # Checks if corner close button is pressed
        if event.type == pg.QUIT:
            state = 0

    # Creates blank screen
    screen.fill(grey_one)

    # Title screen, occurs in game loop only if state = 1
    if state == 1:

        # Create title
        title.render(y_off=True)

        # Button that if toggled shows a box
        if not toggle_button.render_toggle(True, True):
            pg.draw.rect(screen, purple, test_square)

        # Button that when pressed moves the box
        if begin_button.render_click(True, True):
            test_square.y += VU

            # Resets position if the box hits the screen edge
            if test_square.y >= height:
                test_square.y = 0

        # Button that if clicked switches the screen to the settings
        if configure_button.single_render_click(True, True):
            state = 2

        # Button that if clicked quited the game
        if quit_button.single_render_click(True, True):
            state = 0

        # Run FPS counter if enabled
        frame_counter_function()

    # Settings menu, occurs only if state = 2
    elif state == 2:

        # Create title
        title_settings.render(y_off=True)

        # Runs frame counter if enabled
        frame_counter_function()

        # TODO: Fill out with settings
        # TODO: Make settings changes instant
        # TODO: Account for different aspect ratios when drawing objects (21:9, 16:9, 16:10, 3:2, 4:3)

        # Button that returns to main screen if clicked
        if back_button.single_render_click(True, True):
            state = 1

    # Update display
    pg.display.update()

# Closes window
pg.quit()
