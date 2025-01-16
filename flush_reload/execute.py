import time
import json
import os
from pynput.keyboard import Controller
import signal  # handle sigsegv
import argparse
import multiprocessing as mp
import graph

stop_event = mp.Event()

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

def get_address(func: str) -> str:
    output = os.popen(f"sudo cat /proc/kallsyms | grep {func}").read().strip()
    return output


def handle_signal(signum, frame):
    exit(0)


def install_mod():
    print("make clean")
    os.system("make clean")
    print("make")
    os.system("make")
    print("sudo insmod spy.ko")
    print("Please start typing into any window: ")
    os.system("sudo insmod spy.ko")


def start_keystrokes():
    keyboard = Controller()

    print("gvim")
    os.system("gvim")

    print('xdotool search --name "gvim"')
    window_id = os.popen('xdotool search --name "gvim"')
    print(f"xdotool windowactivate {window_id}")
    os.system(f"xdotool windowactivate {window_id}")

    start_time = time.time_ns()
    print(f"keystroke starts: {start_time}")

You said:
can you provide a background paragraph for keystroke timings and their key metrics such as IKI, Key hold time, rollover ratio? write in a academic tone
ChatGPT said:
ChatGPT

Keystroke dynamics is a behavioral biometric modality that analyzes typing patterns to identify or authenticate individuals. It relies on the temporal characteristics of keystroke events, providing unique insights into the rhythm and consistency of a user's typing. Key metrics commonly employed in keystroke dynamics include Inter-Key Interval (IKI), Key Hold Time, and the Rollover Ratio. IKI, defined as the time elapsed between releasing one key and pressing the next, captures the fluidity of transitions between consecutive keys. Key Hold Time, on the other hand, measures the duration a key is held down, reflecting the user's typing force and speed. The Rollover Ratio assesses the degree of overlapping keystrokes, offering a measure of typing efficiency and coordination. These metrics, individually or in combination, form the basis for constructing robust typing profiles that can be used for applications ranging from user authentication to behavioral studies.
You said:
how are meta quest 2's controllers connected? what protocol do they use
ChatGPT said:
ChatGPT

The Meta Quest 2 controllers connect to the headset using Bluetooth Low Energy (BLE) technology. BLE is a power-efficient wireless communication protocol commonly used in devices requiring intermittent data transmission, such as gaming controllers and wearable devices.

In the case of the Meta Quest 2, BLE ensures low-latency communication between the controllers and the headset, enabling responsive tracking and input handling during gameplay. The controllers also rely on embedded infrared (IR) LEDs and onboard sensors to provide precise positional tracking, which is synchronized with the headset's inside-out tracking system for immersive virtual reality experiences.
You said:
what are bigrams in keystroke dynamics
ChatGPT said:
ChatGPT

In keystroke dynamics, bigrams refer to pairs of consecutive keys typed by a user, and they are analyzed to study typing patterns and behaviors. Bigrams capture the temporal relationship between two sequential keystrokes and are a fundamental unit of analysis in this domain. Metrics derived from bigrams often include:

    Inter-Key Interval (IKI): The time elapsed between releasing the first key and pressing the second key in a bigram. This measures the transition speed between two consecutive keys.

    Key Hold Time for Each Key: The duration each key in the bigram is held down, which provides insight into the user's typing rhythm and pressure patterns.

    Flight Time: A broader metric that includes both IKI and the hold time of the first key, capturing the overall transition from one key to the next.

Bigrams are crucial in creating a user's unique typing profile, as they reflect their natural rhythm, speed, and consistency. By analyzing patterns in bigram timings, systems can differentiate between users or detect anomalies, making bigrams valuable in applications such as user authentication, behavior analysis, and security systems.
You said:
what algorithms or models are useful for filtering out if there are duplicate time stamps even though the ground truth happened once
2/2
ChatGPT said:
ChatGPT

Filtering out duplicate timestamps in time-series data, particularly when ground truth events occur only once, requires algorithms or models that can detect and resolve anomalies while preserving the integrity of the data. Here are some approaches and models that can be applied:
1. Statistical Filtering

    Median Filtering: Replaces each timestamp with the median value of a sliding window to eliminate outliers or duplicates.
    Moving Average: Smoothens the data by averaging timestamps over a sliding window, potentially reducing the effect of duplicates.

2. Outlier Detection Algorithms

    Z-Score Analysis: Identifies duplicates by calculating how far a timestamp deviates from the mean in standard deviation units.
    Interquartile Range (IQR): Flags timestamps that fall outside the acceptable range, determined by the first and third quartiles.

3. Clustering-Based Approaches

    DBSCAN (Density-Based Spatial Clustering): Groups timestamps based on proximity, allowing detection of clusters caused by duplicate events.
    K-Means Clustering: Assigns timestamps to clusters and helps identify anomalies in timing patterns.

4. Machine Learning Models

    Supervised Models: If labeled data is available, classifiers like Random Forest or Support Vector Machines (SVM) can be trained to distinguish between valid and duplicate timestamps.
    Anomaly Detection Models: Algorithms like Isolation Forest or One-Class SVM can identify unusual duplicate patterns in the data.

5. Time-Series Models

    ARIMA (AutoRegressive Integrated Moving Average): Can model the expected pattern of events and flag duplicates as deviations from the model's predictions.
    LSTM (Long Short-Term Memory): A neural network model capable of learning temporal dependencies in sequential data, useful for identifying duplicates based on learned patterns.

6. Custom Heuristics

    Threshold-Based Deduplication: If two timestamps are within a specific threshold of each other, one is discarded.
    Unique Event Constraints: Implement logic to enforce the occurrence of a single event per interval, rejecting duplicates.

7. Signal Processing Techniques

    Peak Detection Algorithms: Identify the primary occurrence of an event and suppress duplicate peaks.
    Fourier Transform Filtering: Use frequency-domain analysis to remove spurious duplicates that do not match the expected signal characteristics.

The choice of approach depends on the nature of the data, the level of noise, and the specific application. Often, combining multiple methods (e.g., statistical filters followed by a machine learning model) provides the most robust solution.
You said:
What ML models would you use if you had to filter out false time series observations from real ones. the context of the input data is cache hits for js function call pairs on average 100ms apart with granularity of miliseconds but each ground truth generates several false observations with an error upto 20ms from the ground truth
ChatGPT said:
ChatGPT

To filter out false observations from real ones in time-series data with characteristics like cache hits for JavaScript function call pairs, the goal is to distinguish the true events from noise while preserving temporal integrity. Given the context of the problem, the following machine learning models and approaches can be particularly effective:
1. Supervised Learning Models

If labeled data (true vs. false observations) is available:

    Gradient Boosted Trees (e.g., XGBoost, LightGBM):
    These models can learn the patterns of real vs. false observations based on features like time differences, error ranges, or derived metrics (e.g., local density of events).

    Random Forest:
    Useful for capturing non-linear relationships between features while being robust to overfitting, especially with noisy data.

    Logistic Regression:
    If the decision boundary is simple (e.g., based on error tolerance or timing consistency), logistic regression can effectively classify true vs. false observations.

2. Time-Series Anomaly Detection Models

If labeled data is unavailable or if the problem is framed as detecting anomalies:

    Isolation Forest:
    This algorithm identifies anomalies by isolating points in the feature space. False observations, which deviate in timing patterns, can be flagged.

    One-Class SVM:
    Trains on "normal" data (true observations) and detects anomalies (false observations) as deviations from the learned distribution.

    Autoencoders:
    A neural network-based unsupervised approach that reconstructs the input data. True observations will have low reconstruction error, while false ones will have higher errors.

3. Temporal Sequence Models

To exploit the sequential nature of the data:

    Recurrent Neural Networks (RNNs):
    Models like LSTMs or GRUs can learn temporal dependencies and detect out-of-sequence or irregular timing patterns indicative of false observations.

    Temporal Convolutional Networks (TCNs):
    These can model timing intervals effectively and identify anomalies in timing sequences.

4. Clustering Models

To group observations and identify true events as dense clusters:

    DBSCAN (Density-Based Spatial Clustering):
    Effective for detecting clusters of true observations, with false observations being treated as noise due to their sparse distribution.

    K-Means:
    Groups data into clusters, with features like timing intervals or error bounds used for clustering.

5. Statistical Approaches and Heuristics

Even without ML, statistical or heuristic-based methods can be combined with ML models for feature engineering or pre-filtering:

    Gaussian Mixture Models (GMMs):
    Fit a probabilistic model to timing distributions and classify observations based on their likelihood under the model.

    Threshold-Based Filtering:
    A simple approach to pre-filter observations by rejecting those beyond a 20ms threshold from expected intervals.

Feature Engineering for Models

For any of these models, feature engineering is critical. Potential features include:

    Time Difference (Δt): Time interval between consecutive observations.
    Error Bounds: Absolute difference from the expected timing (e.g., 100ms).
    Local Density: Number of observations within a ±20ms window.
    Sequence Features: Patterns in timing intervals over a sliding window.

Recommended Approach

    If labeled data is available: Start with Gradient Boosted Trees (e.g., XGBoost) due to their interpretability and effectiveness with tabular data.
    If unsupervised: Use Isolation Forest or DBSCAN for anomaly detection.
    If temporal dependencies are complex: Use LSTM or TCN models.

By combining these approaches with robust feature engineering and evaluation on validation data, you can achieve high accuracy in filtering out false observations.
You said:
explain 2 and 3 more
ChatGPT said:
ChatGPT

Here’s a deeper explanation of 2 (Time-Series Anomaly Detection Models) and 3 (Temporal Sequence Models):
2. Time-Series Anomaly Detection Models

These models are particularly suited when you want to identify outliers (false observations) without requiring strong assumptions about the data's structure. They work well when the true events (ground truth) follow consistent patterns, and false observations deviate from those patterns.
Isolation Forest

    How it works:
    Isolation Forest isolates data points by creating random partitions in the feature space. True observations, being more similar to each other (e.g., tightly clustered in timing), require more partitions to isolate. False observations, which are sparse and deviate from the true timing pattern, are isolated with fewer partitions.
    Why it's useful here:
        Can detect sparse, noisy false observations.
        Doesn't assume normal distribution in the data.

One-Class SVM (Support Vector Machine)

    How it works:
    One-Class SVM learns the boundary of the "normal" data (true observations) in the feature space. Any data point outside this learned boundary is classified as an anomaly.
    Why it's useful here:
        Ideal for situations where only true observations (normal data) are available for training.
        Works well in high-dimensional spaces if features like timing, local density, and error bounds are engineered effectively.

Autoencoders (Neural Networks for Anomaly Detection)

    How it works:
    An autoencoder learns to compress and reconstruct input data. True observations (ground truth events) will have low reconstruction errors because they match the learned patterns. False observations will have higher reconstruction errors because they deviate from these patterns.
    Why it's useful here:
        Works well when timing patterns are complex and non-linear.
        Can adapt to temporal features derived from the time series.

3. Temporal Sequence Models

These models are designed to capture dependencies and patterns in sequential data. They are useful when the order and timing of events carry important information (e.g., the 100ms interval between true events).
Recurrent Neural Networks (RNNs)

    How it works:
    RNNs process sequences by maintaining a "memory" of previous inputs, allowing them to model dependencies across time steps. Variants like LSTMs (Long Short-Term Memory) and GRUs (Gated Recurrent Units) are particularly effective for learning long-term dependencies.
    Why it's useful here:
        Can detect subtle timing anomalies, such as irregularities in intervals between events.
        Learns temporal patterns directly from raw data, without extensive feature engineering.

Temporal Convolutional Networks (TCNs)

    How it works:
    TCNs use convolutional layers designed for sequential data, processing multiple time steps in parallel to detect patterns. Unlike RNNs, they don’t rely on sequential processing, making them faster and easier to train.
    Why it's useful here:
        Better suited for time series with consistent patterns (e.g., 100ms intervals).
        Handles long-range dependencies more efficiently than RNNs.

When to Use Each

    Anomaly Detection Models (Isolation Forest, One-Class SVM):
    Use these if you primarily need to identify deviations (false observations) without complex temporal dependencies.

    Sequence Models (LSTMs, TCNs):
    Use these if the data has strong sequential or contextual dependencies, such as patterns over time windows (e.g., 100ms spacing with occasional noise).

By combining these methods with appropriate feature engineering (e.g., calculating time intervals, local densities), you can create robust systems to filter out false observations effectively.
You said:
Generate fifteen sentences using a diverse set of QWERT bigrams in english one example is: "I was sad as Polk place was closed"
ChatGPT said:
ChatGPT

Here are fifteen sentences using a diverse set of QWERTY bigrams:

    "He asked if Quinn knew about the plan."
    "Jill quickly typed the report on her desk."
    "Tom baked an apple pie for his guests."
    "I found the old vase in the attic yesterday."
    "She drove past the quiet lake at sunset."
    "Frank kept his notes in a small black book."
    "The queen's loyal guard stood by her side."
    "Can you help me find the lost keys, please?"
    "The quick brown fox jumps over the lazy dog."
    "Liam fixed the broken pipe with his tools."
    "Zara painted a vivid mural on the brick wall."
    "We had sushi and miso soup for dinner."
    "Her scarf was made of soft, bright silk."
    "The train arrived at the station on time."
    "Greg packed his bags and left for the airport."

These sentences cover a wide range of bigrams while maintaining grammatical correctness and contextual relevance.
You said:
write a bash code that will use xdotool to replay a keystroke from a csv data with regards to the inputted key and the wait time between keystrokes
ChatGPT

Below is a simple Bash script that reads keystrokes and wait times from a CSV file and uses xdotool to replay them. The CSV file should have two columns: the key (e.g., “a”, “Return”, “Shift_L+a” for uppercase letters, etc.) and the wait time in seconds (e.g., 0.2 or 1), separated by commas.
Example CSV File (keystrokes.csv)

a,0.5
b,0.5
Return,1
c,0.2
d,0.8

Bash Script (replay_keystrokes.sh)

#!/usr/bin/env bash

# Usage: ./replay_keystrokes.sh keystrokes.csv

if [ $# -lt 1 ]; then
  echo "Usage: $0 input.csv"
  exit 1
fi

INPUT_CSV="$1"

# Read each line from the CSV: first column is key, second is wait time
while IFS=, read -r KEY WAIT_TIME; do
  # If the line is empty or a comment, skip it
  if [[ -z "$KEY" || "$KEY" =~ ^# ]]; then
    continue
  fi
  
  # Replay the keystroke using xdotool
  xdotool key "$KEY"
  
  # Pause for the specified duration (in seconds) before the next keystroke
  sleep "$WAIT_TIME"
done < "$INPUT_CSV"

How It Works

    Command-Line Argument: The script expects the name (or path) of a CSV file containing the keystrokes.
    CSV Format: Each line in the CSV consists of two values separated by a comma:
        KEY: The name of the key or key combination you want to press (e.g., a, Return, ctrl+c, Shift_L+a).
        WAIT_TIME: The number of seconds to wait after pressing the key.
    Reading & Replaying:
        The script reads each row, separates it into KEY and WAIT_TIME.
        Calls xdotool key "$KEY" to send the keystroke to the active window.
        Pauses for WAIT_TIME seconds using sleep before moving on to the next line.
    Skipping Comments/Empty Lines: If the line is empty or starts with #, the script ignores it.

With this setup, you can record sequences of keystrokes (along with timing data) in a CSV file and replay them automatically using xdotool.
You said:
try using with python-uinput instead of xdotool, the data format is now a space-seperated txt file instead of csv
ChatGPT

Below is an example Python script that reads a space-separated text file (containing a key and a wait time on each line) and uses python-uinput to replay these keystrokes. Please note:

    Root privileges are generally required to create and interact with a uinput device.
    The key map shown here is minimal—you can extend it to include additional keys (e.g., SHIFT, CTRL, etc.) based on your needs.
    The file format is assumed to have lines in the form: \text{KEY_IDENTIFIER} \ \ \text{WAIT_TIME_IN_SECONDS} For example:
    a 0.5b 0.5Enter 1.0
    a 0.5b 0.5Enter 1.0 Lines starting with # or that are empty are skipped.

Example Keystrokes File (keystrokes.txt)

a 0.5
b 0.5
Enter 1.0
a 0.2
b 0.2

# This is a comment line and will be skipped
c 0.5

Python Script (replay_keystrokes.py)

#!/usr/bin/env python3
"""
Replay keystrokes from a space-separated file using python-uinput.

Usage:
  sudo python3 replay_keystrokes.py keystrokes.txt
"""

import uinput
import time
import sys

# Extend or modify this dictionary as needed for your application
KEY_MAP = {
    "a": uinput.KEY_A,
    "b": uinput.KEY_B,
    "c": uinput.KEY_C,
    "d": uinput.KEY_D,
    "Enter": uinput.KEY_ENTER,
    # Add more keys as needed, for example:
    # "Shift": uinput.KEY_LEFTSHIFT,
    # "Esc": uinput.KEY_ESC,
    # "Space": uinput.KEY_SPACE,
    # "Tab": uinput.KEY_TAB,
    # "Up": uinput.KEY_UP,
    # "Down": uinput.KEY_DOWN,
    # "Left": uinput.KEY_LEFT,
    # "Right": uinput.KEY_RIGHT,
}

def main(input_file):
    # Collect all keys we might use from the dictionary
    device = uinput.Device(KEY_MAP.values())

    with open(input_file, "r") as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines or comment lines
            if not line or line.startswith("#"):
                continue

            parts = line.split()
            if len(parts) < 2:
                print(f"Skipping malformed line: {line}")
                continue

            key_string, wait_time_str = parts[0], parts[1]

            # Convert wait time to float
            try:
                wait_time = float(wait_time_str)
            except ValueError:
                print(f"Invalid wait time '{wait_time_str}' in line: {line}")
                continue

            # Lookup the uinput key object
            if key_string not in KEY_MAP:
                print(f"Key '{key_string}' not recognized. Please add it to KEY_MAP.")
                continue

            # Emit the key click (key down + key up)
            device.emit_click(KEY_MAP[key_string])

            # Wait before moving to the next keystroke
            time.sleep(wait_time)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: sudo python3 replay_keystrokes.py <keystrokes.txt>")
        sys.exit(1)

    input_file = sys.argv[1]
    main(input_file)

Explanation

    Imports and Setup
        import uinput, import time, import sys are the main modules required.
        You must run this script with root privileges (e.g., using sudo) because uinput requires access to system input events.

    Key Map
        A dictionary named KEY_MAP maps simple string identifiers (e.g., "a") to their corresponding uinput constants (e.g., uinput.KEY_A).
        Extend this dictionary for any additional keys you need.

    Creating the Device
        device = uinput.Device(KEY_MAP.values()) creates a virtual input device that can emit these keys.

    Reading the Input File
        The script expects a space-separated file (keystrokes.txt) where each line contains a key identifier and a wait time in seconds.
        Lines starting with # or empty lines are ignored.

    Replaying Keystrokes
        For each valid line, the script:
            Splits the line into key_string and wait_time_str.
            Converts the wait time to a float (e.g., 0.5 or 1.0).
            Looks up the corresponding uinput constant in KEY_MAP.
            Emits a key click using device.emit_click(...), which performs a key press and release.
            Sleeps for the specified duration before moving to the next line.

Using this script, you can automate keystroke replays programmatically, which is especially helpful for testing, demo recording, or automation scenarios on Linux systems. Make sure you install python-uinput (for example, sudo apt-get install python3-uinput on Ubuntu) before running the script.
You said:
expand the key map to include all english alphabet and keys on a UNICODE QWERTY layout
ChatGPT

Below is an expanded KEY_MAP covering most keys on a standard QWERTY keyboard, including all English alphabet letters (lowercase), digits, function keys, and common punctuation. This map is intended for use with python-uinput in a Linux environment. It can be integrated into the previous Python script example (using uinput.Device(...)) to simulate keyboard input programmatically. Note that to type uppercase letters or symbols that require the Shift key (e.g., !, @), you need to emit both Shift and the corresponding key (see “Typing Shift-Modified Keys” below).
Expanded KEY_MAP

import uinput

#key map for uinput, TODO: how to do shift combos
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
        fLines = readlines(f)
        for line1, line2 in zip(fLines, fLines[1:0]):

            line1 = line1.strip()
            line2 = line2.strip()

            parts1 = line1.split()
            parts2 = line2.split()

            if len(parts) < 2:
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

            #wait to simulate timing, TODO: determine if sleep() gives good enough granularity
            time.sleep(interval/100)



    # Modify this code to simulate the keystroke patterns you want to automate
    # while not stop_event.is_set():
    #     keyboard.press("a")
    #     keypresses.append({"key-char": "a", "time": time.time_ns()})
    #     time.sleep(0.05)  # hold key for 100 ms
    #     keyboard.release("a")
    #     keyreleases.append({"key-char": "a", "time": time.time_ns()})
    #     time.sleep(0.2)  # wait for 200 ms before next press


def uninstall_mod():
    print("sudo rmmod spy")
    os.system("sudo rmmod spy")


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument(
    #     "--real", action="store_true", default=False, help="real keystroke mode"
    # )
    # args = parser.parse_args()
    # if not args.real:
    #     with mp.Manager() as manager:
    #         keypresses = manager.list()
    #         keyreleases = manager.list()
    #         p = mp.Process(target=install_mod)
    #         q = mp.Process(target=start_keystrokes)
    #         p.start()
    #         q.start()
    #         p.join()
    #         stop_event.set()
    #         q.join()
    #
    #         uninstall_mod()
    #
    #         # Capture dmesg output
    #         output = os.popen("sudo dmesg -c").read().strip().split("\n")
    #         data = graph.sort_output(output)
    #
    #         """
    #         Because simulated keys from pynput does not trigger keylogger, we will need to log the inputs by ourselves
    #         """
    #
    #         data["keypresses"] = [
    #             {
    #                 "key-char": key["key-char"],
    #                 "keystroke-time": key["time"] - data["start_time"],
    #             }
    #             for key in keypresses
    #             if key["time"] > data["start_time"]
    #         ]
    #
    #         data["keyreleases"] = [
    #             {
    #                 "key-char": key["key-char"],
    #                 "keystroke-time": key["time"] - data["start_time"],
    #             }
    #             for key in keyreleases
    #             if key["time"] > data["start_time"]
    #         ]
    #
    #         graph.write_output(data)
    #         graph.graph_keystrokes(data)
    # else:
    install_mod()
    uninstall_mod()
    output = os.popen("sudo dmesg -c").read().strip().split("\n")
    data = graph.sort_output(output)
    graph.write_output(data)
    graph.graph_keystrokes(data)
