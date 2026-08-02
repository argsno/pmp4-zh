# 03 — 重建并部署到 GitHub Pages

**What to build:** 在 01、02 完成后，重新生成整站（含三站点）并发布到 GitHub Pages（argsno.github.io/pmp4-zh），让读者在手机上实际看到新的移动端导航：顶栏随页滚走、底部固定翻页条。

**Blocked by:** 02 — 移动端顶栏随页滚走 + 固定底部翻页条。

**Status:** ready-for-agent

> ⚠️ 部署动作需用户在对话中显式确认后才执行。本 ticket 在用户发话前**不得**运行 push 或任何发布命令；在此之前只可做本地重建与本地验证。

- [ ] 本地 `python3 build_site.py` 完整重建成功，无渲染失败。
- [ ] 用 `.scratch/mobile-responsive/sweep.py` 在 375px 跑通：顶栏滚走、底条固定、下拉跳章、三站点一致。
- [ ] 用户确认后，将 `docs/`（及构建产物）提交并推送到 `main`，触发 GitHub Pages 重新发布。
- [ ] 线上站（argsno.github.io/pmp4-zh）在 375px 验证新导航行为符合预期。
