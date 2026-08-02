# 01 — 移除移动端下滑自动隐藏

**What to build:** 移动端（≤640px）导航栏不再随滚动"下滑隐藏、上滑出现"。读者向下读章节时顶栏始终留在原处（跟随 sticky 定位），不再有 `translateY` 位移或 `nav-hidden` 隐藏。章节下拉选择器照常工作。桌面（>640px）行为完全不变。

**Blocked by:** None — can start immediately.

**Status:** implemented（375px CDP 验证通过：en/zh/bilingual 三站顶栏滚动中恒为 `top: 0`、`transform: none`、无 `nav-hidden`，下拉仍能跳章；1280px 桌面顶栏仍 sticky）

- [x] 在 ≤640px 滚动页面，顶栏始终可见，不出现 `translateY` 位移、不被隐藏。
- [x] 选择章节下拉项仍能跳转到对应章节页（下拉跳转逻辑保留）。
- [x] 自动隐藏相关代码已清除：`topnav.js` 仅保留 `select` 的 `change` 跳转 handler，删除 `matchMedia`/`scroll`/触摸整段；`TOPNAV_CSS` 中 `.topnav.nav-hidden`、`≤640px` 内的 `.topnav` `transform`/`transition`、`≤640px and (prefers-reduced-motion: reduce)` 块均已移除。
- [x] 桌面（>640px）顶栏 `sticky` 行为不变。
