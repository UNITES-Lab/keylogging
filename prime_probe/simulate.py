import uinput
import time

KEY_MAP = {
    # Letters (lowercase)
    "a": uinput.KEY_A,
    "b": uinput.KEY_B,
    "c": uinput.KEY_C,
    "d": uinput.KEY_D,
    "e": uinput.KEY_E,
    "f": uinput.KEY_F,
    "g": uinput.KEY_G,
    "h": uinput.KEY_H,
    "i": uinput.KEY_I,
    "j": uinput.KEY_J,
    "k": uinput.KEY_K,
    "l": uinput.KEY_L,
    "m": uinput.KEY_M,
    "n": uinput.KEY_N,
    "o": uinput.KEY_O,
    "p": uinput.KEY_P,
    "q": uinput.KEY_Q,
    "r": uinput.KEY_R,
    "s": uinput.KEY_S,
    "t": uinput.KEY_T,
    "u": uinput.KEY_U,
    "v": uinput.KEY_V,
    "w": uinput.KEY_W,
    "x": uinput.KEY_X,
    "y": uinput.KEY_Y,
    "z": uinput.KEY_Z,

    # Digits (top row)
    "1": uinput.KEY_1,
    "2": uinput.KEY_2,
    "3": uinput.KEY_3,
    "4": uinput.KEY_4,
    "5": uinput.KEY_5,
    "6": uinput.KEY_6,
    "7": uinput.KEY_7,
    "8": uinput.KEY_8,
    "9": uinput.KEY_9,
    "0": uinput.KEY_0,

    # Common punctuation on QWERTY
    "`": uinput.KEY_GRAVE,       # Backtick / Grave accent
    "-": uinput.KEY_MINUS,
    "=": uinput.KEY_EQUAL,
    "[": uinput.KEY_LEFTBRACE,
    "]": uinput.KEY_RIGHTBRACE,
    "\\": uinput.KEY_BACKSLASH,
    ";": uinput.KEY_SEMICOLON,
    "'": uinput.KEY_APOSTROPHE,
    ",": uinput.KEY_COMMA,
    ".": uinput.KEY_DOT,
    "/": uinput.KEY_SLASH,

    # Whitespace/Control keys
    "Space": uinput.KEY_SPACE,
    "Tab": uinput.KEY_TAB,
    "Enter": uinput.KEY_ENTER,
    "Backspace": uinput.KEY_BACKSPACE,

    # Modifier keys
    "LeftShift": uinput.KEY_LEFTSHIFT,
    "RightShift": uinput.KEY_RIGHTSHIFT,
    "LeftCtrl": uinput.KEY_LEFTCTRL,
    "RightCtrl": uinput.KEY_RIGHTCTRL,
    "LeftAlt": uinput.KEY_LEFTALT,
    "RightAlt": uinput.KEY_RIGHTALT,
    "CapsLock": uinput.KEY_CAPSLOCK,

    # Navigation keys
    "Esc": uinput.KEY_ESC,
    "Up": uinput.KEY_UP,
    "Down": uinput.KEY_DOWN,
    "Left": uinput.KEY_LEFT,
    "Right": uinput.KEY_RIGHT,
    "Home": uinput.KEY_HOME,
    "End": uinput.KEY_END,
    "PageUp": uinput.KEY_PAGEUP,
    "PageDown": uinput.KEY_PAGEDOWN,
    "Insert": uinput.KEY_INSERT,
    "Delete": uinput.KEY_DELETE,

    # Function keys
    "F1": uinput.KEY_F1,
    "F2": uinput.KEY_F2,
    "F3": uinput.KEY_F3,
    "F4": uinput.KEY_F4,
    "F5": uinput.KEY_F5,
    "F6": uinput.KEY_F6,
    "F7": uinput.KEY_F7,
    "F8": uinput.KEY_F8,
    "F9": uinput.KEY_F9,
    "F10": uinput.KEY_F10,
    "F11": uinput.KEY_F11,
    "F12": uinput.KEY_F12
}

def simulate(keystrokes):
    device = uinput.Device(KEY_MAP.values())

    with open(keystrokes, "r") as f:
        fLines = f.readlines()
        for line1, line2 in zip(fLines, fLines[1:0]):

            line1 = line1.strip()
            line2 = line2.strip()

            parts1 = line1.split()
            parts2 = line2.split()

            if len(parts1) < 2:
                print(f"Skipping malformed line: {line}")
                continue

            #pull values, TODO: needs modification
            pressedChar, pressTime, nextPressTime = parts1[4], parts1[5], parts2[5]

            try:
                interval = float(pressTime - nextPressTime)
            except ValueError:
                print(f"Invalid wait time '{wait_time_str}' in line: {line}")
                continue


            #simulate keystroke, TODO: may need additional formatting
            device.emit_click(KEY_MAP[char])

            #wait to simulate timing, TODO: determine if sleep() gives good enough granularity, replace with time_ns()
            time.sleep(interval/100)

if __name__ == "__main__":
    device = uinput.Device(KEY_MAP.values())
    start_time = time.time()
    while time.time() - start_time < 20:
        device.emit_click(KEY_MAP['a'])
        time.sleep(0.1)
