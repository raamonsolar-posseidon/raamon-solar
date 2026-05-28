import os, base64, tempfile, shutil
from pathlib import Path
from flask import Flask, request, jsonify, Response
from motor import generar_propuesta

BASE = Path(__file__).parent
app  = Flask(__name__)
PORT = int(os.environ.get('PORT', 8080))

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RA-AMON SOLAR · Generador de Propuestas</title>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{--gold:#F5C518;--gold2:#c9a00f;--dark:#0e0d0d;--dark2:#1a1818;--dark3:#242222;--dark4:#2e2c2c;--light:#f0ede8;--muted:#7a7570;--green:#34c77b;--r:6px}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{background:var(--dark);color:var(--light);font-family:'Outfit',sans-serif;min-height:100vh;overflow-x:hidden}
body::before{content:'';position:fixed;inset:0;z-index:0;background-image:linear-gradient(rgba(245,197,24,.03) 1px,transparent 1px),linear-gradient(90deg,rgba(245,197,24,.03) 1px,transparent 1px);background-size:40px 40px;pointer-events:none}
body::after{content:'';position:fixed;inset:0;z-index:0;background:radial-gradient(ellipse 55% 35% at 85% 15%,rgba(245,197,24,.05) 0%,transparent 60%),radial-gradient(ellipse 40% 50% at 5% 85%,rgba(245,197,24,.03) 0%,transparent 55%);pointer-events:none}
.wrap{position:relative;z-index:1;max-width:740px;margin:0 auto;padding:52px 24px 80px}
.hdr{display:flex;align-items:flex-start;gap:20px;margin-bottom:48px;animation:dn .5s ease both}
.bolt{width:56px;height:56px;background:var(--gold);border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:3px;box-shadow:0 0 28px rgba(245,197,24,.20)}
.bolt svg{width:28px;height:28px;fill:var(--dark)}
.hdr h1{font-family:'Bebas Neue',sans-serif;font-size:clamp(34px,6.5vw,52px);letter-spacing:2px;line-height:1}
.hdr h1 span{color:var(--gold)}
.hdr p{color:var(--muted);font-size:13.5px;margin-top:7px;font-weight:300}
.divider{width:100%;height:1px;background:linear-gradient(90deg,var(--gold) 0%,transparent 55%);margin-bottom:36px}
.card{background:var(--dark2);border:1px solid rgba(245,197,24,.10);border-radius:12px;padding:30px 34px;margin-bottom:16px;animation:up .45s ease both}
.card:nth-child(2){animation-delay:.05s}.card:nth-child(3){animation-delay:.10s}.card:nth-child(4){animation-delay:.15s}
.ct{font-family:'Bebas Neue',sans-serif;font-size:15px;letter-spacing:2.5px;color:var(--gold);margin-bottom:22px;display:flex;align-items:center;gap:10px}
.ct::after{content:'';flex:1;height:1px;background:rgba(245,197,24,.14)}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.g3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}
.s2{grid-column:1/-1}
.f{display:flex;flex-direction:column;gap:7px}
.f label{font-size:11px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted)}
.f input,.f select{background:var(--dark3);border:1.5px solid rgba(255,255,255,.07);border-radius:var(--r);padding:13px 16px;font-family:'Outfit',sans-serif;font-size:15px;color:var(--light);outline:none;transition:border-color .18s,box-shadow .18s;appearance:none;-webkit-appearance:none}
.f select{background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%237a7570' stroke-width='1.5' stroke-linecap='round' fill='none'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 14px center;padding-right:40px}
.f input:focus,.f select:focus{border-color:var(--gold);box-shadow:0 0 0 3px rgba(245,197,24,.09)}
.f input::placeholder{color:#3e3c3a}
.f small{color:var(--muted);font-size:11.5px}
.popts{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
.po{background:var(--dark3);border:1.5px solid rgba(255,255,255,.07);border-radius:var(--r);padding:11px 4px 9px;text-align:center;cursor:pointer;transition:all .14s;color:var(--muted);font-family:'Outfit',sans-serif;font-size:11.5px;font-weight:600;user-select:none}
.po .n{display:block;font-size:20px;font-weight:700;color:var(--light);line-height:1.15;margin-bottom:1px}
.po:hover{border-color:rgba(245,197,24,.35)}
.po.on{background:rgba(245,197,24,.11);border-color:var(--gold);color:var(--gold)}
.po.on .n{color:var(--gold)}
.prev{background:var(--dark2);border:1px solid rgba(245,197,24,.10);border-radius:12px;padding:24px 34px;margin-bottom:16px;display:none;animation:up .35s ease both}
.prev.show{display:block}
.pl{font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:16px}
.pg{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px}
.pi{background:var(--dark3);border-radius:var(--r);padding:12px 14px}
.pi .l{font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:var(--muted);margin-bottom:3px}
.pi .v{font-size:13.5px;font-weight:600;color:var(--light)}
.pi .v.g{color:var(--gold)}
.cg{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:12px}
.ci{background:var(--dark4);border-radius:var(--r);padding:10px 8px;text-align:center}
.ci .cl{font-size:9px;font-weight:700;letter-spacing:.8px;text-transform:uppercase;color:var(--muted);margin-bottom:3px}
.ci .cv{font-size:13px;font-weight:700;color:var(--gold)}
.tip{font-size:12.5px;color:var(--muted);padding:11px 16px;margin-bottom:16px;background:rgba(245,197,24,.04);border:1px solid rgba(245,197,24,.12);border-radius:var(--r);line-height:1.6}
.tip strong{color:var(--gold)}
.btn-gen{width:100%;background:var(--gold);color:var(--dark);border:none;border-radius:var(--r);padding:19px;font-family:'Bebas Neue',sans-serif;font-size:21px;letter-spacing:3px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:12px;transition:all .18s;margin-bottom:16px;animation:up .45s .18s ease both}
.btn-gen:hover:not(:disabled){background:#ffd63a;transform:translateY(-2px);box-shadow:0 10px 28px rgba(245,197,24,.24)}
.btn-gen:disabled{opacity:.42;cursor:not-allowed;transform:none!important}
.btn-gen svg{width:22px;height:22px;fill:currentColor}
.sw{background:var(--dark2);border:1px solid rgba(245,197,24,.10);border-radius:12px;padding:26px 34px;display:none;animation:up .3s ease both}
.sw.show{display:block}
.sh{display:flex;align-items:center;gap:14px;margin-bottom:14px}
.si{width:44px;height:44px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.si.ld{background:rgba(245,197,24,.08);border:1.5px solid rgba(245,197,24,.22)}
.si.ok{background:rgba(52,199,123,.12);border:1.5px solid rgba(52,199,123,.38)}
.si.er{background:rgba(220,80,80,.12);border:1.5px solid rgba(220,80,80,.38)}
.spinner{width:20px;height:20px;border:2.5px solid rgba(245,197,24,.18);border-top-color:var(--gold);border-radius:50%;animation:spin .75s linear infinite}
.st strong{display:block;font-size:15.5px;font-weight:600;margin-bottom:3px}
.st p{font-size:13px;color:var(--muted);line-height:1.55}
.pw{background:var(--dark3);border-radius:100px;height:5px;overflow:hidden;margin:14px 0}
.pb{height:100%;background:linear-gradient(90deg,var(--gold2),var(--gold));border-radius:100px;transition:width .45s ease;width:0%}
.steps{display:flex;flex-direction:column;gap:9px;margin-bottom:4px}
.stp{display:flex;align-items:center;gap:10px;font-size:13px;color:var(--muted);transition:color .25s}
.stp.done{color:var(--green)}.stp.active{color:var(--light)}
.dot{width:7px;height:7px;border-radius:50%;background:var(--dark4);border:1.5px solid var(--muted);flex-shrink:0;transition:all .25s}
.stp.done .dot{background:var(--green);border-color:var(--green)}
.stp.active .dot{background:var(--gold);border-color:var(--gold2);animation:pulse 1.3s ease-in-out infinite}
.dl{display:none;flex-direction:column;gap:10px;margin-top:16px}
.dl.show{display:flex}
.sb{background:rgba(52,199,123,.07);border:1px solid rgba(52,199,123,.22);border-radius:var(--r);padding:14px 18px;font-size:13.5px;line-height:1.65;color:var(--light)}
.sb strong{color:var(--gold)}
.btn-dl{display:flex;align-items:center;justify-content:center;gap:10px;padding:14px;font-size:15px;font-weight:600;border-radius:var(--r);cursor:pointer;text-decoration:none;border:none;width:100%;transition:all .18s;background:var(--gold);color:var(--dark)}
.btn-dl:hover{background:#ffd63a}
.btn-new{width:100%;padding:13px;font-size:13px;color:var(--muted);background:none;border:1.5px solid rgba(255,255,255,.08);border-radius:var(--r);cursor:pointer;font-family:'Outfit',sans-serif;transition:all .15s}
.btn-new:hover{color:var(--light);border-color:rgba(255,255,255,.16)}
.footer{text-align:center;margin-top:56px;color:var(--muted);font-size:12px;letter-spacing:.4px;animation:up .5s .25s ease both}
.footer span{color:var(--gold)}
@keyframes dn{from{opacity:0;transform:translateY(-18px)}to{opacity:1;transform:translateY(0)}}
@keyframes up{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(245,197,24,.4)}50%{box-shadow:0 0 0 5px rgba(245,197,24,0)}}
@media(max-width:580px){.g2,.g3,.pg,.cg{grid-template-columns:1fr}.popts{grid-template-columns:repeat(4,1fr)}.card,.prev,.sw{padding:20px 16px}}
</style>
</head>
<body>
<div class="wrap">

<div class="hdr">
  <div class="bolt"><svg viewBox="0 0 24 24"><path d="M13 2L4.5 13.5H11L10 22L19.5 10.5H13Z"/></svg></div>
  <div>
    <h1><span>RA-AMON</span> SOLAR</h1>
    <p>Generador automático de propuestas comerciales fotovoltaicas</p>
  </div>
</div>
<div class="divider"></div>

<div class="card">
  <div class="ct">01 · Cliente</div>
  <div class="f">
    <label>Nombre del cliente o empresa</label>
    <input id="f-cli" type="text" placeholder="Ej: CÁRNICOS NOKUA S.A.S" oninput="upPrev()">
  </div>
</div>

<div class="card">
  <div class="ct">02 · Proyecto</div>
  <div class="f s2" style="margin-bottom:18px">
    <label>Paneles AE Solar TopCon 700W Bifaciales</label>
    <div class="popts">
      <div class="po" onclick="setP(10,this)"><span class="n">10</span>paneles</div>
      <div class="po" onclick="setP(12,this)"><span class="n">12</span>paneles</div>
      <div class="po" onclick="setP(16,this)"><span class="n">16</span>paneles</div>
      <div class="po on" onclick="setP(20,this)"><span class="n">20</span>paneles</div>
      <div class="po" onclick="setP(24,this)"><span class="n">24</span>paneles</div>
      <div class="po" onclick="setP(30,this)"><span class="n">30</span>paneles</div>
      <div class="po" onclick="setP(40,this)"><span class="n">40</span>paneles</div>
      <div class="po" onclick="setP('x',this)"><span class="n">···</span>otro</div>
    </div>
    <input id="f-cust" type="number" min="1" max="200" placeholder="Cantidad personalizada" style="display:none;margin-top:10px" oninput="upPrev()">
  </div>
  <div class="f">
    <label>Precio total del proyecto (COP)</label>
    <input id="f-pre" type="text" placeholder="Ej: 43500000  —  solo números" oninput="this.value=this.value.replace(/\\D/g,'');upPrev()">
    <small>Sin puntos ni comas · Ej: 43500000 → $ 43.500.000</small>
  </div>
</div>

<div class="card">
  <div class="ct">03 · Inversor</div>
  <div class="g2" style="margin-bottom:14px">
    <div class="f">
      <label>Marca</label>
      <select id="f-mar" onchange="autoMod();upPrev()">
        <option>HUAWEI</option><option>SOLAX</option><option>GROWATT</option>
        <option>SUNGROW</option><option>FRONIUS</option><option>SMA</option><option>OTRA</option>
      </select>
    </div>
    <div class="f">
      <label>Modelo</label>
      <input id="f-mod" type="text" placeholder="Ej: SUN2000-8KTL" oninput="upPrev()">
    </div>
  </div>
  <div class="g2">
    <div class="f">
      <label>Potencia (kW)</label>
      <select id="f-kw" onchange="upPrev()">
        <option>5</option><option>6</option><option selected>8</option><option>10</option>
        <option>12</option><option>15</option><option>17</option><option>20</option><option>25</option><option>30</option>
      </select>
    </div>
    <div class="f">
      <label>Tipo de conexión</label>
      <select id="f-fas" onchange="upPrev()">
        <option>BIFÁSICO</option><option>TRIFÁSICO</option><option>MONOFÁSICO</option>
      </select>
    </div>
  </div>
</div>

<div class="prev" id="prev">
  <div class="pl">Vista previa del proyecto</div>
  <div class="pg">
    <div class="pi"><div class="l">Cliente</div><div class="v g" id="pv-c">—</div></div>
    <div class="pi"><div class="l">Paneles</div><div class="v" id="pv-p">—</div></div>
    <div class="pi"><div class="l">Capacidad</div><div class="v" id="pv-k">—</div></div>
    <div class="pi"><div class="l">Generación / mes</div><div class="v" id="pv-g">—</div></div>
    <div class="pi"><div class="l">Inversor</div><div class="v" id="pv-i">—</div></div>
    <div class="pi"><div class="l">Precio</div><div class="v g" id="pv-pr">—</div></div>
  </div>
  <div class="cg" id="cg" style="display:none">
    <div class="ci"><div class="cl">Payback</div><div class="cv" id="cv-pb">—</div></div>
    <div class="ci"><div class="cl">Ahorro año 1</div><div class="cv" id="cv-a1">—</div></div>
    <div class="ci"><div class="cl">Ahorro 20 años</div><div class="cv" id="cv-a20">—</div></div>
    <div class="ci"><div class="cl">TIR estimada</div><div class="cv" id="cv-tir">—</div></div>
  </div>
</div>

<div class="tip"><strong>Nota:</strong> Las diapositivas de diseño fotovoltaico (4 y 5) se incluyen solo cuando se soliciten con el output de PVsol.</div>

<button class="btn-gen" id="btn-gen" onclick="generar()">
  <svg viewBox="0 0 24 24"><path d="M14 2H6C4.9 2 4 2.9 4 4v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm4 18H6V4h7v5h5v11zM12 11l-3 3h2v4h2v-4h2l-3-3z"/></svg>
  GENERAR PROPUESTA
</button>

<div class="sw" id="sw">
  <div class="sh">
    <div class="si ld" id="si"><div class="spinner"></div></div>
    <div class="st"><strong id="st-t">Generando propuesta...</strong><p id="st-m">Preparando datos</p></div>
  </div>
  <div class="pw"><div class="pb" id="pb"></div></div>
  <div class="steps" id="stps">
    <div class="stp" id="s1"><div class="dot"></div>Calculando análisis financiero</div>
    <div class="stp" id="s2"><div class="dot"></div>Generando gráficas de proyección</div>
    <div class="stp" id="s3"><div class="dot"></div>Ensamblando presentación</div>
    <div class="stp" id="s4"><div class="dot"></div>Preparando archivo para descarga</div>
  </div>
  <div class="dl" id="dl">
    <div class="sb" id="sb"></div>
    <a class="btn-dl" id="dl-link" href="#" download>
      ⬇ DESCARGAR PROPUESTA (.PPTX)
    </a>
    <button class="btn-new" onclick="resetApp()">↩ Generar otra propuesta</button>
  </div>
</div>

<div class="footer">
  <span>RA-AMON SOLAR</span> · Paneles AE Solar TopCon 700W Bifaciales<br>
  raamonsolar@gmail.com · 3128370064 · 3224235739
</div>
</div>

<script>
let pan=20;
const mods={HUAWEI:'SUN2000-8KTL',SOLAX:'X3-PRO-8K',GROWATT:'MIN 8000TL-X',SUNGROW:'SG8RT',FRONIUS:'Symo 8.2-3-M',SMA:'Sunny Tripower 8.0',OTRA:''};
const kws={HUAWEI:'8',SOLAX:'10',GROWATT:'8',SUNGROW:'8',FRONIUS:'8',SMA:'8',OTRA:'10'};
const $=id=>document.getElementById(id);
const fmt=n=>'$ '+Math.round(n).toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g,'.');
const delay=ms=>new Promise(r=>setTimeout(r,ms));

function getPan(){const c=$('f-cust');return c.style.display!=='none'?(parseInt(c.value)||0):pan;}
function autoMod(){const m=$('f-mar').value;$('f-mod').value=mods[m]||'';const ks=$('f-kw');for(const o of ks.options)if(o.value===(kws[m]||'10'))o.selected=true;}
function setP(v,b){document.querySelectorAll('.po').forEach(x=>x.classList.remove('on'));b.classList.add('on');const c=$('f-cust');if(v==='x'){c.style.display='block';pan=parseInt(c.value)||0;}else{c.style.display='none';pan=v;}upPrev();}

function calc(p,pr){
  const gm=p*84,mt=p*25000*2;
  let fl=[],ac=-pr,pb=20;
  for(let i=1;i<=20;i++){fl.push(gm*12*Math.pow(.995,i-1)*1000*Math.pow(1.08,i-1)-mt);}
  let a=-pr;
  for(let i=0;i<fl.length;i++){const pv=a;a+=fl[i];if(a>=0){pb=i+(-pv/fl[i]);break;}}
  const a20=fl.reduce((s,f)=>s+f,0);
  let lo=0,hi=5;
  for(let j=0;j<200;j++){const m=(lo+hi)/2;const n=-pr+fl.reduce((s,f,i)=>s+f/Math.pow(1+m,i+1),0);if(n>0)lo=m;else hi=m;}
  return{a20,pb,tir:(lo+hi)/2*100,a1:fl[0]};
}

function upPrev(){
  const c=$('f-cli').value.trim(),p=getPan(),pr=parseInt($('f-pre').value)||0;
  const m=$('f-mar').value,mod=$('f-mod').value.trim(),kw=$('f-kw').value,fa=$('f-fas').value;
  const pv=$('prev');
  if(!c&&!p&&!pr){pv.classList.remove('show');return;}
  pv.classList.add('show');
  $('pv-c').textContent=c.toUpperCase()||'—';
  $('pv-p').textContent=p>0?`${p} paneles`:'—';
  $('pv-k').textContent=p>0?`${Math.round(p*7)/10} kW`:'—';
  $('pv-g').textContent=p>0?`${(p*84).toLocaleString('es-CO')} kWh`:'—';
  $('pv-i').textContent=mod?`${m} ${mod} ${kw}kW`:'—';
  $('pv-pr').textContent=pr>0?fmt(pr):'—';
  const cg=$('cg');
  if(p>0&&pr>1000000){
    cg.style.display='grid';
    const d=calc(p,pr);
    $('cv-pb').textContent=`~ ${d.pb.toFixed(1)} años`;
    $('cv-a1').textContent=fmt(d.a1);
    $('cv-a20').textContent=fmt(d.a20);
    $('cv-tir').textContent=`~ ${d.tir.toFixed(0)} %`;
  }else{cg.style.display='none';}
}

function step(n){
  for(let i=1;i<=4;i++){const e=$(`s${i}`);e.classList.remove('active','done');if(i<n)e.classList.add('done');else if(i===n)e.classList.add('active');}
  $('pb').style.width=`${Math.round((n-1)/4*100)}%`;
}

async function generar(){
  const cli=$('f-cli').value.trim(),p=getPan(),pr=parseInt($('f-pre').value)||0;
  const mar=$('f-mar').value,mod=$('f-mod').value.trim()||'MODELO',kw=$('f-kw').value,fas=$('f-fas').value;
  if(!cli){alert('Ingresa el nombre del cliente.');return;}
  if(p<1){alert('Selecciona la cantidad de paneles.');return;}
  if(pr<1000000){alert('Ingresa un precio válido (mín. $1.000.000).');return;}

  $('btn-gen').disabled=true;
  $('sw').classList.add('show');
  $('dl').classList.remove('show');
  $('stps').style.display='flex';
  $('si').className='si ld';$('si').innerHTML='<div class="spinner"></div>';
  $('st-t').textContent='Generando propuesta...';
  $('st-m').textContent=`${cli.toUpperCase()} · ${p} paneles · ${fmt(pr)}`;
  step(1);

  try{
    await delay(200);step(2);$('st-m').textContent='Generando gráficas financieras...';
    await delay(300);step(3);$('st-m').textContent='Ensamblando diapositivas...';

    const resp=await fetch('/generar',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({nombre:cli,paneles:p,precio:pr,inv_marca:mar,inv_modelo:mod,inv_kw:parseInt(kw),inv_fase:fas})
    });

    await delay(200);step(4);$('st-m').textContent='Preparando descarga...';

    if(!resp.ok){
      const err=await resp.json();
      throw new Error(err.error||'Error del servidor');
    }

    const data=await resp.json();
    if(!data.ok) throw new Error(data.error||'Error generando el archivo');

    // Convertir base64 a blob descargable
    const bytes=Uint8Array.from(atob(data.data),c=>c.charCodeAt(0));
    const blob=new Blob([bytes],{type:'application/vnd.openxmlformats-officedocument.presentationml.presentation'});
    const url=URL.createObjectURL(blob);

    $('pb').style.width='100%';
    $('si').className='si ok';
    $('si').innerHTML='<svg width="22" height="22" viewBox="0 0 24 24" fill="#34c77b"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>';
    $('st-t').textContent='¡Propuesta lista!';
    $('st-m').textContent='';
    $('stps').style.display='none';

    const r=data.resumen;
    $('sb').innerHTML=`<strong>${cli.toUpperCase()}</strong> · ${p} paneles · ${fmt(pr)}<br>
      Payback ~${r.payback} años · Ahorro 20 años: ${fmt(r.ahorro20)} · TIR ${r.tir}%`;

    const dl=$('dl-link');
    dl.href=url; dl.download=data.filename;
    $('dl').classList.add('show');

  }catch(e){
    $('si').className='si er';
    $('si').innerHTML='<svg width="22" height="22" viewBox="0 0 24 24" fill="#dc5050"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>';
    $('st-t').textContent='Error al generar';
    $('st-m').textContent=e.message||'Intenta de nuevo';
    $('stps').style.display='none';
  }
  $('btn-gen').disabled=false;
}

function resetApp(){
  $('sw').classList.remove('show');$('prev').classList.remove('show');
  $('stps').style.display='flex';$('btn-gen').disabled=false;
  $('f-cli').value='';$('f-pre').value='';$('f-cust').style.display='none';
  pan=20;document.querySelectorAll('.po').forEach(b=>b.classList.remove('on'));
  document.querySelectorAll('.po')[3].classList.add('on');
}

autoMod();
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return Response(HTML, mimetype='text/html')

@app.route('/health')
def health():
    return jsonify({'status':'ok','plantilla':(BASE/'propuesta_plantilla.pptx').exists()})

@app.route('/generar', methods=['POST'])
def generar():
    data      = request.get_json(force=True) or {}
    nombre    = str(data.get('nombre','')).strip()
    paneles   = int(data.get('paneles', 20))
    precio    = int(data.get('precio', 0))
    inv_marca = str(data.get('inv_marca','HUAWEI')).strip()
    inv_modelo= str(data.get('inv_modelo','SUN2000')).strip()
    inv_kw    = int(data.get('inv_kw', 8))
    inv_fase  = str(data.get('inv_fase','BIFÁSICO')).strip()

    if not nombre:
        return jsonify({'error':'Nombre del cliente requerido'}), 400
    if precio < 1_000_000:
        return jsonify({'error':'Precio inválido'}), 400
    if not (1 <= paneles <= 200):
        return jsonify({'error':'Cantidad de paneles inválida'}), 400

    tmp = tempfile.mkdtemp()
    try:
        output_path, datos = generar_propuesta(
            nombre, paneles, precio,
            inv_marca, inv_modelo, inv_kw, inv_fase, tmp)
        with open(output_path,'rb') as f:
            b64 = base64.b64encode(f.read()).decode()
        return jsonify({
            'ok': True,
            'filename': Path(output_path).name,
            'data': b64,
            'resumen': {
                'payback':  round(datos['payback'], 2),
                'ahorro20': int(datos['ahorro20']),
                'tir':      round(datos['tir'], 1),
                'van':      int(datos['van']),
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)
