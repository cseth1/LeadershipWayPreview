'use strict';
// One audience and search contract across all discovery pages.
window.LeadershipDiscovery=(()=>{
 const employeeRoles=['Employees','Staff','Faculty','FacultyFocus','Supervisors'];
 const labels={Employees:'All employee opportunities',Staff:'Staff',Faculty:'Faculty',FacultyFocus:'Faculty-focused learning',Supervisors:'Supervisors & people leaders',Other:'Student, System & external',Students:'Students',System:'System & agency employees',External:'External & professional learners'};
 const normalize=value=>String(value??'').normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/&/g,' and ').replace(/[^\p{L}\p{N}]+/gu,' ').trim();
 function audienceMatches(record,audience='Employees'){
  if(audience==='Employees')return record.scope==='Employees';
  if(audience==='FacultyFocus')return record.scope==='Employees'&&record.facultyFocused===true;
  if(audience==='Other')return record.scope==='Other';
  if(employeeRoles.includes(audience))return record.scope==='Employees'&&(record.audienceTags||[]).includes(audience);
  return record.scope==='Other'&&(record.audienceTags||[]).includes(audience);
 }
 function filter(records,state={}){
  const words=normalize(state.q).split(' ').filter(Boolean);
  const rows=records.filter(r=>audienceMatches(r,state.audience||'Employees')&&(!state.stage||(r.stages||[]).includes(state.stage))&&(!state.type||r.type===state.type)&&(!state.topic||r.topic===state.topic)&&(!state.origin||r.origin===state.origin)&&(!state.area||r.area===state.area)&&(!state.provider||r.owner===state.provider)&&words.every(w=>normalize([r.title,r.description,r.owner,r.topic,r.area,r.audienceLabel,...(r.audience||[]),r.delivery].filter(Boolean).join(' ')).includes(w)));
  if(state.sort==='duration')rows.sort((a,b)=>(a.sortHours??Infinity)-(b.sortHours??Infinity)||a.title.localeCompare(b.title));
  else if(state.sort==='provider')rows.sort((a,b)=>a.owner.localeCompare(b.owner)||a.title.localeCompare(b.title));
  else if(state.sort==='title')rows.sort((a,b)=>a.title.localeCompare(b.title));
  else if(state.audience==='Faculty')rows.sort((a,b)=>Number((a.audienceTags||[]).includes('Staff'))-Number((b.audienceTags||[]).includes('Staff')));
  return rows;
 }
 return Object.freeze({filter,audienceMatches,normalize,labels,employeeRoles});
})();
