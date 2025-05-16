const express     = require('express');
const serveStatic = require('serve-static');
const yargs       = require('yargs');
const fs          = require('fs');
const bodyParser  = require('body-parser');

const argv = yargs
    .option('port', {
        default: 8080,
        description: 'port to bind http server to',
    })
    .option('address', {
        default: '0.0.0.0',
        description: 'address to bind http server to',
    })
    .option('serve', {
        default: 'static',
        description: 'directory to serve over http',
    })
    .argv;

const port = argv.port;
const address = argv.address;


const app = express();

app.use(function(req, res, next){
    res.header("Cross-Origin-Embedder-Policy", "require-corp");
    res.header("Cross-Origin-Opener-Policy", "same-origin");
    next();
});

app.use(express.text({limit: '50mb'}));
app.use(express.json({limit: '50mb'}));
app.use(serveStatic(argv.serve));
app.use(bodyParser.raw({type: 'application/octet-stream'}));
app.use(bodyParser.json());  // for JSON-based control messages

// === Server state ===
let sentence_id = null;
let PP_RDY = true;      // Tab is ready to start next sentence 
let SIM_START = false;  // Python start signal for each sentence
let SIM_END = false;    // Python end signal for each sentence 
let ALL_DONE = false;   // Python signal for finishing all sentences in the file
let WORKER_ACK = false; // acknowledgement from worker to indicate Prime+Probe started

// === Endpoint: Upload measured trace from browser ===
app.post('/upload_trace', (req, res) => {
    const binaryData = req.body;
    if (!sentence_id) {
        console.error("No sentence_id set before upload.");
        return res.sendStatus(400);
    }

    try {
        fs.writeFileSync(`traces/${sentence_id}.bin`, binaryData);
        PP_RDY = true;
        res.sendStatus(200);
    } catch (error) {
        console.error("Error writing binary data to file: ", error);
        res.sendStatus(500);
    }
});

// === Endpoint: Python checks if trace has been stored ===
app.get('/get_status', (req, res) => {
    res.send({ status: PP_RDY });
});
 
// Note: set_status is not needed because PP_RDY is only set after file write completes

app.post('/set_sentence_id', (req, res) => {
    console.log("set_sentence_id: " + req.body["sentence_id"])
    const data = req.body;
    sentence_id = data["sentence_id"];
    res.sendStatus(200);
})
// === Endpoint: Python sets sentence_id and triggers simulation start ===
app.post('/set_start', (req, res) => {
    console.log("set_start");
    SIM_START = true;
    PP_RDY = false;  
    res.sendStatus(200);
});

// === Endpoint: Browser polls for start signal ===
app.get('/get_start', (req, res) => {
    res.send({ status: SIM_START });
    if (SIM_START) {
        SIM_START = false; // consume the signal after sending
    }
});

// === Endpoint: Python signals the end of the simulation ===
app.post('/set_end', (req, res) => {
    console.log("set_end");
    SIM_END = true;
    res.sendStatus(200);
});

// === Endpoint: Browser polls to check if simulation ended ===
app.get('/get_end', (req, res) => {
    res.send({ status: SIM_END });
    if (SIM_END) {
        SIM_END = false; // consume signal after reading
    }
});

// === Endpoint: Python signals the whole experiment is done ===
app.post('/set_done', (req, res) => {
    console.log("set_done");
    ALL_DONE = true;
    res.sendStatus(200);
});

// === Endpoint: Browser polls for end-of-experiment signal ===
app.get('/get_done', (req, res) => {
    console.log("get_done: " + ALL_DONE);
    res.send({ status: ALL_DONE });
});

// === Endpoint: Browser signals start is received ===
app.post('/set_ack', (req, res) => {
    console.log("set_ack");
    WORKER_ACK = true;
    res.sendStatus(200);
});

// === Endpoint: Python polls for to determine if simulation could start===
app.get('/get_ack', (req, res) => {
    res.send({ status: WORKER_ACK });
    if(WORKER_ACK){
        WORKER_ACK = false;
    }
});

// === Start the server ===
app.listen(8080, () => {
    console.log("Server listening on port 8080");
});



