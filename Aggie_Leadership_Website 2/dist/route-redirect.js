'use strict';
(function(){
  function preserveBookmark(){
    const u=new URL(location.href);
    if(!['','index.html'].includes(u.pathname.split('/').pop()))return;
    const way=['#aggie-way','#our-purpose','#our-values','#leadership-in-action','#guiding-principles','#put-it-into-practice','#framework'];
    let destination='';
    if(way.includes(u.hash))destination='aggie-way.html';
    else if(['#opportunities','#resources'].includes(u.hash)||['q','stage','type'].some(k=>u.searchParams.has(k)))destination='programs.html';
    if(destination)location.replace(new URL(destination+u.search+u.hash,u).href);
  }
  preserveBookmark();window.addEventListener('hashchange',preserveBookmark);
})();
