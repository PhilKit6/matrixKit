import pygame
import sys
import math
import pyperclip
import random
import time

pyperclip.set_clipboard("wl-clipboard")

WIDTH, HEIGHT = 32, 32
LED_SIZE = 20
MARGIN = 4
FPS = 30
OFF = (10, 10, 10)

pygame.init()
font = pygame.font.SysFont("Consolas", 18)
screen_width = (LED_SIZE + MARGIN) * WIDTH
ui_height = 100
screen_height = (LED_SIZE + MARGIN) * HEIGHT + ui_height
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Phil's LED Sim")
clock = pygame.time.Clock()

input_fields = {
    "r": {"rect": pygame.Rect(30, screen_height - 85, screen_width - 150, 25), "text": "0"},
    "g": {"rect": pygame.Rect(30, screen_height - 55, screen_width - 150, 25), "text": "0"},
    "b": {"rect": pygame.Rect(30, screen_height - 25, screen_width - 150, 25), "text": "0"}
}
field_order = ["r", "g", "b"]
active_field = "r"

button_rect = pygame.Rect(screen_width - 100, screen_height - 45, 90, 30)
clear_rect = pygame.Rect(screen_width - 100, screen_height - 80, 90, 30)
compiled_exprs = {"r": None, "g": None, "b": None}
error_message = ""

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
            rect = pygame.Rect(x * (LED_SIZE + MARGIN), y * (LED_SIZE + MARGIN), LED_SIZE, LED_SIZE)
            pygame.draw.rect(screen, color, rect)

def draw_ui():
    for label, field in input_fields.items():
        color = (60, 60, 60) if label == active_field else (30, 30, 30)
        pygame.draw.rect(screen, color, field["rect"], border_radius=4)
        if label == active_field:
            pygame.draw.rect(screen, (0, 255, 255), field["rect"], width=2, border_radius=4)

        prefix = f"{label}="
        text_surface = font.render(prefix + field["text"], True, (255, 255, 255))
        screen.blit(text_surface, (field["rect"].x + 5, field["rect"].y + 3))

    pygame.draw.rect(screen, (70, 130, 180), button_rect)
    screen.blit(font.render("Submit", True, (255, 255, 255)), (button_rect.x + 10, button_rect.y + 5))

    pygame.draw.rect(screen, (200, 50, 50), clear_rect)
    screen.blit(font.render("Clear", True, (255, 255, 255)), (clear_rect.x + 15, clear_rect.y + 5))

    if error_message:
        err_surface = font.render(error_message, True, (255, 0, 0))
        screen.blit(err_surface, (10, screen_height - 5 - font.get_height()))

# Splash animation
def splash_matrix(t):
    matrix = clear_matrix()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            r = int((math.sin((x + t) * 0.2) + 1) * 127.5)
            g = int((math.sin((y + t) * 0.2) + 1) * 127.5)
            b = int((math.sin((x + y + t) * 0.1) + 1) * 127.5)
            matrix[y][x] = (r, g, b)
    return matrix

# Initialize compiled expressions
for label in input_fields:
    compiled_exprs[label], error_message = compile_expr(input_fields[label]["text"])

# Key hold tracking
key_hold_start = None
key_hold_repeat_delay = 0.1

t = 0
splash_done = False
splash_duration = 100
splash_timer = 0

while True:
    screen.fill((0, 0, 0))
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            for label, field in input_fields.items():
                if field["rect"].collidepoint(event.pos):
                    active_field = label
            if button_rect.collidepoint(event.pos):
                for label in input_fields:
                    expr, err = compile_expr(input_fields[label]["text"])
                    compiled_exprs[label] = expr
                    error_message = err
            if clear_rect.collidepoint(event.pos):
                for label in input_fields:
                    input_fields[label]["text"] = "0"
                compiled_exprs = {"r": None, "g": None, "b": None}
                error_message = ""

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                i = field_order.index(active_field)
                active_field = field_order[(i + 1) % len(field_order)]
            elif event.key == pygame.K_BACKSPACE:
                key_hold_start = time.time()
                input_fields[active_field]["text"] = input_fields[active_field]["text"][:-1]
            elif event.key == pygame.K_RETURN:
                for label in input_fields:
                    expr, err = compile_expr(input_fields[label]["text"])
                    compiled_exprs[label] = expr
                    error_message = err
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
                key_hold_start = None

    # Handle key hold for Backspace
    if pygame.key.get_pressed()[pygame.K_BACKSPACE] and key_hold_start:
        if time.time() - key_hold_start > key_hold_repeat_delay:
            input_fields[active_field]["text"] = input_fields[active_field]["text"][:-1]
            key_hold_start = time.time()

    # Splash screen logic
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

                    def clamp(val): return max(0, min(255, int(val)))
                    matrix[y][x] = (clamp(r), clamp(g), clamp(b))
        except Exception as e:
            error_message = f"Runtime Error: {e}"

    draw_matrix(matrix)
    draw_ui()

    pygame.display.flip()
    t += 0.1
    clock.tick(FPS)
