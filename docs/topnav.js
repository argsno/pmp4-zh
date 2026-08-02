// The chapter dropdown is the whole script: a native <select> cannot navigate
// on its own.  Where the bar sits is topnav.css's business, and no scroll
// position changes it.
(function () {
  var sel = document.getElementById('nav-select');
  if (sel) {
    sel.addEventListener('change', function () {
      if (this.value) window.location.href = this.value;
    });
  }
})();
