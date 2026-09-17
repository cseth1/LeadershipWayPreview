'use strict';
// Preserve existing links after moving the narrative to the home page.
(function () {
  function followMovedPage() {
    const current = new URL(window.location.href);
    const page = current.pathname.split('/').pop();
    let destination = '';
    if (page === 'aggie-way.html') destination = 'index.html';
    else if ((page === '' || page === 'index.html') &&
      (['#opportunities', '#journey', '#resources'].includes(current.hash) ||
       ['q', 'stage', 'type'].some(key => current.searchParams.has(key)))) {
      destination = 'programs.html';
    }
    if (destination) window.location.replace(new URL(destination + current.search + current.hash, current).href);
  }
  followMovedPage();
  window.addEventListener('hashchange', followMovedPage);
})();
