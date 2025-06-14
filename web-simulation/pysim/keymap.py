import uinput
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
    "NUM_1": uinput.KEY_NUMERIC_1,
    "NUM_2": uinput.KEY_NUMERIC_2,
    "NUM_3": uinput.KEY_NUMERIC_3,
    "NUM_4": uinput.KEY_NUMERIC_4,
    "NUM_5": uinput.KEY_NUMERIC_5,
    "NUM_6": uinput.KEY_NUMERIC_6,
    "NUM_7": uinput.KEY_NUMERIC_7,
    "NUM_8": uinput.KEY_NUMERIC_8,
    "NUM_9": uinput.KEY_NUMERIC_9,
    "NUM_0": uinput.KEY_NUMERIC_0,

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
    " ": uinput.KEY_SPACE,
    "TAB": uinput.KEY_TAB,
    "Enter": uinput.KEY_ENTER,
    "BKSP": uinput.KEY_BACKSPACE,

    # Modifier keys
    "SHIFT": uinput.KEY_LEFTSHIFT,
    "LeftCtrl": uinput.KEY_LEFTCTRL,
    "RightCtrl": uinput.KEY_RIGHTCTRL,
    "LeftAlt": uinput.KEY_LEFTALT,
    "RightAlt": uinput.KEY_RIGHTALT,
    "CAPS_LOCK": uinput.KEY_CAPSLOCK,
    "ALT": uinput.KEY_LEFTALT, 
    "CTRL": uinput.KEY_LEFTCTRL,
    "WIN": uinput.KEY_ESC,

    # Navigation keys
    "Esc": uinput.KEY_ESC,
    "ESC": uinput.KEY_ESC,
    "Up": uinput.KEY_UP,
    "Down": uinput.KEY_DOWN,
    "Left": uinput.KEY_LEFT,
    "Right": uinput.KEY_RIGHT,
    "Home": uinput.KEY_HOME,
    "End": uinput.KEY_END,
    "PageUp": uinput.KEY_PAGEUP,
    "PageDown": uinput.KEY_PAGEDOWN,
    "PG_UP": uinput.KEY_PAGEUP,
    "PG_DOWN": uinput.KEY_PAGEDOWN,
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
    "F12": uinput.KEY_F12,

    # Uppercase letters
    "A": uinput.KEY_A,
    "B": uinput.KEY_B,
    "C": uinput.KEY_C,
    "D": uinput.KEY_D,
    "E": uinput.KEY_E,
    "F": uinput.KEY_F,
    "G": uinput.KEY_G,
    "H": uinput.KEY_H,
    "I": uinput.KEY_I,
    "J": uinput.KEY_J,
    "K": uinput.KEY_K,
    "L": uinput.KEY_L,
    "M": uinput.KEY_M,
    "N": uinput.KEY_N,
    "O": uinput.KEY_O,
    "P": uinput.KEY_P,
    "Q": uinput.KEY_Q,
    "R": uinput.KEY_R,
    "S": uinput.KEY_S,
    "T": uinput.KEY_T,
    "U": uinput.KEY_U,
    "V": uinput.KEY_V,
    "W": uinput.KEY_W,
    "X": uinput.KEY_X,
    "Y": uinput.KEY_Y,
    "Z": uinput.KEY_Z,

    # Shift-modified symbols
    "!": uinput.KEY_1,
    "@": uinput.KEY_2,
    "#": uinput.KEY_3,
    "$": uinput.KEY_4,
    "%": uinput.KEY_5,
    "^": uinput.KEY_6,
    "&": uinput.KEY_7,
    "NUM_MULT": uinput.KEY_8,
    "(": uinput.KEY_9,
    ")": uinput.KEY_0,
    "~": uinput.KEY_GRAVE,
    "_": uinput.KEY_MINUS,
    "NUM_ADD": uinput.KEY_EQUAL,
    "{": uinput.KEY_LEFTBRACE,
    "}": uinput.KEY_RIGHTBRACE,
    "|": uinput.KEY_BACKSLASH,
    ":": uinput.KEY_SEMICOLON,
    "\"": uinput.KEY_APOSTROPHE,
    "<": uinput.KEY_COMMA,
    ">": uinput.KEY_DOT,
    "?": uinput.KEY_SLASH,

    "ARW_LEFT": uinput.KEY_LEFT,       # Left arrow key
    "ARW_RIGHT": uinput.KEY_RIGHT,     # Right arrow key
    "ARW_UP": uinput.KEY_UP,           # Up arrow key
    "ARW_DOWN": uinput.KEY_DOWN,
    "ARw_DOWN": uinput.KEY_DOWN,
    "HOME": uinput.KEY_HOME,         # Home key
    "END": uinput.KEY_END,           # End key
    "PAGE_UP": uinput.KEY_PAGEUP,    # Page Up key
    "PAGE_DOWN": uinput.KEY_PAGEDOWN,# Page Down key
    "INSERT": uinput.KEY_INSERT,     # Insert key
    "DELETE": uinput.KEY_DELETE, 
    "NUM_LK": uinput.KEY_NUMLOCK,
    "MENU": uinput.KEY_MENU,
    "PAUSE": uinput.KEY_PAUSE,

    # odd special characters
    "ä": uinput.KEY_A,
    "á": uinput.KEY_A,
    "\x13": uinput.KEY_EXIT,
    "\x15": uinput.KEY_EXIT, 
    "´": uinput.KEY_GRAVE,
    "ç": uinput.KEY_C,
    "ø": uinput.KEY_EXIT,
    "ö": uinput.KEY_O,
    "ò": uinput.KEY_O,
    "ñ": uinput.KEY_N,
    "": uinput.KEY_EXIT,
    "¡": uinput.KEY_I,
    "Ä": uinput.KEY_A,
    "à": uinput.KEY_A, 
    "å": uinput.KEY_A,
    "ì": uinput.KEY_I,
    "É": uinput.KEY_E,
    "\x01": uinput.KEY_EXIT,
    "\x19": uinput.KEY_EXIT,
    "é": uinput.KEY_E
}

SHIFT_MAP = {
    # Uppercase letters
    "A": uinput.KEY_A,
    "B": uinput.KEY_B,
    "C": uinput.KEY_C,
    "D": uinput.KEY_D,
    "E": uinput.KEY_E,
    "F": uinput.KEY_F,
    "G": uinput.KEY_G,
    "H": uinput.KEY_H,
    "I": uinput.KEY_I,
    "J": uinput.KEY_J,
    "K": uinput.KEY_K,
    "L": uinput.KEY_L,
    "M": uinput.KEY_M,
    "N": uinput.KEY_N,
    "O": uinput.KEY_O,
    "P": uinput.KEY_P,
    "Q": uinput.KEY_Q,
    "R": uinput.KEY_R,
    "S": uinput.KEY_S,
    "T": uinput.KEY_T,
    "U": uinput.KEY_U,
    "V": uinput.KEY_V,
    "W": uinput.KEY_W,
    "X": uinput.KEY_X,
    "Y": uinput.KEY_Y,
    "Z": uinput.KEY_Z,

    # Shift-modified symbols
    "!": uinput.KEY_1,
    "@": uinput.KEY_2,
    "#": uinput.KEY_3,
    "$": uinput.KEY_4,
    "%": uinput.KEY_5,
    "^": uinput.KEY_6,
    "&": uinput.KEY_7,
    "*": uinput.KEY_8,
    "(": uinput.KEY_9,
    ")": uinput.KEY_0,
    "~": uinput.KEY_GRAVE,
    "_": uinput.KEY_MINUS,
    "+": uinput.KEY_EQUAL,
    "{": uinput.KEY_LEFTBRACE,
    "}": uinput.KEY_RIGHTBRACE,
    "|": uinput.KEY_BACKSLASH,
    ":": uinput.KEY_SEMICOLON,
    "\"": uinput.KEY_APOSTROPHE,
    "<": uinput.KEY_COMMA,
    ">": uinput.KEY_DOT,
    "?": uinput.KEY_SLASH
}
