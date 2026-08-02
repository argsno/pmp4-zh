# 02 — 移动端顶栏随页滚走 + 固定底部翻页条

**What to build:** 移动端（≤640px）顶栏不再固定，随正文一起滚出屏幕；同时视口底部固定一条 Prev/Next 翻页条，让线性阅读的读者随时翻页而不必滚回顶部。仅章节页显示底部条（落地页无 prev/next 故不显示）。正文末行不被底条遮挡，并适配 iPhone 底部安全区。English / Chinese / bilingual 三站均生效。

**Blocked by:** 01 — 移除移动端下滑自动隐藏（两者都改同一 `TOPNAV_CSS` 的 `≤640px` 块，先稳定"自动隐藏移除"再改定位更干净；属排序依赖，非功能门禁）。

**Status:** ready-for-agent

- [ ] ≤640px 时顶栏为 `position: static`，向下滚动时整条顶栏随页面滚出视口。
- [ ] 章节页底部出现固定翻页条，含 Prev / Next；首页的 Prev、末页的 Next 为禁用态；落地页无翻页条。
- [ ] `≤640px` 给正文容器补 `padding-bottom` 腾出底条空间，翻页条含 `env(safe-area-inset-bottom)` 适配，末行不被遮挡。
- [ ] 在 375px（用 `.scratch/mobile-responsive/sweep.py`）验证：顶栏滚走 + 底条固定 + 下拉仍能跳章。
- [ ] Chinese / bilingual 站点的底条与相对链接行为与 English 站一致（翻页条随头部整段被渲染器带过去）。
