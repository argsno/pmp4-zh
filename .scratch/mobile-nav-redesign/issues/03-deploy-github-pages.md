# 03 — 重建并部署到 GitHub Pages

**What to build:** 在 01、02 完成后，重新生成整站（含三站点）并发布到 GitHub Pages（argsno.github.io/pmp4-zh），让读者在手机上实际看到新的移动端导航：顶栏随页滚走、底部固定翻页条。

**Blocked by:** 02 — 移动端顶栏随页滚走 + 固定底部翻页条。

**Status:** complete（用户在对话中确认后推送，Pages 构建 `26d7d85` 成功，线上 375px 验证 0 failing of 13）

> ⚠️ 部署动作需用户在对话中显式确认后才执行。本 ticket 在用户发话前**不得**运行 push 或任何发布命令；在此之前只可做本地重建与本地验证。

- [x] 本地 `python3 build_site.py` 完整重建成功，无渲染失败（33 页 ok，4 页为既有跳过项；产物与已提交的 `docs/` 逐字节一致，`chinese.css` 与 `.nojekyll` 软链未被构建破坏）。
- [x] 用 `.scratch/mobile-responsive/sweep.py` 在 375px 跑通（布局 0 failing of 45）；导航行为另用 `.scratch/mobile-nav-redesign/nav_check.py` 验证：顶栏 `static` 且滚出视口、底条 `fixed` 不随滚动移动、首页 Prev / 末页 Next 为禁用 `<span>`、落地页无底条、正文末行不被遮挡、下拉仍能跳章，三站点一致（0 failing of 13）。
- [x] 用户确认后推送 `f99f347..26d7d85` 到 `main`（ticket 01 `6577521`、ticket 02 `a2ec919`、导航验证脚本 `26d7d85`）；重建产物与已提交 `docs/` 一致，故无额外构建提交。Pages 构建 `26d7d85` 状态 `built`。
- [x] 线上站（argsno.github.io/pmp4-zh）在 375px 验证通过：`topnav.css` 已含 `.bottom-pager` 与 `position: static`、不再含 `nav-hidden`，`zh/chinese.css` 软链返回 200；`nav_check.py --base https://argsno.github.io/pmp4-zh` 三站点 0 failing of 13。
