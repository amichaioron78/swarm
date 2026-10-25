import {test} from 'node:test';import assert from 'node:assert/strict';
for(const team of ['team_a','team_b']){
const {Simulator}=await import(`./${team}/engine.mjs`);
test(`${team}: invalid bucket and amount must never mutate ledger`,()=>{for(const bucket of ['missing','__proto__','constructor',null,{},'']){const s=new Simulator(),before=JSON.stringify(s.export());assert.throws(()=>s.charge(bucket,1));assert.equal(JSON.stringify(s.export()),before);}for(const n of [-1,NaN,Infinity,.1,'1']){const s=new Simulator();assert.throws(()=>s.charge('A',n));assert.equal(s.spent,0);}});
test(`${team}: boundary evidence gives no same-round sharing advantage`,()=>{const s=new Simulator({members:2,budget:200});s.rng=()=>.298;s.step();assert.deepEqual(s.successes,{A:0,B:0});assert.equal(s.notes.length,2);});
test(`${team}: nothing published before both reviews`,()=>{const s=new Simulator();let observed=[];s.noteText=()=>{observed.push(s.notes.length);return 'Finding';};s.step();s.step();assert.deepEqual(observed,[0,0,2,2]);});
test(`${team}: ledger and credited points remain conserved across seeds`,()=>{for(let seed=0;seed<50;seed++){const s=new Simulator({seed,members:2+seed%19});while(!s.done)s.step();assert.equal(s.spent+Object.values(s.remaining).reduce((a,b)=>a+b,0),s.total);assert.equal(s.remaining.A,s.remaining.B);assert.ok(Object.values(s.remaining).every(n=>Number.isFinite(n)&&n>=0));assert.ok(Math.abs(s.agents.reduce((a,b)=>a+b.points,0)-s.scores.A-s.scores.B)<1e-6);}});
}
