'use strict';
document.querySelectorAll('[data-opportunity]').forEach(button=>button.addEventListener('click',()=>{
  showOpportunity(CATALOG.find(record=>record.id===button.dataset.opportunity));
}));
