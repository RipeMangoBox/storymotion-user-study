// Shared buffering barrier and bounded drift correction. No simulated watch time.
window.PairedPlayer = class {
 constructor(videos,onCoverage,onBuffer,onError){
  this.videos=videos;this.want=false;this.internal=false;this.dead=false;this.onBuffer=onBuffer;this.onError=onError;this.priming=false;
  const pause=()=>{this.internal=true;videos.forEach(v=>v.pause());this.internal=false;};
  this.pauseInternal=pause;
  videos.forEach(v=>{
   v.addEventListener('waiting',()=>{if(this.want&&!this.dead&&!this.priming){pause();onBuffer(true);}});
   v.addEventListener('canplay',()=>{if(this.want&&!this.priming)this.resume();});
   v.addEventListener('play',()=>{if(!this.internal&&!this.priming){this.want=true;this.resume();}});
   v.addEventListener('pause',()=>{if(!this.internal&&!this.want)this.pause();});
   v.addEventListener('ended',()=>this.pause());
   v.addEventListener('error',()=>{if(!this.dead){this.pause();onError();}});
   v.addEventListener('timeupdate',()=>{
    if(this.dead||this.priming)return;
    let total=0;for(let i=0;i<v.played.length;i++)total+=v.played.end(i)-v.played.start(i);
    onCoverage(videos.indexOf(v),Number.isFinite(v.duration)?Math.min(1,total/v.duration):0);
   });
  });
  this.timer=setInterval(()=>{
   if(!this.want||this.dead||this.priming)return;
   if(videos.some(v=>v.readyState<3)){pause();onBuffer(true);return;}
   if(videos.some(v=>v.paused)){this.resume();return;}
   const delta=videos[1].currentTime-videos[0].currentTime;
   if(Math.abs(delta)>.12)videos[1].currentTime=videos[0].currentTime;
  },200);
 }
 async resume(){
  if(this.dead||!this.want||this.resuming)return;
  if(this.videos.some(v=>v.readyState<3)){this.pauseInternal();this.onBuffer(true);return;}
  this.resuming=true;this.internal=true;
  try{await Promise.all(this.videos.map(v=>v.play()));if(!this.dead)this.onBuffer(false);}catch{this.want=false;this.pauseInternal();}
  finally{this.internal=false;this.resuming=false;}
 }
 async play(reset=false){
  if(this.dead||this.priming)return;
  this.want=true;
  if(reset){this.pauseInternal();this.videos.forEach(v=>v.currentTime=0);}
  if(this.videos.some(v=>v.readyState<3)){
   // Safari may defer preload until a user-gesture play request. Prime both
   // within this click, then reset to the shared position before scoring watch time.
   this.priming=true;this.onBuffer(true);
   const position=reset?0:Math.min(...this.videos.map(v=>v.currentTime||0));
   try{
    await Promise.all(this.videos.map(v=>v.play()));
    this.pauseInternal();
    this.videos.forEach(v=>v.currentTime=position);
   }catch{this.pause();if(!this.dead)this.onError();}
   finally{this.priming=false;}
  }
  this.resume();
 }
 pause(){this.want=false;this.pauseInternal();if(!this.dead)this.onBuffer(false);}
 toggle(){if(this.want)this.pause();else this.play();}
 destroy(){this.dead=true;this.pause();clearInterval(this.timer);}
};
