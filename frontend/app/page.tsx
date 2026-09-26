"use client";
import {FormEvent,useEffect,useState} from "react";
import {api,Project} from "../lib/api";

export default function Home(){
 const [projects,setProjects]=useState<Project[]>([]);
 const [name,setName]=useState(""); const [description,setDescription]=useState(""); const [baseUrl,setBaseUrl]=useState(""); const [error,setError]=useState("");
 const load=()=>api.projects().then(setProjects).catch(e=>setError(String(e)));
 useEffect(()=>{load()},[]);
 async function create(e:FormEvent){e.preventDefault();setError("");try{await api.createProject(name,description,baseUrl);setName("");setDescription("");setBaseUrl("");load()}catch(e){setError(String(e))}}
 return <main className="shell">
  <header><div><span className="eyebrow">AI-NATIVE QA</span><h1>AI Release Guardian</h1><p>Detect interface changes, explain release risk, and focus regression testing where it matters.</p></div><div className="version">V2 · DEVELOPMENT</div></header>
  <section className="hero"><div><h2>Release confidence from observable UI facts.</h2><p>Code extracts facts. AI reasoning comes next.</p></div><div className="flow"><b>SCAN</b><span>→</span><b>DIFF</b><span>→</span><b>RISK</b></div></section>
  <div className="grid">
   <section className="panel"><h3>Projects</h3>{projects.length===0?<p className="muted">No projects yet.</p>:projects.map(p=><a className="project" href={`/projects/${p.id}`} key={p.id}><div><strong>{p.name}</strong><small>{p.description||"No description"}</small></div><span>Open →</span></a>)}</section>
   <section className="panel"><h3>New project</h3><form onSubmit={create}><label>Name<input value={name} onChange={e=>setName(e.target.value)} required minLength={2}/></label><label>Description<textarea value={description} onChange={e=>setDescription(e.target.value)} rows={4}/></label><label>Base URL <small>(optional, used by Playwright export)</small><input type="url" placeholder="https://app.example.com" value={baseUrl} onChange={e=>setBaseUrl(e.target.value)}/></label><button>Create project</button></form>{error&&<p className="error">{error}</p>}</section>
  </div>
 </main>
}
