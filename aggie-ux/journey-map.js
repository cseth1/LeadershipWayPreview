'use strict';
// Editorial journey connections extend, but do not overwrite, source research.
window.JourneyMapping = (() => {
  const names = {'Start at A&M':'Start at A&M','Grow your skills':'Lead Yourself','Lead Yourself':'Lead Yourself','Lead people':'Lead People','Lead People':'Lead People','Lead Teams':'Lead Teams','Lead across A&M':'Lead Across A&M','Lead Across A&M':'Lead Across A&M','Develop others':'Develop Others','Develop Others':'Develop Others'};
  const extra = {
    E002:['Lead Teams'],E003:['Lead People','Lead Teams'],E004:['Lead Teams'],
    E005:['Lead Teams'],E006:['Lead People'],E007:['Lead Teams'],
    E011:['Lead Teams'],E012:['Lead Teams'],E013:['Lead Teams'],
    E015:['Lead Teams'],E016:['Lead Teams'],E017:['Lead Teams'],E027:['Lead Teams'],E033:['Lead Teams']
  };
  const topics = {
    'New supervisors':['Start at A&M','Lead People'],
    'Communication and feedback':['Lead Yourself','Lead People','Lead Teams'],
    'Trust and teamwork':['Lead People','Lead Teams','Lead Across A&M'],
    'Performance and accountability':['Lead People','Lead Teams'],
    'Coaching and mentoring':['Lead Yourself','Lead People','Lead Teams','Develop Others'],
    'Change and adaptability':['Lead Yourself','Lead Teams','Lead Across A&M'],
    'Professional growth':['Lead Yourself','Develop Others'],
    'Digital skills':['Lead Yourself']
  };
  for (const r of [...(window.CATALOG||[]),...(window.COURSES||[])]) {
    r.journeyStages=[...new Set([...(r.stages||[]).map(s=>names[s]||s),...(extra[r.id]||[])])];
  }
  const selectedResources={"T001": ["Start at A&M"], "T051": ["Start at A&M"], "T006": ["Start at A&M", "Lead Yourself", "Lead Across A&M", "Develop Others"], "T021": ["Lead Yourself"], "T044": ["Lead Yourself"], "T019": ["Lead People"], "T025": ["Lead People", "Develop Others"], "T052": ["Lead People"], "T053": ["Lead People", "Develop Others"], "T030": ["Lead Teams"], "T033": ["Lead Teams", "Lead Across A&M"], "T054": ["Lead Teams"], "T046": ["Lead Teams"], "T034": ["Lead Across A&M"], "T035": ["Lead Across A&M"], "T007": ["Develop Others"]};
  for (const r of window.TOOLKIT||[]) r.journeyStages=[...new Set([...(topics[r.topic]||[]),...(selectedResources[r.id]||[])])];
  return Object.freeze({canonical:value=>names[value]||value});
})();
