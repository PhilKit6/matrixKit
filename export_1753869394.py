import time
import math
from picographics import PicoGraphics, DISPLAY_COSMIC_UNICORN
from cosmic_unicorn import CosmicUnicorn

cu = CosmicUnicorn()
graphics = PicoGraphics(display=DISPLAY_COSMIC_UNICORN)
cu.set_brightness(0.5)

WIDTH, HEIGHT = cu.WIDTH, cu.HEIGHT

def compute_color(x, y, t):
    try:
        r = int((math.sin(x * 0.3 + t) + 1) * 127.5)
        g = int((math.sin(y * 0.3 + t + math.cos(x * 0.2 + t)) + 1) * 127.5)
        b = int((math.sin((x + y) * 0.2 - t * 1.5) + 1) * 127.5)
    except:
        r = g = b = 0
    return max(0, min(255, int(r))), max(0, min(255, int(g))), max(0, min(255, int(b)))

t = 0
while True:
    for y in range(HEIGHT):
        for x in range(WIDTH):
            r, g, b = compute_color(x, y, t)
            cu.set_pixel(x, y, r, g, b)
    cu.update()
    t += 0.1
    time.sleep(0.03)
