import {mkdir,copyFile,readdir} from 'node:fs/promises';
await mkdir('vendor',{recursive:true});
for(const name of await readdir('node_modules/onnxruntime-web/dist')){
 if(['ort.min.js','ort-wasm-simd-threaded.mjs','ort-wasm-simd-threaded.wasm','ort-wasm-simd-threaded.jsep.mjs','ort-wasm-simd-threaded.jsep.wasm','ort-wasm-simd-threaded.jspi.mjs','ort-wasm-simd-threaded.jspi.wasm'].includes(name)) await copyFile('node_modules/onnxruntime-web/dist/'+name,'vendor/'+name);
}
console.log('Local runtime ready; serve project root: python -m http.server 8000');
