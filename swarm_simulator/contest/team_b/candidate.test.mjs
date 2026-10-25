import test from 'node:test';
import assert from 'node:assert/strict';
import {Simulator} from './engine.mjs';

test('unknown, inherited and non-string budget keys reject atomically',()=>{
  const s=new Simulator();
  for(const key of ['', 'unknown', '__proto__', 'constructor', 'toString', null, undefined, {}, ['A'], Symbol('A')]){
    const before=structuredClone({remaining:s.remaining,spent:s.spent});
    assert.throws(()=>s.charge(key,1), /Budget limit/);
    assert.deepEqual({remaining:s.remaining,spent:s.spent},before);
  }
});

test('invalid amounts and overspending leave valid buckets untouched',()=>{
  const s=new Simulator();
  for(const bucket of ['A','B','referee']){
    for(const value of [-1, .5, NaN, Infinity, '1', true, s.remaining[bucket]+1]){
      const before=structuredClone({remaining:s.remaining,spent:s.spent});
      assert.throws(()=>s.charge(bucket,value), /Budget limit/);
      assert.deepEqual({remaining:s.remaining,spent:s.spent},before);
    }
    const amount=s.remaining[bucket];
    s.charge(bucket,amount);
    assert.equal(s.remaining[bucket],0);
  }
  assert.equal(s.spent,s.total);
});

test('both teams use only prior-round notes, then share the current round together',()=>{
  const s=new Simulator({members:2,budget:150,diversity:false,sharing:true,scenario:'marketing'});
  // Equal initial probability .268. Old code gives B .274 after A publishes.
  s.rng=()=>.271;
  s.step();
  assert.deepEqual(s.successes,{A:0,B:0});
  assert.equal(s.notes.length,2);
  assert.deepEqual(s.notes.map(n=>n.team),['A','B']);
  // Prior notes are now equally usable, raising both probabilities to .280.
  s.step();
  assert.deepEqual(s.successes,{A:1,B:1});
  assert.equal(s.scores.A,s.scores.B);
  assert.equal(s.notes.length,4);
});

test('current-round notes are not published while either team is processing',()=>{
  const s=new Simulator({members:2,sharing:true});
  const observed=[];
  const original=s.noteText.bind(s);
  s.noteText=(team,accepted)=>{observed.push([team,s.notes.length]);return original(team,accepted);};
  s.step();
  assert.deepEqual(observed,[['A',0],['B',0]]);
  s.step();
  assert.deepEqual(observed.slice(2),[['A',2],['B',2]]);
});

test('disabled sharing never publishes notes; complete runs conserve the budget',()=>{
  for(const sharing of [false,true]){
    const s=new Simulator({members:7,budget:157,sharing});
    while(!s.done)s.step();
    assert.equal(s.notes.length,sharing?24:0);
    assert.equal(s.spent+Object.values(s.remaining).reduce((a,b)=>a+b,0),s.total);
    assert.ok(Object.values(s.remaining).every(v=>Number.isInteger(v)&&v>=0));
    assert.equal(s.history.length,12);
  }
});
