export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Project = { id:number; name:string; description:string; created_at:string };
export type Scan = { id:number; project_id:number; url:string; title:string; role:string; total_testable_objects:number; created_at:string };
export type RiskFactor = { code:string; description:string; weight:number; count:number; points:number };
export type TestableObject = { object_type:string; tag_name:string; id?:string|null; name?:string|null; locator:string; display_name?:string|null; [key:string]:unknown };
export type ElementChange = { fingerprint:string; before:TestableObject; after:TestableObject; changed_fields:string[]; risk_points:number; field_risk_points:Record<string,number> };
export type RegressionFocusItem = { priority:number; severity:"LOW"|"MEDIUM"|"HIGH"|"CRITICAL"; target:string; locator:string; reason:string; risk_points:number; suggested_check:string };
export type RegressionTestCase = { id:string; priority:number; severity:"LOW"|"MEDIUM"|"HIGH"|"CRITICAL"; title:string; target:string; locator:string; preconditions:string[]; steps:string[]; expected_results:string[]; source:"deterministic"; risk_points:number };
export type CompareResult = {
  diff:{ added:TestableObject[]; removed:TestableObject[]; changed:ElementChange[]; unchanged_count:number };
  risk:{ score:number; raw_score:number; level:"LOW"|"MEDIUM"|"HIGH"|"CRITICAL"; factors:RiskFactor[]; summary:string };
  regression_focus:RegressionFocusItem[];
  regression_tests:RegressionTestCase[];
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

export type EvidenceItem={id:string;kind:string;statement:string;source:string;score:number|null};
export type AIAnalysisResponse={
 provider:string;model:string;
 analysis:{release_summary:string;likely_impacts:string[];regression_focus:string[];suggested_tests:string[];confidence:"low"|"medium"|"high";limitations:string[]};
 evidence:{observed:EvidenceItem[];retrieved:EvidenceItem[]};
};
export async function analyzeProject(id:number):Promise<AIAnalysisResponse>{
 return request<AIAnalysisResponse>(`/api/v1/projects/${id}/ai-analysis`,{method:"POST"});
}

export function regressionExportUrl(id:number,format:"json"|"markdown"|"playwright"):string{return `${API_URL}/api/v1/projects/${id}/regression-tests/export?format=${format}`;}
