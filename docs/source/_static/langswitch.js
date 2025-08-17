(function () {
  function onReady(fn) {
    if (document.readyState === "complete" || document.readyState === "interactive") {
      setTimeout(fn, 0);
    } else {
      document.addEventListener("DOMContentLoaded", fn);
    }
  }

  function computeBasePrefix() {
    // 兼容 GitHub Pages 的子路径，如 /algolib/en/... 或 /algolib/zh/...
    var parts = window.location.pathname.split("/").filter(Boolean);
    var idx = parts.indexOf("algolib");
    if (idx >= 0) {
      return "/" + parts.slice(0, idx + 1).join("/") + "/"; // -> "/algolib/"
    }
    return "/"; // 本地 file:// 或非子路径
  }

  onReady(function () {
    // RTD 主题的侧边栏可滚动容器
    var sideScroll =
      document.querySelector(".wy-side-scroll") ||
      document.querySelector(".wy-nav-side"); // 兜底
    if (!sideScroll) return;

    var base = computeBasePrefix();      // e.g. "/algolib/"
    var enHref = base + "en/";
    var zhHref = base + "zh/";

    // 容器：语言切换 + GitHub 按钮
    var wrap = document.createElement("div");
    wrap.className = "algolib-extras";

    var langDiv = document.createElement("div");
    langDiv.className = "algolib-lang";
    langDiv.innerHTML =
      '<h3>Language / 语言</h3>' +
      '<p><a href="' + enHref + '">English</a> <span class="sep">|</span> ' +
      '<a href="' + zhHref + '">简体中文</a></p>';

    // GitHub 圆形白底图标（不变形，深色背景可见）
    var gh = document.createElement("a");
    gh.className = "algolib-gh";
    gh.href = "https://github.com/HidekiHokuto/algolib";
    gh.target = "_blank";
    gh.rel = "noopener";
    gh.setAttribute("aria-label", "GitHub Repo");
    gh.innerHTML =
      '<span class="algolib-gh-circle">' +
      '<img src="https://github.githubassets.com/favicons/favicon.svg" alt="GitHub" />' +
      "</span>";

    wrap.appendChild(langDiv);
    wrap.appendChild(gh);

    // 插到底部；配合 CSS flex，让它贴底
    sideScroll.appendChild(wrap);
  });
})();