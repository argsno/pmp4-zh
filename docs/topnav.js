(function () {
  var sel = document.getElementById('nav-select');
  if (sel) {
    sel.addEventListener('change', function () {
      if (this.value) window.location.href = this.value;
    });
  }

  var header = document.querySelector('header.topnav');
  if (!header) return;

  // Mobile only: the desktop bar is always fixed, and stays that way.  The
  // same ≤640px breakpoint the CSS uses gates every hide/reveal below.
  var mq = window.matchMedia('(max-width: 640px)');

  var HIDE_DOWN = 20;     // cumulative scroll-down (px) that hides the bar
  var KEEP_TOP = 100;     // bar always visible this close to the page top
  var KEEP_BOTTOM = 200;  // ...and this close to the page bottom
  var hidden = false;
  var lastY = window.pageYOffset;
  var accum = 0;
  var ticking = false;
  var pressing = false;

  function apply() {
    header.classList.toggle('nav-hidden', hidden);
  }

  function reveal() {
    if (hidden) {
      hidden = false;
      apply();
    }
    accum = 0;
  }

  function onScroll() {
    if (!mq.matches) return;   // desktop: the bar never moves
    if (pressing) return;      // a finger or cursor is on the bar: it stays put
    var y = window.pageYOffset;
    var delta = y - lastY;
    lastY = y;
    var maxY = document.documentElement.scrollHeight - window.innerHeight;
    // Any upward scroll brings the bar back immediately, and it never leaves
    // within ~100px of the top or ~200px of the bottom — exactly where the
    // chapter dropdown and the prev/next buttons are wanted.  A bar the
    // reader is using (select open, a button focused) stays put too.
    if (delta < 0 || y <= KEEP_TOP || maxY - y <= KEEP_BOTTOM ||
        header.matches(':focus-within')) {
      reveal();
    } else if (delta > 0) {
      // Down-scrolls accumulate: a 20px flick hides the bar, while a few px
      // of drift here and there does not.
      accum += delta;
      if (!hidden && accum >= HIDE_DOWN) {
        hidden = true;
        apply();
      }
    }
  }

  window.addEventListener('scroll', function () {
    if (ticking) return;   // one pass per animation frame
    ticking = true;
    window.requestAnimationFrame(function () {
      ticking = false;
      onScroll();
    });
  }, { passive: true });

  // Touching, pressing, or focusing anything in the bar counts as using it:
  // keep it on screen and cancel any pending hide.  `pressing` stays set for
  // the whole hold, so a drag that starts on the bar cannot hide it — the
  // moment a touch/mouse is released, ordinary scroll behaviour resumes.
  function press() { pressing = true; reveal(); }
  function release() { pressing = false; }
  header.addEventListener('touchstart', press, { passive: true });
  header.addEventListener('mousedown', press, { passive: true });
  header.addEventListener('touchend', release, { passive: true });
  header.addEventListener('touchcancel', release, { passive: true });
  header.addEventListener('mouseup', release);
  header.addEventListener('mouseleave', release);
  header.addEventListener('focusin', reveal);

  // Coming back to a desktop width reveals a bar a mobile session left hidden.
  var onMqChange = function () { if (!mq.matches) reveal(); };
  if (mq.addEventListener) mq.addEventListener('change', onMqChange);
  else mq.addListener(onMqChange);
})();
