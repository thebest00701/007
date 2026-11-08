import React,{useEffect,useRef,useState} from 'react';
import * as THREE from 'three';
import {ArrowDown,ArrowUpRight,Plus,Minus,X,ShoppingBag,Instagram,Move3D} from 'lucide-react';
const products=[
{id:1,name:'Slow Roast',type:'Whole bean · 250 g',price:18,note:'Caramel · Brown sugar · Roasted almond',tag:'HOUSE FAVOURITE',img:'https://images.unsplash.com/photo-1559525839-b184a4d698c7?auto=format&fit=crop&w=900&q=85'},
{id:2,name:'Morning Glory',type:'Whole bean · 250 g',price:21,note:'Orange zest · Honey · Milk chocolate',tag:'BRIGHT & JUICY',img:'https://images.unsplash.com/photo-1442512595331-e89e73853f31?auto=format&fit=crop&w=900&q=85'},
{id:3,name:'After Hours',type:'Whole bean · 250 g',price:19,note:'Dark cocoa · Cherry · Hazelnut',tag:'FOR SLOW DAYS',img:'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=85'},
{id:4,name:'Decaf Club',type:'Whole bean · 250 g',price:20,note:'Toffee · Red apple · Soft spice',tag:'ALL THE FLAVOUR',img:'https://images.unsplash.com/photo-1511537190424-bbbab87ac5eb?auto=format&fit=crop&w=900&q=85'}];
function CoffeeScene(){
 const mount=useRef(null);
 useEffect(()=>{
  const host=mount.current;if(!host)return;
  const scene=new THREE.Scene();scene.background=null;
  const camera=new THREE.PerspectiveCamera(34,1,.1,100);camera.position.set(0,1.25,8.7);
  const renderer=new THREE.WebGLRenderer({alpha:true,antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.35;host.appendChild(renderer.domElement);
  scene.add(new THREE.HemisphereLight(0xffe8cb,0x28140d,2.1));
  const key=new THREE.DirectionalLight(0xffd3a1,4.2);key.position.set(-3,6,5);key.castShadow=true;scene.add(key);
  const rim=new THREE.PointLight(0xc66d39,42,15);rim.position.set(4,2,1);scene.add(rim);
  const group=new THREE.Group();scene.add(group);
  const mat=(color,roughness=.45,metalness=0)=>new THREE.MeshStandardMaterial({color,roughness,metalness});
  const cream=mat('#e8ddc9',.28),dark=mat('#26140e',.34),coffee=mat('#4b2415',.2),gold=mat('#bd8755',.27,.55),paper=mat('#d2c0a4',.8);
  const floor=new THREE.Mesh(new THREE.CircleGeometry(5,64),mat('#4a281a',.7));floor.rotation.x=-Math.PI/2;floor.position.y=-1.32;floor.receiveShadow=true;group.add(floor);
  // sculpted takeaway cup
  const cup=new THREE.Group();cup.position.set(.95,-.3,.25);cup.rotation.z=-.09;group.add(cup);
  const cupGeo=new THREE.CylinderGeometry(.67,.49,1.42,64,1,true);const cupBody=new THREE.Mesh(cupGeo,cream);cupBody.castShadow=true;cupBody.receiveShadow=true;cup.add(cupBody);
  const coffeeTop=new THREE.Mesh(new THREE.CircleGeometry(.64,64),coffee);coffeeTop.rotation.x=-Math.PI/2;coffeeTop.position.y=.72;cup.add(coffeeTop);
  const lid=new THREE.Mesh(new THREE.CylinderGeometry(.7,.68,.12,64),dark);lid.position.y=.77;lid.castShadow=true;cup.add(lid);
  const lidLip=new THREE.Mesh(new THREE.TorusGeometry(.68,.045,12,64),gold);lidLip.rotation.x=Math.PI/2;lidLip.position.y=.83;cup.add(lidLip);
  const logo=new THREE.Mesh(new THREE.PlaneGeometry(.82,.28),mat('#382015',.8));logo.position.set(0,.05,.51);cup.add(logo);
  // coffee pouch
  const pouch=new THREE.Group();pouch.position.set(-1.25,-.13,-.2);pouch.rotation.z=.12;group.add(pouch);
  const bag=new THREE.Mesh(new THREE.BoxGeometry(1.35,2.25,.55,1,1,1),paper);bag.castShadow=true;bag.receiveShadow=true;pouch.add(bag);
  const seal=new THREE.Mesh(new THREE.BoxGeometry(1.36,.12,.57),gold);seal.position.y=1.08;pouch.add(seal);
  const label=new THREE.Mesh(new THREE.PlaneGeometry(1.05,1.05),cream);label.position.set(0,.05,.286);pouch.add(label);
  const beanMat=mat('#3a1a10',.25);
  const beans=[];
  for(let i=0;i<28;i++){const b=new THREE.Mesh(new THREE.SphereGeometry(.12,16,12),beanMat);b.scale.set(1,.58,.72);b.position.set((Math.random()-.5)*5,(Math.random()-.5)*3.4,(Math.random()-.5)*2-1);b.rotation.set(Math.random()*3,Math.random()*3,Math.random()*3);b.castShadow=true;scene.add(b);beans.push({mesh:b,base:b.position.clone(),phase:Math.random()*6});}
  const plate=new THREE.Mesh(new THREE.CylinderGeometry(1.08,1.12,.12,64),cream);plate.position.set(.95,-1.08,.2);plate.castShadow=true;cup.add(plate);
  const shadow=new THREE.Mesh(new THREE.CircleGeometry(2.8,64),new THREE.MeshBasicMaterial({color:'#140b07',transparent:true,opacity:.22}));shadow.rotation.x=-Math.PI/2;shadow.position.set(0,-1.29,-.1);group.add(shadow);
  let pointer={x:0,y:0},target={x:0,y:0},drag=false,lastX=0,rotation=0,scroll=0;
  const onMove=e=>{const r=host.getBoundingClientRect();target.x=((e.clientX-r.left)/r.width-.5)*2;target.y=((e.clientY-r.top)/r.height-.5)*2;if(drag){rotation+=(e.clientX-lastX)*.009;lastX=e.clientX;}};
  const down=e=>{drag=true;lastX=e.clientX;host.setPointerCapture?.(e.pointerId);};
  const up=()=>drag=false;
  const onScroll=()=>{const r=host.getBoundingClientRect();scroll=THREE.MathUtils.clamp((window.innerHeight-r.top)/(window.innerHeight+r.height),0,1);};
  host.addEventListener('pointermove',onMove);host.addEventListener('pointerdown',down);host.addEventListener('pointerup',up);host.addEventListener('pointercancel',up);window.addEventListener('scroll',onScroll,{passive:true});
  const resize=()=>{const w=host.clientWidth,h=host.clientHeight;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();};const ro=new ResizeObserver(resize);ro.observe(host);resize();
  let raf;const clock=new THREE.Clock();
  const animate=()=>{raf=requestAnimationFrame(animate);const t=clock.getElapsedTime();pointer.x+=(target.x-pointer.x)*.035;pointer.y+=(target.y-pointer.y)*.035;group.rotation.y+=(pointer.x*.16+rotation-group.rotation.y)*.035;group.rotation.x+=(pointer.y*-.07+Math.sin(t*.35)*.025-group.rotation.x)*.035;group.position.y=Math.sin(t*.65)*.055-scroll*.32;cup.rotation.y=Math.sin(t*.55)*.045;cup.rotation.z=-.09+Math.sin(t*.4)*.018;pouch.rotation.y=Math.sin(t*.45)*.07;beans.forEach(({mesh,base,phase})=>{mesh.position.y=base.y+Math.sin(t*.65+phase)*.18;mesh.position.x=base.x+Math.sin(t*.28+phase)*.06;mesh.rotation.z+=.002;});camera.position.x+=(pointer.x*.28-camera.position.x)*.025;camera.position.y+=(1.25-pointer.y*.12-camera.position.y)*.025;camera.lookAt(0,0,0);renderer.render(scene,camera);};animate();
  return()=>{cancelAnimationFrame(raf);ro.disconnect();window.removeEventListener('scroll',onScroll);host.removeEventListener('pointermove',onMove);host.removeEventListener('pointerdown',down);host.removeEventListener('pointerup',up);host.removeEventListener('pointercancel',up);renderer.dispose();host.innerHTML='';};
 },[]);
 return <div className="scene-wrap"><div className="scene-canvas" ref={mount}/><div className="scene-label label-one"><small>01 / THE DAILY RITUAL</small><b>Slow roast<br/>. good days.</b></div><div className="scene-label label-two"><small>DRAG TO EXPLORE</small><Move3D size={15}/></div><div className="scene-glow"/></div>;
}
export default function App(){
 const[cart,setCart]=useState([]),[open,setOpen]=useState(false),[intro,setIntro]=useState(true),[receipt,setReceipt]=useState(false);
 const count=cart.reduce((s,x)=>s+x.qty,0),total=cart.reduce((s,x)=>s+x.price*x.qty,0);
 useEffect(()=>{const t=setTimeout(()=>setIntro(false),1900);const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting&&e.target.dataset.reveal)e.target.classList.add('in-view')}),{threshold:.16});document.querySelectorAll('[data-reveal]').forEach(el=>io.observe(el));return()=>{clearTimeout(t);io.disconnect()}},[]);
 function add(p){setCart(old=>old.some(x=>x.id===p.id)?old.map(x=>x.id===p.id?{...x,qty:x.qty+1}:x):[...old,{...p,qty:1}]);setOpen(true)}
 function qty(id,d){setCart(old=>old.map(x=>x.id===id?{...x,qty:x.qty+d}:x).filter(x=>x.qty>0))}
 return <div className="shell">
 {intro&&<div className="intro-screen"><div className="intro-cup"><div className="intro-coffee"/></div><span>BREWNS — POUR SOMETHING GOOD</span></div>}
 <div className="announcement">GOOD COFFEE. GOOD MOOD. <span>ROASTED WITH LOVE IN COPENHAGEN</span><span>FREE SHIPPING OVER €45</span></div>
 <header><nav><a href="#shop">SHOP</a><a href="#menu">MENU</a><a href="#story">OUR STORY</a></nav><a className="logo" href="#top">brewns<span>✳</span></a><div className="right"><a href="#visit">FIND US</a><button onClick={()=>setOpen(true)}><ShoppingBag size={15}/> BAG <b>{String(count).padStart(2,'0')}</b></button></div></header>
 <main id="top">
 <section className="hero"><div className="hero-copy"><small>// SPECIALTY COFFEE HOUSE · COPENHAGEN</small><h1>COFFEE<br/>FOR YOUR<br/><em>mood.</em></h1><p>Carefully sourced beans. Thoughtfully brewed. Made to make your day.</p><a className="under" href="#shop">EXPLORE THE GOOD STUFF <ArrowDown size={14}/></a></div><CoffeeScene/><div className="hero-foot"><span>EST. 2021 — COPENHAGEN</span><span>SCROLL TO FEEL THE GOOD ↓</span></div></section>
 <div className="ticker"><div>GOOD COFFEE ✳ GOOD MOOD ✳ SLOW DOWN ✳ STAY A WHILE ✳ GOOD COFFEE ✳ GOOD MOOD ✳</div></div>
 <section className="story" id="story"><div className="eyebrow">01 / A BETTER DAILY RITUAL</div><div className="story-grid" data-reveal><h2>A little pause.<br/>A <em>lot</em> of good.</h2><div><p>We believe a really good cup can change the pace of your day. That’s why we work with people who care as much about coffee as we do — from the farms we source from to the hands that make your cup.</p><a className="under" href="#visit">GET TO KNOW US <ArrowUpRight size={15}/></a></div></div></section>
 <section className="shop" id="shop"><div className="eyebrow">02 / THE GOOD STUFF <span>FRESHLY ROASTED · ALWAYS</span></div><div className="shop-head"><div><small>TAKE A LITTLE HOME</small><h2>Meet your<br/><em>new daily.</em></h2></div><a className="round" href="#menu">ALL COFFEE ↗</a></div><div className="products">{products.map((p,i)=><article className="product" key={p.id} data-reveal style={{'--i':i}}><button className="photo" onClick={()=>add(p)}><img src={p.img} alt={p.name}/><span>{p.tag}</span><i><Plus size={18}/></i></button><div className="product-meta"><div><h3>{p.name}</h3><small>{p.type}</small></div><b>€{p.price.toFixed(2)}</b></div><p className="notes">{p.note}</p></article>)}</div></section>
 <section className="latte" id="menu"><div data-reveal><div className="eyebrow">03 / MADE WITH A LITTLE MAGIC</div><h2>Not just<br/>a coffee.<br/><em>A feeling.</em></h2><p>Good things take time. Our baristas take the long way around — dialing in every shot, steaming every pour, making every cup count.</p><a className="under" href="#visit">COME SAY HELLO <ArrowUpRight size={15}/></a></div><div className="latte-stage"><div className="latte-orbit orbit-a"/><div className="latte-orbit orbit-b"/><img src="https://images.unsplash.com/photo-1461023058943-07fcbe16d735?auto=format&fit=crop&w=1100&q=90" alt="Iced oat latte"/><span>SLOW SIPS ONLY</span><b>04:35 PM</b></div></section>
 <section className="beans-section"><div className="eyebrow">A LITTLE EXTRA SOMETHING</div><h2>Good things<br/>are <em>in the air.</em></h2><div className="beans-cloud" aria-hidden="true">{Array.from({length:18},(_,i)=><span key={i} style={{'--n':i}}>✳</span>)}</div><p>Freshly roasted. Never rushed. Always worth the wait.</p></section>
 <section className="visit" id="visit"><div className="eyebrow">YOUR TABLE IS WAITING</div><h2>Come as<br/><em>you are.</em></h2><div className="visit-grid"><div><small>FIND YOUR WAY</small><p>Nørrebro, Copenhagen<br/>Denmark</p><a href="https://maps.google.com/?q=Norrebro+Copenhagen" target="_blank" rel="noreferrer">GET DIRECTIONS ↗</a></div><div><small>WHEN WE’RE HERE</small><p>MON — FRI <b>08:00 — 17:00</b><br/>SAT — SUN <b>09:00 — 18:00</b></p></div><div><small>SAY SOMETHING</small><p>hello@brewns.coffee</p><a href="mailto:hello@brewns.coffee">DROP US A LINE ↗</a></div></div></section>
 </main>
 <footer><a className="logo" href="#top">brewns<span>✳</span></a><div>GOOD COFFEE.<br/>GOOD MOOD.<br/><em>See you soon.</em></div><a href="https://instagram.com" target="_blank" rel="noreferrer">INSTAGRAM <Instagram size={14}/></a><small>© BREWNS COFFEE HOUSE 2025 · MADE SLOWLY, WITH LOVE.</small></footer>
 {open&&<div className="backdrop" onClick={()=>setOpen(false)}><aside className="drawer" onClick={e=>e.stopPropagation()}><div className="drawer-top"><small>YOUR LITTLE PICK-ME-UP</small><button onClick={()=>setOpen(false)}><X/></button></div><h2>Your bag<span>.</span></h2>{cart.length===0?<div className="empty">Your bag is taking a little coffee break.<br/><a href="#shop" onClick={()=>setOpen(false)}>EXPLORE THE SHOP ↗</a></div>:<>{cart.map(x=><div className="line" key={x.id}><img src={x.img}/><div><b>{x.name}</b><small>{x.type}</small><div className="qty"><button onClick={()=>qty(x.id,-1)}><Minus size={13}/></button>{x.qty}<button onClick={()=>qty(x.id,1)}><Plus size={13}/></button></div></div><strong>€{(x.price*x.qty).toFixed(2)}</strong></div>)}<div className="subtotal"><span>SUBTOTAL</span><b>€{total.toFixed(2)}</b></div><p className="fine">Shipping and taxes calculated at checkout.</p><button className="checkout" onClick={()=>alert('Thanks for stopping by! Checkout is a demo in this concept build.')}>CONTINUE TO CHECKOUT ↗</button></>}</aside></div>}
 </div>;
}