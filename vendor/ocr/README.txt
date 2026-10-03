tesseract.js 5.1.1, tesseract.js-core 5.1.1 (Apache-2.0) and the English LSTM model 4.0.0_best_int from @tesseract.js-data/eng 1.0.0 (Apache-2.0).
Shipped as eng-traineddata-gz.wasm (gzipped model; the name is only so artifacts serve it).
Used by index.html to read numbers from IKEA measurement drawings in the browser.
Patched: worker.min.js maps language objects to their .code (not .data) when initialising, fixing a tesseract.js 5.1.1 bug with in-memory language data.
