import {mkdir,copyFile} from 'node:fs/promises';
await mkdir('dist',{recursive:true});
for(const file of ['index.html','style.css','app.mjs','engine.mjs','live-test.json']) await copyFile(`public/${file}`,`dist/${file}`);
console.log('Built static simulator in dist/');
