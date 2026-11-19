/* GTA 6 Setup Builder: runs entirely in the browser from data/products.json + data/config.json */
(function(){
  var BASE=window.GTA6_BASE||"";
  var $=function(id){return document.getElementById(id);};
  var DATA=null,CFG={amazon_tag:""},FX=null;
  var PLAT_NAME={ps5:"PS5",ps5pro:"PS5 Pro",xsx:"Xbox Series X",xss:"Xbox Series S"};
  function esc(s){return String(s).replace(/[&<>"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];});}
  function inr(n){n=Math.round(n);var s=String(Math.abs(n)),r=s;if(s.length>3){var h=s.slice(0,-3),t=s.slice(-3),parts=[];while(h.length>2){parts.unshift(h.slice(-2));h=h.slice(0,-2);}if(h)parts.unshift(h);r=parts.concat([t]).join(",");}return (n<0?"-":"")+"₹"+r;}
  function money(n){if($("cur").value==="USD"&&FX){return "$"+Math.round(n/FX).toLocaleString("en-US")+" (≈"+inr(n)+")";}return inr(n);}
  function link(asin){return "https://www.amazon.in/dp/"+asin+(CFG.amazon_tag?"?tag="+encodeURIComponent(CFG.amazon_tag):"");}
  function slotOf(p){return p.category;}
  function cands(slot,plat,extra){
    return DATA.products.filter(function(p){return p.category===slot&&p.price&&(!p.platforms||p.platforms.indexOf(plat)>=0)&&(!extra||extra(p));})
      .sort(function(a,b){return (a.price-b.price)||(b.rank-a.rank);});
  }
  function bestWithin(list,cap){
    var best=null;
    list.forEach(function(p){if(p.price<=cap&&(!best||p.rank>best.rank||(p.rank===best.rank&&p.price<best.price)))best=p;});
    return best;
  }
  function build(){
    var budget=parseFloat($("budget").value)||0;
    if($("cur").value==="USD"&&FX)budget=budget*FX;
    var plat=$("platform").value,disp=$("display").value,hs=$("headset").value,ex=$("extras").value;
    var owns=$("own-console").checked,needCtl=$("own-controller").checked;
    var slots=[];
    function add(name,slot,w,extra){slots.push({name:name,slot:slot,w:w,list:cands(slot,plat,extra),pick:null});}
    if(disp==="tv"||disp==="best")add("TV","tv",0.5);
    if(disp==="monitor"||disp==="best")add("Monitor","monitor",0.5);
    if(hs!=="none")add("Headset","headset",0.16,function(p){return hs==="any"||(hs==="wireless"?p.wireless:!p.wireless);});
    if(needCtl)add("Controller","controller",0.10);
    if(ex==="storage")add("Storage","storage",0.22);
    if(ex!=="none"){add("HDMI 2.1 cable","cable",0.02);add("Controller charger","charger",0.04);}
    var consoleItem=DATA.products.filter(function(p){return p.category==="console"&&p.platforms.indexOf(plat)>=0;})[0];
    var consoleCost=0,consoleNote="";
    if(!owns){
      if(consoleItem&&consoleItem.price){consoleCost=consoleItem.price;}
      else consoleNote=consoleItem?("Console price could not be confirmed on Amazon.in ("+(consoleItem.price_note||"check price")+"), so it is not counted in your budget."):("No "+PLAT_NAME[plat]+" listing found on Amazon.in, so it is not counted in your budget; buy from Sony or an authorised retailer.");
    }
    var avail=budget-consoleCost,notes=[];
    if(disp==="best"){
      var tvS=slots.filter(function(s){return s.slot==="tv";})[0],moS=slots.filter(function(s){return s.slot==="monitor";})[0];
      var cap=avail*0.5*1.3,tvB=bestWithin(tvS.list,cap),moB=bestWithin(moS.list,cap);
      var keep=(tvB&&(!moB||tvB.rank>=moB.rank))?tvS:moS;
      slots=slots.filter(function(s){return (s.slot!=="tv"&&s.slot!=="monitor")||s===keep;});
    }
    slots.forEach(function(s){s.pick=s.list.length?s.list[0]:null;});
    function total(){return slots.reduce(function(a,s){return a+(s.pick?s.pick.price:0);},0);}
    // if even the cheapest set is over budget, drop optional slots (least important first)
    ["storage","charger","cable","controller","headset"].forEach(function(k){
      if(total()<=avail)return;
      var i=slots.map(function(s){return s.slot;}).indexOf(k);
      if(i>=0&&slots[i].pick){notes.push("Left out "+slots[i].name+" to fit your budget.");slots.splice(i,1);}
    });
    var totalW=slots.reduce(function(a,s){return a+s.w;},0)||1;
    // upgrade passes: first within a per-slot cap, then with whatever is left
    [1.25,99].forEach(function(capMul){
      var changed=true,guard=0;
      while(changed&&guard++<200){
        changed=false;
        slots.forEach(function(s){
          if(!s.pick)return;
          var cap=avail*s.w/totalW*capMul,cur=s.pick,room=avail-total()+cur.price;
          var up=bestWithin(s.list.filter(function(n){return n.rank>cur.rank;}),Math.min(cap,room));
          if(up){s.pick=up;changed=true;}
        });
      }
    });
    var lines=[];
    if(!owns&&consoleItem){lines.push({label:"Console",p:consoleItem});}
    slots.forEach(function(s){lines.push(s.pick?{label:s.name,p:s.pick}:{label:s.name,none:true});});
    var spend=total()+consoleCost;
    render(lines,spend,budget,spend,consoleNote,owns,plat,notes);
    if(window.gtag)gtag("event","builder_run",{site:"gta6-setup",platform:plat,display:disp,budget_band:budget<20000?"<20k":budget<40000?"20-40k":budget<80000?"40-80k":"80k+"});
  }
  function render(lines,spend,budget,floor,consoleNote,owns,plat,notes){
    var h="";
    var left=budget-spend;
    if(spend>budget)h+='<p class="notice warn">Your budget is below the cheapest set of priced items we have ('+esc(money(spend))+'). Showing the cheapest option for each slot; try skipping the headset or choosing a monitor.</p>';
    (notes||[]).forEach(function(n){h+='<p class="notice">'+esc(n)+'</p>';});
    h+='<h2>Your '+esc(PLAT_NAME[plat])+' setup</h2><div class="sumrow"><span>Total of priced items: <strong>'+esc(money(spend))+'</strong></span><span>Budget: '+esc(money(budget))+'</span><span>'+(left>=0?'Left over: '+esc(money(left)):'Over by '+esc(money(-left)))+'</span></div>';
    h+='<div class="plist">';
    lines.forEach(function(l){
      if(l.none){h+='<div class="pl"><div class="pl-h">'+esc(l.label)+'</div><p class="muted">No priced '+esc(l.label.toLowerCase())+' for this platform and filter in our list. <a href="'+BASE+'/products/">Browse products</a>.</p></div>';return;}
      var p=l.p;
      h+='<div class="pl"><div class="pl-h">'+esc(l.label)+'</div><h3>'+esc(p.name)+'</h3><p class="why">'+esc(p.why)+'</p><p>'+
        (p.price?'<span class="price">'+esc(money(p.price))+'</span> <span class="muted small">on Amazon.in, checked '+esc(p.price_checked)+'</span>':'<span class="price none">Check price</span> <span class="muted small">'+esc(p.price_note||"")+'</span>')+
        '</p><p><a class="btn" href="'+esc(link(p.asin))+'" target="_blank" rel="sponsored nofollow noopener" data-tool="'+esc(p.asin)+'">View on Amazon.in</a> <span class="tag-aff">Affiliate link</span></p>'+
        (l.note?'<p class="muted small">'+esc(l.note)+'</p>':'')+'</div>';
    });
    h+='</div>';
    if(consoleNote)h+='<p class="notice">'+esc(consoleNote)+'</p>';
    if(owns)h+='<p class="muted small">Console not included (you said you own one).</p>';
    h+='<p class="muted small">Prices are the figures read from Amazon.in on the date shown and can change. Picks are chosen by a simple rule: cover each slot with the best-ranked product that fits its share of your budget, then spend what is left on upgrades. As an Amazon Associate we earn from qualifying purchases. Guides: <a href="'+BASE+'/guides/">read the buying guides</a>.</p>';
    $("result").innerHTML=h;
    $("result").scrollIntoView({behavior:"smooth",block:"nearest"});
  }
  function init(){
    Promise.all([fetch(BASE+"/data/products.json").then(function(r){return r.json();}),fetch(BASE+"/data/config.json").then(function(r){return r.json();}).catch(function(){return {};})]).then(function(r){
      DATA=r[0];CFG=r[1]||CFG;
      if(CFG.usd_inr){FX=CFG.usd_inr;var o=$("usd-opt");o.disabled=false;o.textContent="USD ($), 1 USD = ₹"+FX+" ("+CFG.usd_inr_date+")";}
      $("bf").addEventListener("submit",function(e){e.preventDefault();build();});
      $("cur").addEventListener("change",function(){var usd=this.value==="USD";$("cur-sym").textContent=usd?"$":"₹";var b=$("budget");b.value=usd?Math.round(parseFloat(b.value)/FX):Math.round(parseFloat(b.value)*FX/500)*500;b.step=usd?10:500;});
      build();
    }).catch(function(){$("result").innerHTML='<p class="notice warn">Could not load product data. Browse <a href="'+BASE+'/products/">all products</a> instead.</p>';});
  }
  init();
})();
