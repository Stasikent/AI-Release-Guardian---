export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Project = { id:number; name:string; description:string; base_url:string|null; block_on:"HIGH"|"CRITICAL"; max_risk_score:number; require_all_routes:boolean; created_at:string };
export type Scan = { id:number; project_id:number; url:string; route:string|null; title:string; role:string; total_testable_objects:number; created_at:string };
export type RiskFactor = { code:string; description:string; weight:number; count:number; points:number };
export type TestableObject = { object_type:string; tag_name:string; id?:string|null; name?:string|null; locator:string; display_name?:string|null; [key:string]:unknown };
export type ElementChange = { fingerprint:string; before:TestableObject; after:TestableObject; changed_fields:string[]; risk_points:number; field_risk_points:Record<string,number> };
export type RegressionFocusItem = { priority:number; severity:"LOW"|"MEDIUM"|"HIGH"|"CRITICAL"; target:string; locator:string; reason:string; risk_points:number; suggested_check:string };
export type RegressionTestCase = { id:string; priority:number; severity:"LOW"|"MEDIUM"|"HIGH"|"CRITICAL"; title:string; target:string; locator:string; preconditions:string[]; steps:string[]; expected_results:string[]; source:"deterministic"; risk_points:number };
export type RouteReleaseSummary = { route:string; status:"READY"|"MISSING_BASELINE"|"MISSING_CURRENT"; comparable:boolean; baseline_scan_id:number|null; current_scan_id:number|null; risk_score:number|null; risk_level:"LOW"|"MEDIUM"|"HIGH"|"CRITICAL"|null; added_count:number; removed_count:number; changed_count:number; regression_tests_count:number };
export type ProjectReleaseOverview = { project_id:number; gate_status:"READY"|"BLOCKED"|"INCOMPLETE"; gate_reason:string; routes:RouteReleaseSummary[]; comparable_routes:number; incomplete_routes:number; overall_risk_score:number; overall_risk_level:"LOW"|"MEDIUM"|"HIGH"|"CRITICAL" };
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
  createProject:(name:string,description:string,base_url:string)=>request<Project>("/api/v1/projects",{method:"POST",body:JSON.stringify({name,description,base_url:base_url||null})}),
  scans:(id:number)=>request<Scan[]>(`/api/v1/projects/${id}/scans`),
  routes:(id:number)=>request<string[]>(`/api/v1/projects/${id}/routes`),
  releaseOverview:(id:number)=>request<ProjectReleaseOverview>(`/api/v1/projects/${id}/release-overview`),
  updateReleasePolicy:(id:number,policy:{block_on:"HIGH"|"CRITICAL";max_risk_score:number;require_all_routes:boolean})=>request<Project>(`/api/v1/projects/${id}/release-policy`,{method:"PUT",body:JSON.stringify(policy)}),
  scan:(id:number,url:string,role:"baseline"|"current",route?:string)=>request<Scan>(`/api/v1/projects/${id}/scans`,{method:"POST",body:JSON.stringify({url,role,route:route||null})}),
  compare:(id:number,route?:string)=>request<CompareResult>(`/api/v1/projects/${id}/compare${route?`?route=${encodeURIComponent(route)}`:""}`),
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

export function regressionExportUrl(id:number,format:"json"|"markdown"|"playwright",route?:string):string{return `${API_URL}/api/v1/projects/${id}/regression-tests/export?format=${format}${route?`&route=${encodeURIComponent(route)}`:""}`;}

export function multiRoutePlaywrightExportUrl(id:number):string{return `${API_URL}/api/v1/projects/${id}/regression-tests/export?format=playwright`;}
