// docs/source/_static/langswitch.js
(function () {
  function onReady(cb) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", cb);
    } else {
      cb();
    }
  }

  function computeLocaleAndUrls() {
    // 例如 /algolib/en/api/algolib.html 或 /algolib/zh/index.html
    const path = window.location.pathname;
    const parts = path.split("/").filter(Boolean); // ["algolib","en","api",...]
    if (parts.length === 0) {
      return { loc: "en", enURL: "/en/", zhURL: "/zh/" };
    }
    // GitHub Pages 仓库名（第一段）
    const repo = parts[0];                   // "algolib"
    const base = "/" + repo + "/";           // "/algolib/"

    // 判断第二段是否是语言段
    let loc = "en";
    let startIdx = 1;
    if (parts[1] === "en" || parts[1] === "zh" || parts[1] === "zh_CN") {
      loc = parts[1] === "zh" || parts[1] === "zh_CN" ? "zh" : "en";
      startIdx = 2;
    }

    const tail = parts.slice(startIdx).join("/"); // 语言段后的剩余路径
    const tailWithSlash = tail ? tail + (path.endsWith("/") ? "/" : "") : "";

    const enURL = base + "en/" + tailWithSlash;
    const zhURL = base + "zh/" + tailWithSlash;

    return { loc, enURL, zhURL };
  }

  onReady(function () {
    const host = document.querySelector(".wy-side-scroll");
    if (!host) return;

    const { loc, enURL, zhURL } = computeLocaleAndUrls();

    // 创建固定在侧栏底部的容器
    const footer = document.createElement("div");
    footer.id = "algolib-side-footer";
    footer.innerHTML = `
      <div class="algolib-footer-title">Language / 语言</div>
      <div class="algolib-footer-lang">
        <a href="${enURL}" class="${loc === "en" ? "active" : ""}">English</a>
        <span class="sep">|</span>
        <a href="${zhURL}" class="${loc !== "en" ? "active" : ""}">简体中文</a>
      </div>
      <div class="algolib-footer-gh">
        <a class="gh-icon" href="https://github.com/HidekiHokuto/algolib"
           aria-label="GitHub Repo" title="GitHub Repo">
          <!-- GitHub mark：用 currentColor，颜色由 CSS 决定（深色自动白） -->
          <svg viewBox="0 0 16 16" width="22" height="22" aria-hidden="true">
            <path fill="currentColor"
d="M8 0C3.58 0 0 3.58 0 8a8 8 0 005.47 7.59c.4.07.55-.17.55-.38
0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13
-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66
.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15
-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82a7.65 7.65 0 012 0
c1.53-1.03 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15
0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.19
0 .21.15.46.55.38A8 8 0 0016 8c0-4.42-3.58-8-8-8z"></path>
          </svg>
        </a>
      </div>
    `;

    host.appendChild(footer);

    // 让侧栏有底部空间，不被覆盖
    host.style.position = "relative";
    host.style.paddingBottom = "96px";
  });
})();