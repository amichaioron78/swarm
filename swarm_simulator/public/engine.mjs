export function random(seed){let a=seed>>>0; return ()=>{a+=0x6D2B79F5;let t=a;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return((t^t>>>14)>>>0)/4294967296;};}
export class Simulator {
  constructor({members=6,budget=200,seed=42,sharing=true,diversity=true,scenario='marketing'}={}){
    if(!Number.isInteger(members)||members<2||members>20||!Number.isInteger(budget)||budget<50||budget>2000||!Number.isInteger(seed)||seed<0||seed>999999||!['marketing','research','coding'].includes(scenario))throw Error('Invalid simulation settings');
    this.config={members,budget,seed,sharing,diversity,scenario};this.rng=random(seed);this.round=0;this.maxRounds=12;this.done=false;this.history=[];this.events=[];this.notes=[];this.phase='Ready';
    this.agents=Array.from({length:members},(_,i)=>({id:i,name:['Atlas','Nova','Sage','Echo','Orbit','Pixel','Cedar','Lumen','Kite','Sol'][i%10]+(i>=10?' II':''),provider:diversity?['GPT · mock','Claude · mock','DeepSeek · mock'][i%3]:'GPT · mock',team:i%2?'B':'A',active:true,points:0,spent:0,cooldownUntil:null}));
    this.total=members*budget;let team=Math.floor(this.total*.4);this.remaining={A:team,B:team,referee:this.total-2*team};this.initial={...this.remaining};this.scores={A:0,B:0};this.spent=0;this.successes={A:0,B:0};
  }
  log(kind,text){this.events.unshift({round:this.round,kind,text});}
  leave(id){let a=this.agents.find(x=>x.id===id);if(!a||!a.active)return false;a.active=false;a.cooldownUntil=183;this.log('membership',`${a.name} left. Future access revoked; 183-day rejoining cooldown. Committed budget stays pooled.`);return true;}
  charge(bucket,amount){if(!['A','B','referee'].includes(bucket)||!Number.isInteger(amount)||amount<0||amount>this.remaining[bucket])throw Error('Budget limit');this.remaining[bucket]-=amount;this.spent+=amount;}
  step(){
    if(this.done)return false;
    if(!['A','B'].every(t=>this.agents.some(a=>a.active&&a.team===t))){this.done=true;this.phase='Stopped · team unavailable';this.log('system','Both teams need an active member. Start a new room to rebalance.');return false;}
    this.round++;this.phase='Referee verified';
    const reviewCost=Math.max(1,Math.floor(this.initial.referee/this.maxRounds));
    if(this.remaining.referee<reviewCost){this.done=true;this.phase='Referee budget exhausted';return false;}
    this.charge('referee',reviewCost);
    // Both teams work from the same knowledge snapshot; publish after both finish.
    const priorNotes=this.notes.length;
    const pendingNotes=[];
    for(const team of ['A','B']){
      const active=this.agents.filter(a=>a.active&&a.team===team);
      const allocation=Math.min(this.remaining[team],Math.max(1,Math.floor(this.initial[team]/this.maxRounds)));
      this.charge(team,allocation);active.forEach(a=>a.spent+=allocation/active.length);
      // Deliberately synthetic dynamics. Coefficients are assumptions, not empirical claims.
      const spendFactor=allocation/Math.max(1,this.initial[team]/this.maxRounds);
      const coverage=Math.min(.10,active.length*.018);
      const reuse=this.config.sharing?Math.min(.12,priorNotes*.006):0;
      const variety=this.config.diversity?.035:0;
      const overhead=Math.max(0,active.length-4)*.022;
      const base={marketing:.25,research:.4,coding:.35}[this.config.scenario];
      const probability=Math.max(.03,Math.min(.9,(base+coverage+reuse+variety-overhead)*spendFactor));
      const evidence=this.rng();const accepted=evidence<probability;
      const utility=accepted?Math.round((.55+this.rng()*.45)*100):0;
      if(accepted){this.successes[team]++;this.scores[team]+=utility;const contributor=active[Math.floor(this.rng()*active.length)];contributor.points+=utility*.7;active.forEach(a=>a.points+=utility*.3/active.length);this.log('verified',`Team ${team}: ${this.outcomeLabel()} verified by simulated referee. +${utility} points; ${contributor.name} receives discovery credit.`);}
      else this.log('review',`Team ${team}: candidate did not meet the simulated evidence threshold. No points awarded.`);
      if(this.config.sharing){const author=active[(this.round-1)%active.length];pendingNotes.push({round:this.round,team,author:author.name,text:this.noteText(team,accepted)});}
    }
    this.notes.push(...pendingNotes);
    this.history.push({round:this.round,A:this.scores.A,B:this.scores.B,spent:this.spent});
    if(this.round>=this.maxRounds){this.done=true;this.phase='Complete';this.log('system','12 rounds complete. Export the experiment or change the seed to test another run.');}
    return true;
  }
  outcomeLabel(){return {marketing:'qualified client',research:'sourced finding',coding:'passing solution'}[this.config.scenario];}
  noteText(team,accepted){const options={marketing:['Test a narrower company segment.','Compare timing of public requests.','Separate replies from qualified clients.','Record acquisition cost alongside outcomes.'],research:['Cross-check the primary source.','Record uncertainty and date.','Search an independent evidence branch.','Retest the strongest counterexample.'],coding:['Add a hidden edge-case check.','Reproduce the failure in isolation.','Compare the simpler implementation.','Verify the patch against the full contract.']};return `${options[this.config.scenario][(this.round+(team==='A'?0:1))%4]} ${accepted?'Result accepted.':'Current attempt inconclusive.'}`;}
  export(){return {version:'0.2.0',simulationOnly:true,assumptions:'Seeded synthetic probabilities; no real models, clients, token usage or model training.',config:this.config,round:this.round,done:this.done,phase:this.phase,total:this.total,remaining:this.remaining,scores:this.scores,spent:this.spent,agents:this.agents,notes:this.notes,events:this.events,history:this.history};}
}
