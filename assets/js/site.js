// Mobile menu
document.querySelector('.menu-toggle')?.addEventListener('click', e => {
  const nav = document.getElementById('site-nav'); const open = nav.classList.toggle('open');
  e.currentTarget.setAttribute('aria-expanded', open);
});
// Hide dated promotions (BOGO week, holiday) outside their start/end dates.
(() => {
  const today = new Date().toISOString().slice(0, 10);
  document.querySelectorAll('[data-start],[data-end]').forEach(el => {
    const s = el.dataset.start, e = el.dataset.end;
    if ((s && today < s) || (e && today > e)) {
      el.hidden = true;
      const sec = el.closest('section');
      if (sec && !sec.querySelector('[data-start]:not([hidden]),[data-end]:not([hidden]),.card')) sec.hidden = true;
    }
  });
})();
// Learn page: play YouTube videos in place
document.querySelectorAll('.yt[data-yt]').forEach(a => a.addEventListener('click', e => {
  e.preventDefault();
  a.innerHTML = `<iframe src="https://www.youtube-nocookie.com/embed/${a.dataset.yt}?autoplay=1" allow="autoplay; encrypted-media" allowfullscreen></iframe>`;
}));
