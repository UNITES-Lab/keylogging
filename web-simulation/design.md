# Browser Simulation System Design Document

## Overview

This system performs coordinated keystroke timing simulations using a combination of Python (for orchestration), a Node.js server (for signaling and trace storage), and browser-based JavaScript/WebAssembly (for Prime+Probe measurement). It simulates typing sentences, records microarchitectural traces, and stores results for further analysis.

## Components

### 1. Python Controller

* Drives the sentence replay logic.
* Interacts with Node.js server via REST API through the requests library for synchronization.
* Initiates the simulation and signals start/end/done.

### 2. Node.js Server

* Acts as the synchronization coordinator with REST API 
* Maintains the synchronization variable state
* Saves traces to local storage
### 3. Web Browser 
#### Web Worker 
* Runs the Prime+Probe logic
* Interact with Node.js with fetch API for synchronization
* Returns probe traces to main thread for handling 
#### Main Thread
* The main thread processes and uploads traces.

## Synchronization Variables (Owned by Node.js)

| Variable    | Type    | Description                                               |
| ----------- | ------- | --------------------------------------------------------- |
| `PP_RDY`    | Boolean | True when ready to receive next start signal.             |
| `SIM_START` | Boolean | True when simulation should begin.                        |
| `SIM_END`   | Boolean | True when current simulation should stop.                 |
| `ALL_DONE`  | Boolean | True when all sentences have been simulated.              |
| `PP_ACK`    | Boolean | True when browser acknowledges receiving data from sender |

## REST API Endpoints

In this section, **Python** refers to the program that simulates the keystrokes and **Tab** refers to the worker thread that monitors the cache state through Prime+Probe. All gets endpoints are implemented as destructive reads to prevent signal reactivation and deadlock situations.

| Endpoint          | User   | Description                                                 |
| ----------------- | ------ | ----------------------------------------------------------- |
| `GET /get_status` | Python | Returns the availability status of the browser tab          |
| `GET /get_start`  | Tab    | Returns the availability of the next simulation sentence    |
| `GET /get_end`    | Tab    | Returns whether the current simulation sentence should end  |
| `GET /get_done`   | Tab    | Returns whether the entire simulation is completed          |
| `GET /get_ack`    | Python | Returns whether the Tab receives the start signal           |
| `POST /set_start` | Python | Set the start signal to request start for next sentence     |
| `POST /set_end`   | Python | Set the end signal to signal the end of current sentence    |
| `POST /set_done`  | Python | Set the done signal to signal the completion of entire file |
| `POST /set_ack`   | Tab    | Set the acknowledgement signal to indicate receiving start  |
| `N/A /set_status` | N/A    | Node.js set the status once binary file is written          |

## System Workflow

### 1. Initialization

* Python loads `test.jsonl` file.
* JS Worker finds the eviction sets 

### 2. For Each Sentence

1. Python polls `/get_status` until `PP_RDY == true`.
2. Python POSTs to `/set_start`.
3. Worker sees `/get_start == true`, begins Prime+Probe, and POSTs to `/set_ack`
4. Python polls `/get_ack` until `PP_ACK == true`
5. Python simulates the sentence.
6. Python POSTs to `/set_end`.
7. Worker checks `/get_end == true` each second, ends loop, and posts `sentenceTrace` to main thread.
8. Main thread processes the trace into hits per millisecond and POSTs it to `/upload_trace`.
9. Server writes file then sets `PP_RDY = true`.
10. Python waits for `PP_RDY` again before next sentence.

### 3. Completion

* After last sentence is completed, Python polls `/get_status` until `PP_RDY == true` to ensure writing of last sentence is done by the server
* Python POSTs `/set_done` to indicate completion of the entire simulation then terminates.
* Worker receives by polling `/get_done` and stops the counter timer

## Output Format

* Each Prime+Probe trace is recorded by the worker thread as an object containing two array of arrays, one each for kbd_keycode and kbd_event
	* array.length represents the amount of seconds that this simulation takes 
	* array\[0\].length shows the amount of Prime+Probe measurements made in this second 
	* each Prime+Probe iteration is stored as a bit, packed into unsigned 8-bit integer arrays with bit shifting
* Main thread processes each trace into hits per millisecond for each of the functions and packed into a single binary file for efficient transmission
	* the first half of the binary file is kbd_keycode and the second half is for kbd_event 
	* hits are stored as unsigned 16-bit integers (uint16)
* Nodejs server stores the received binary file directly into local storage at `traces/{sentence_id}.bin` for further analysis
