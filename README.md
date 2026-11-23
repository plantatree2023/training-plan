# 5K训练课表

2026年9月到2027年11月的每日5K训练计划和实际完成记录。

- `index.html`:页面(按月份切换,宽屏时日历在左侧)
- `plan.json`:全部数据。每天有 `plan`(计划)、`actual`(实际完成)、`score`/`scoreNote`(评分)
- `tools/`:最初生成全年计划用的脚本,只用过一次,日常更新不需要它们

每天晚上由定时任务从 Strava 拉取当天记录,更新 `plan.json` 并推送到这里,GitHub Pages 自动重新部署。
