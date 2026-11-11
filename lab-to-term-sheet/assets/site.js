// Shared: reading progress bar
(function(){
  var bar=document.querySelector('.progress');
  if(!bar) return;
  function upd(){
    var h=document.documentElement;
    var max=h.scrollHeight-h.clientHeight;
    bar.style.width=(max>0?(h.scrollTop/max)*100:0)+'%';
  }
  window.addEventListener('scroll',upd,{passive:true});upd();
})();
// Shared: copy helper with inline feedback
window.copyText=function(text,btn){
  var done=function(msg){var o=btn.textContent;btn.textContent=msg;setTimeout(function(){btn.textContent=o},1800)};
  try{navigator.clipboard.writeText(text).then(function(){done('Copied')},function(){done('Select & copy below')})}
  catch(e){done('Select & copy below')}
};
