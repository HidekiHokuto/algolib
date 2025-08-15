(function () {
  // 取当前路径，不依赖域名或仓库名
  var path = window.location.pathname;

  // 如果没有语言段，兜底把它当作首页（比如 /algolib/），指向语言选择页
  if (!/\/(en|zh_CN)\//.test(path)) {
    return;
  }

  function swapTo(lang) {
    // 只替换第一个语言段 en/zh_CN，后面的路径保留，保证同页切换
    return path.replace(/\/(en|zh_CN)\//, "/" + lang + "/");
  }

  var en = document.getElementById("lang-en");
  var zh = document.getElementById("lang-zh");
  if (en) en.setAttribute("href", swapTo("en"));
  if (zh) zh.setAttribute("href", swapTo("zh_CN"));
})();