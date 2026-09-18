export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Project = { id:number; name:string; description:string; created_at:string };
export type Scan = { id:number; project_id:number; url:string; title:string; role:string; total_testable_objects:number; created_at:string };
export type RiskFactor = { code:string; description:string; weight:number; count:number; points:number };
export type CompareResult = {
  diff:{ added:unknown[]; removed:unknown[]; changed:unknown[]; unchanged_count:number };
  risk:{ score:number; raw_score:number; level:"LOW"|"MEDIUM"|"HIGH"|"CRITICAL"; factors:RiskFactor[]; summary:string };
};

async function request<T>(path:string, init?:RequestInit):Promise<T>{
  const response=await fetch(API_URL+path,{...init,headers:{"Content-Type":"application/json",...(init?.headers??{})},cache:"no-store"});
  if(!response.ok) throw new Error((await response.text()) || `HTTP ${response.status}`);
  return response.json();
}
export const api={
  projects:()=>request<Project[]>("/api/v1/projects"),
  createProject:(name:string,description:string)=>request<Project>("/api/v1/projects",{method:"POST",body:JSON.stringify({name,description})}),
  scans:(id:number)=>request<Scan[]>(`/api/v1/projects/${id}/scans`),
  scan:(id:number,url:string,role:"baseline"|"current")=>request<Scan>(`/api/v1/projects/${id}/scans`,{method:"POST",body:JSON.stringify({url,role})}),
  compare:(id:number)=>request<CompareResult>(`/api/v1/projects/${id}/compare`),
};
