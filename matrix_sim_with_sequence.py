import pygame
import sys
import math
import pyperclip

pyperclip.set_clipboard("wl-clipboard")

WIDTH, HEIGHT = 32, 32
LED_SIZE = 20
MARGIN = 1
FPS = 30
OFF = (10, 10, 10)

pygame.init()
font = pygame.font.SysFont("Consolas", 18)

screen_width = (LED_SIZE + MARGIN) * WIDTH
ui_height = 100
screen_height = (LED_SIZE + MARGIN) * HEIGHT + ui_height
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("RGB Equation Animator with Frame Sequences")
clock = pygame.time.Clock()

# --- INPUT FIELD STATE ---
input_fields = {
    "r": {"rect": pygame.Rect(30, screen_height - 85, screen_width - 150, 25),
          "text": "255 if (x + t) % 32 == y else 0"},
    "g": {"rect": pygame.Rect(30, screen_height - 55, screen_width - 150, 25),
          "text": "0"},
    "b": {"rect": pygame.Rect(30, screen_height - 25, screen_width - 150, 25),
          "text": "0"}
}
active_field = None

submit_button_rect = pygame.Rect(screen_width - 100, screen_height - 45, 90, 30)
mode_button_rect = pygame.Rect(screen_width - 100, screen_height - 85, 90, 30)

compiled_exprs = {"r": None, "g": None, "b": None}
error_message = ""
mode = "equation"

safe_globals = {
    "__builtins__": None,
    "math": math,
    "abs": abs,
    "round": round,
    "min": min,
    "max": max
}

# --- Frame sequence sample ---
sample_frames = [
    [[(255, 0, 0) if x == 16 and y == 16 else OFF for x in range(WIDTH)] for y in range(HEIGHT)],
    [[(0, 255, 0) if x == 10 and y == 16 else OFF for x in range(WIDTH)] for y in range(HEIGHT)],
    [[(0, 0, 255) if x == 22 and y == 16 else OFF for x in range(WIDTH)] for y in range(HEIGHT)],
]

def compile_expr(expr):
    try:
        return compile(expr, "<string>", "eval"), ""
    except Exception as e:
        return None, f"Syntax Error: {e}"

# --- MATRIX FUNCTIONS ---
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
        pygame.draw.rect(screen, (30, 30, 30), field["rect"])
        prefix = f"{label}="
        text_surface = font.render(prefix + field["text"], True, (255, 255, 255))
        screen.blit(text_surface, (field["rect"].x + 5, field["rect"].y + 3))

    pygame.draw.rect(screen, (70, 130, 180), submit_button_rect)
    screen.blit(font.render("Submit", True, (255, 255, 255)), (submit_button_rect.x + 10, submit_button_rect.y + 5))

    pygame.draw.rect(screen, (100, 180, 100), mode_button_rect)
    mode_label = "Mode: Eqn" if mode == "equation" else "Mode: Seq"
    screen.blit(font.render(mode_label, True, (0, 0, 0)), (mode_button_rect.x + 5, mode_button_rect.y + 5))

    if error_message:
        err_surface = font.render(error_message, True, (255, 0, 0))
        screen.blit(err_surface, (10, screen_height - 5 - font.get_height()))

# --- MAIN LOOP ---
t = 0
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
            if submit_button_rect.collidepoint(event.pos):
                for label in input_fields:
                    expr, err = compile_expr(input_fields[label]["text"])
                    compiled_exprs[label] = expr
                    error_message = err
            if mode_button_rect.collidepoint(event.pos):
                mode = "sequence" if mode == "equation" else "equation"

        elif event.type == pygame.KEYDOWN and active_field:
            if event.key == pygame.K_BACKSPACE:
                input_fields[active_field]["text"] = input_fields[active_field]["text"][:-1]
            elif event.key == pygame.K_RETURN:
                expr, err = compile_expr(input_fields[active_field]["text"])
                compiled_exprs[active_field] = expr
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

    # --- Draw matrix depending on mode ---
    if mode == "equation":
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
    else:
        frame_index = int(t * 2) % len(sample_frames)
        matrix = sample_frames[frame_index]

    draw_matrix(matrix)
    draw_ui()

    pygame.display.flip()
    t += 0.1
    clock.tick(FPS)
