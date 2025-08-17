(function () {
  function onReady(fn) {
    if (document.readyState === "complete" || document.readyState === "interactive") {
      setTimeout(fn, 0);
    } else {
      document.addEventListener("DOMContentLoaded", fn);
    }
  }
/*
  function computeBasePrefix() {
    // 兼容 GitHub Pages 的子路径，如 /algolib/en/... 或 /algolib/zh/...
    var parts = window.location.pathname.split("/").filter(Boolean);
    var idx = parts.indexOf("algolib");
    if (idx >= 0) {
      return "/" + parts.slice(0, idx + 1).join("/") + "/"; // -> "/algolib/"
    }
    return "/"; // 本地 file:// 或非子路径
  }
*/
    // 计算当前页面对应的英/中文链接（保持子路径）
function computeLangHrefs() {
  var path = window.location.pathname;              // e.g. /algolib/en/api/xxx.html
  var parts = path.split("/").filter(Boolean);

  // —— 基底：GitHub Pages 项目路径（/algolib/）
  var repoIdx = parts.indexOf("algolib");          // ← 如果改了仓库名，这里要同步改
  var baseParts = repoIdx >= 0 ? parts.slice(0, repoIdx + 1) : [];
  var base = baseParts.length ? ("/" + baseParts.join("/") + "/") : "/";

  // —— 找当前语言段（en / zh），并取其后的“子路径”
  var langIdx = -1;
  for (var i = baseParts.length; i < parts.length; i++) {
    if (parts[i] === "en" || parts[i] === "zh") {  // 如果以后用 zh_CN，这里替换成 "zh_CN"
      langIdx = i;
      break;
    }
  }
  var subParts = langIdx >= 0 ? parts.slice(langIdx + 1) : parts.slice(baseParts.length);
  var subpath = subParts.join("/");

  // 去掉末尾的 index.html（避免 .../en/index.html 变成双 index）
  subpath = subpath.replace(/(^|\/)index\.html$/, "");

  // 组装目标链接
  var en = base + "en/" + subpath;
  var zh = base + "zh/" + subpath;

  // 如果是目录（没有 .html），补一个斜杠以避免 301 跳转
  if (subpath && !subpath.endsWith(".html") && !subpath.endsWith("/")) {
    en += "/";
    zh += "/";
  }
  return { en: en, zh: zh };
}

  onReady(function () {
    // RTD 主题的侧边栏可滚动容器
    var sideScroll =
      document.querySelector(".wy-side-scroll") ||
      document.querySelector(".wy-nav-side"); // 兜底
    if (!sideScroll) return;

    // var base = computeBasePrefix();      // e.g. "/algolib/"
    // var enHref = base + "en/";
    // var zhHref = base + "zh/";
    var links = computeLangHrefs();
    var enHref = links.en;
    var zhHref = links.zh;

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