import pygame
import sys
import math
import pyperclip
import time

pyperclip.set_clipboard("wl-clipboard")

WIDTH, HEIGHT = 32, 32
LED_SIZE = 20
MARGIN = 1
FPS = 30
OFF = (10, 10, 10)

pygame.init()
font = pygame.font.SysFont("Consolas", 18)
screen_width = (LED_SIZE + MARGIN) * WIDTH
ui_height = 140
screen_height = (LED_SIZE + MARGIN) * HEIGHT + ui_height
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Phil's LED Sim")
clock = pygame.time.Clock()

input_fields = {
    "r": {"rect": pygame.Rect(30, screen_height - 115, screen_width - 150, 25), "text": "0"},
    "g": {"rect": pygame.Rect(30, screen_height - 85, screen_width - 150, 25), "text": "0"},
    "b": {"rect": pygame.Rect(30, screen_height - 55, screen_width - 150, 25), "text": "0"}
}
active_field = None

submit_button = pygame.Rect(screen_width - 100, screen_height - 45, 90, 30)
clear_button = pygame.Rect(screen_width - 100, screen_height - 80, 90, 30)
export_button = pygame.Rect(screen_width - 100, screen_height - 115, 90, 30)

compiled_exprs = {"r": None, "g": None, "b": None}
error_message = ""
saved_message = ""
saved_message_timer = 0

safe_globals = {
    "__builtins__": None,
    "math": math,
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "int": int,
    "float": float
}

backspace_held = False
backspace_timer = 0

def compile_expr(expr):
    try:
        return compile(expr, "<string>", "eval"), ""
    except Exception as e:
        return None, f"Syntax Error: {e}"

def clear_matrix():
    return [[OFF for _ in range(WIDTH)] for _ in range(HEIGHT)]

def draw_matrix(matrix):
    for y in range(HEIGHT):
        for x in range(WIDTH):
            color = matrix[y][x]
            rect = pygame.Rect(
                x * (LED_SIZE + MARGIN),
                y * (LED_SIZE + MARGIN),
                LED_SIZE,
                LED_SIZE
            )
            pygame.draw.rect(screen, color, rect)

def draw_ui():
    for label, field in input_fields.items():
        color = (50, 50, 50) if active_field == label else (30, 30, 30)
        pygame.draw.rect(screen, color, field["rect"])
        prefix = f"{label}="
        text_surface = font.render(prefix + field["text"], True, (255, 255, 255))
        screen.blit(text_surface, (field["rect"].x + 5, field["rect"].y + 3))

    pygame.draw.rect(screen, (70, 130, 180), submit_button)
    screen.blit(font.render("Submit", True, (255, 255, 255)), (submit_button.x + 10, submit_button.y + 5))

    pygame.draw.rect(screen, (200, 50, 50), clear_button)
    screen.blit(font.render("Clear", True, (255, 255, 255)), (clear_button.x + 15, clear_button.y + 5))

    pygame.draw.rect(screen, (50, 180, 90), export_button)
    screen.blit(font.render("Export", True, (255, 255, 255)), (export_button.x + 10, export_button.y + 5))

    if error_message:
        err_surface = font.render(error_message, True, (255, 0, 0))
        screen.blit(err_surface, (10, screen_height - 5 - font.get_height()))

    if saved_message:
        save_surface = font.render(saved_message, True, (0, 255, 0))
        screen.blit(save_surface, (10, screen_height - 30))

def splash_matrix(t):
    matrix = clear_matrix()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            r = int((math.sin((x + t) * 0.2) + 1) * 127.5)
            g = int((math.sin((y + t) * 0.2) + 1) * 127.5)
            b = int((math.sin((x + y + t) * 0.1) + 1) * 127.5)
            matrix[y][x] = (r, g, b)
    return matrix

def export_to_micropython():
    filename = f"export_{int(time.time())}.py"
    with open(filename, "w") as f:
        f.write(
            "import time\n"
            "import math\n"
            "from picographics import PicoGraphics, DISPLAY_COSMIC_UNICORN\n"
            "from cosmic_unicorn import CosmicUnicorn\n\n"
            "cu = CosmicUnicorn()\n"
            "graphics = PicoGraphics(display=DISPLAY_COSMIC_UNICORN)\n"
            "cu.set_brightness(0.5)\n\n"
            "WIDTH, HEIGHT = cu.WIDTH, cu.HEIGHT\n\n"
            "def compute_color(x, y, t):\n"
            "    try:\n"
            f"        r = {input_fields['r']['text']}\n"
            f"        g = {input_fields['g']['text']}\n"
            f"        b = {input_fields['b']['text']}\n"
            "    except:\n"
            "        r = g = b = 0\n"
            "    return max(0, min(255, int(r))), max(0, min(255, int(g))), max(0, min(255, int(b)))\n\n"
            "t = 0\n"
            "while True:\n"
            "    for y in range(HEIGHT):\n"
            "        for x in range(WIDTH):\n"
            "            r, g, b = compute_color(x, y, t)\n"
            "            cu.set_pixel(x, y, r, g, b)\n"
            "    cu.update()\n"
            "    t += 0.1\n"
            "    time.sleep(0.03)\n"
        )
    return filename

# --- Main Loop ---
t = 0
splash_done = False
splash_timer = 0
splash_duration = 100

for label in input_fields:
    compiled_exprs[label], error_message = compile_expr(input_fields[label]["text"])

while True:
    screen.fill((0, 0, 0))
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            active_field = None
            for label, field in input_fields.items():
                if field["rect"].collidepoint(event.pos):
                    active_field = label
            if submit_button.collidepoint(event.pos):
                for label in input_fields:
                    compiled_exprs[label], error_message = compile_expr(input_fields[label]["text"])
            if clear_button.collidepoint(event.pos):
                for label in input_fields:
                    input_fields[label]["text"] = "0"
                compiled_exprs = {"r": None, "g": None, "b": None}
                error_message = ""
            if export_button.collidepoint(event.pos):
                saved_filename = export_to_micropython()
                saved_message = f"Exported: {saved_filename}"
                saved_message_timer = 90  # ~3 sec

        elif event.type == pygame.KEYDOWN:
            if active_field:
                if event.key == pygame.K_BACKSPACE:
                    backspace_held = True
                    backspace_timer = 0
                    input_fields[active_field]["text"] = input_fields[active_field]["text"][:-1]
                elif event.key == pygame.K_RETURN:
                    compiled_exprs[active_field], error_message = compile_expr(input_fields[active_field]["text"])
                elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    try:
                        pasted = pyperclip.paste()
                        if pasted:
                            input_fields[active_field]["text"] += pasted
                    except Exception as e:
                        error_message = f"Paste Error: {e}"
                else:
                    input_fields[active_field]["text"] += event.unicode

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_BACKSPACE:
                backspace_held = False

    if backspace_held and active_field:
        backspace_timer += 1
        if backspace_timer > 10:
            input_fields[active_field]["text"] = input_fields[active_field]["text"][:-1]

    if saved_message_timer > 0:
        saved_message_timer -= 1
    else:
        saved_message = ""

    if not splash_done:
        matrix = splash_matrix(t)
        splash_timer += 1
        if splash_timer > splash_duration:
            splash_done = True
    else:
        matrix = clear_matrix()
        try:
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    context = {"x": x, "y": y, "t": t}
                    r = eval(compiled_exprs["r"], safe_globals, context) if compiled_exprs["r"] else 0
                    g = eval(compiled_exprs["g"], safe_globals, context) if compiled_exprs["g"] else 0
                    b = eval(compiled_exprs["b"], safe_globals, context) if compiled_exprs["b"] else 0
                    matrix[y][x] = (max(0, min(255, int(r))),
                                    max(0, min(255, int(g))),
                                    max(0, min(255, int(b))))
        except Exception as e:
            error_message = f"Runtime Error: {e}"

    draw_matrix(matrix)
    draw_ui()
    pygame.display.flip()
    t += 0.1
    clock.tick(FPS)
