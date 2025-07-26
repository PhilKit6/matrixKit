# LED Matrix RGB Equation Simulator





This project is an interactive LED matrix simulator designed to provide a virtual platform for developing animations for a real-world bike-mounted LED system.

Inspired by a desire to enhance nighttime cycling visibility with personality and creativity, this simulator allows you to experiment with mathematical patterns and colour dynamics. The 32x32 LED grid (based on Pimoroni's Cosmic Unicorn LED panel) acts as a virtual canvas where you can write real-time equations to generate flowing waves, sparkles, pulses, and more. It's an ideal tool for testing and perfecting animation logic before deploying it to physical LED hardware like the Cosmic Unicorn or similar devices.

Whether you're a hobbyist, an engineer, or just someone who enjoys visual math experiments, this simulator offers a playful and powerful way to bring light-based designs to life.

---

## Features

* **32x32 RGB LED Grid**: Each LED can be individually controlled.
* **Live Equation Editor**: Input mathematical expressions for `r`, `g`, and `b` values using variables `x`, `y`, and `t`.
* **Real-time Animation**: The matrix updates frame-by-frame using your equations.
* **Splash Screen**: Starts with a colorful, animated splash effect.
* **Clipboard Support**: Supports pasting into the input fields (Ubuntu/Wayland compatible).
* **Clear & Submit Buttons**: Easy controls to clear fields or apply changes.

---

## Input Expressions

Use the following variables in your equations:

* `x` = column index (0–31)
* `y` = row index (0–31)
* `t` = time, which increments each frame

Example:

```python
r = 255 if (x + t) % 32 == y else 0
g = 255 if (x + y + t) % 61 == 0 else 0
b = 0
```

---

## Requirements

* Python 3.10+
* `pygame`
* `pyperclip`

Install dependencies:

```bash
python3 -m venv pygame-venv
source pygame-venv/bin/activate
pip install pygame pyperclip
```
If you're using Ubuntu 24.04 or another Wayland-based system and get an error like:

Paste Error: no 'wl-paste'
Install the Wayland clipboard tool with:

`sudo apt install wl-clipboard`

This will enable clipboard paste support for Ctrl+V inside the simulator.
---

## Run It

```bash
python matrix_sim.py
```

---

## Ideas for Equations

* Firefly Flicker:

```python
r = 255 if (int((x * y + t * 50)) % 61) == 0 else 0
g = r
b = 0
```

* Rainbow Wave:

```python
r = (math.sin((x + t) * 0.2) + 1) * 127.5
g = (math.sin((y + t) * 0.2) + 1) * 127.5
b = (math.sin((x + y + t) * 0.1) + 1) * 127.5
```

---

## Future Improvements

* Export to Unicorn HAT or Cosmic Unicorn format

---

