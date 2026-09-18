"use client";
import {FormEvent,useEffect,useState} from "react";
import {api,CompareResult,Scan} from "../../../lib/api";

export default function ProjectPage({params}:{params:{id:string}}){
 const id=Number(params.id); const [scans,setScans]=useState<Scan[]>([]); const [url,setUrl]=useState(""); const [role,setRole]=useState<"baseline"|"current">("current"); const [comparison,setComparison]=useState<CompareResult|null>(null); const [busy,setBusy]=useState(false); const [error,setError]=useState("");
 const load=()=>api.scans(id).then(setScans).catch(e=>setError(String(e))); useEffect(()=>{load()},[id]);
 async function scan(e:FormEvent){e.preventDefault();setBusy(true);setError("");try{await api.scan(id,url,role);await load();setUrl("")}catch(e){setError(String(e))}finally{setBusy(false)}}
 async function compare(){setBusy(true);setError("");try{setComparison(await api.compare(id))}catch(e){setError("Create both baseline and current scans before comparing.")}finally{setBusy(false)}}
 return <main className="shell"><a className="back" href="/">← Projects</a><header><div><span className="eyebrow">PROJECT #{id}</span><h1>Release analysis</h1><p>Capture a baseline, scan the current UI, then compare observable changes.</p></div></header>
 <div className="grid">
  <section className="panel"><h3>Run scan</h3><form onSubmit={scan}><label>Target URL<input type="url" placeholder="https://example.com" value={url} onChange={e=>setUrl(e.target.value)} required/></label><label>Scan role<select value={role} onChange={e=>setRole(e.target.value as "baseline"|"current")}><option value="baseline">Baseline</option><option value="current">Current</option></select></label><button disabled={busy}>{busy?"Running…":"Run scan"}</button></form></section>
  <section className="panel risk"><h3>Release Risk</h3>{comparison?<><div className={`score ${comparison.risk.level.toLowerCase()}`}>{comparison.risk.score}<small>/100</small></div><b>{comparison.risk.level}</b><p>{comparison.risk.summary}</p><div className="metrics"><span>+ {comparison.diff.added.length} added</span><span>− {comparison.diff.removed.length} removed</span><span>△ {comparison.diff.changed.length} changed</span></div></>:<><div className="score empty">--</div><p className="muted">Compare baseline and current scans to calculate risk.</p></>}<button className="secondary" onClick={compare} disabled={busy}>Compare latest</button></section>
 </div>
 <section className="panel"><h3>Scan history</h3>{scans.length===0?<p className="muted">No scans yet.</p>:<div className="table">{scans.map(s=><div className="row" key={s.id}><span className={`badge ${s.role}`}>{s.role}</span><div><strong>{s.title||s.url}</strong><small>{s.url}</small></div><span>{s.total_testable_objects} objects</span><time>{new Date(s.created_at).toLocaleString()}</time></div>)}</div>}{error&&<p className="error">{error}</p>}</section>
 {comparison&&comparison.risk.factors.length>0&&<section className="panel"><h3>Why this score?</h3>{comparison.risk.factors.map(f=><div className="factor" key={f.code}><div><strong>{f.description}</strong><small>{f.count} × {f.weight} points</small></div><b>+{f.points}</b></div>)}</section>}
 </main>
}
