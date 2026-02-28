---
type: script
lang: bash
component: nginx
---

# Nginx Log 分析小工具

這個腳本常被用於初步故障排除：[[SOP_Restart_Nginx]]。

有時候雖然 CPU 飆高，但我們需先釐清是 HTTP 500 還是 HTTP 200 (純粹流量大)。
您可以直接在機器上執行以下指令來觀察 access_log：

```bash
#!/bin/bash
# 取出近 1000 行日誌，並統計 HTTP Status Code
tail -n 1000 /var/log/nginx/access.log | awk '{print $9}' | sort | uniq -c | sort -rn
```
