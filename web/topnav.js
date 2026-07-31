(function () {
  var sel = document.getElementById('nav-select');
  if (sel) {
    sel.addEventListener('change', function () {
      if (this.value) window.location.href = this.value;
    });
  }
})();
