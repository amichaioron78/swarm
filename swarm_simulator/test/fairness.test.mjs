import test from 'node:test';
import assert from 'node:assert/strict';
import {Simulator} from '../public/engine.mjs';

test('unknown and inherited bucket names cannot mutate the ledger',()=>{
  const s=new Simulator();
  const before=structuredClone(s.export());
  for(const bucket of ['unknown','__proto__','constructor','toString',null,undefined,{},['A']]){
    assert.throws(()=>s.charge(bucket,1),/Budget limit/);
    assert.deepEqual(s.export(),before);
  }
});

test('invalid amounts and overspending leave all balances unchanged',()=>{
  const s=new Simulator();
  const before=structuredClone(s.export());
  for(const amount of [-1,0.5,NaN,Infinity,'1',true,s.remaining.A+1]){
    assert.throws(()=>s.charge('A',amount),/Budget limit/);
    assert.deepEqual(s.export(),before);
  }
});

test('exact remaining balance can be spent and total remains conserved',()=>{
  const s=new Simulator();
  for(const bucket of ['A','B','referee']){
    s.charge(bucket,s.remaining[bucket]);
    assert.equal(s.spent+Object.values(s.remaining).reduce((a,b)=>a+b,0),s.total);
    assert.ok(Object.values(s.remaining).every(n=>Number.isFinite(n)&&n>=0));
  }
  assert.equal(s.spent,s.total);
});

test('both teams use the same pre-round notes at a threshold that previously favored B',()=>{
  // Six members => three workers/team; base .25 + coverage .054 + diversity .035=.339.
  // .342 fails both teams against the old snapshot but passed B after A added .006.
  const s=new Simulator({members:6,budget:200,sharing:true,scenario:'marketing'});
  s.rng=()=>.342;
  s.step();
  assert.deepEqual(s.successes,{A:0,B:0});
  assert.equal(s.notes.length,2);
  // Prior round's two published notes now give both teams the same .012 benefit.
  s.step();
  assert.deepEqual(s.successes,{A:1,B:1});
  assert.equal(s.notes.length,4);
});

test('notes are published only after both candidates are evaluated',()=>{
  const s=new Simulator({members:2,sharing:true});
  const observed=[];
  s.rng=()=>{observed.push(s.notes.length);return .99;};
  s.step();
  assert.deepEqual(observed,[0,0]);
  assert.equal(s.notes.length,2);
});

test('sharing disabled publishes no notes; repeated seed gives same outcome',()=>{
  const a=new Simulator({seed:73,sharing:false});
  const b=new Simulator({seed:73,sharing:false});
  while(!a.done)a.step();
  while(!b.done)b.step();
  assert.deepEqual(a.export(),b.export());
  assert.deepEqual(a.notes,[]);
  assert.equal(a.spent+Object.values(a.remaining).reduce((x,y)=>x+y,0),a.total);
});
