---
component: nginx
env: production
type: config
---

# Nginx 生產環境配置參數

本參數檔直接相關的告警為：[[P001_HighCPU]]
處理方式請參閱：[[SOP_Restart_Nginx]]

## 核心參數

以下為系統目前的 `nginx.conf` 重點參數摘錄。
*請注意：我們強烈建議將 config 放在 `.md` 的 code-block 內，確保 Obsidian 的標籤索引能正確涵蓋它們。*

```yaml
worker_processes: auto
events:
  worker_connections: 4096 
  multi_accept: "on"
http:
  keepalive_timeout: 65
  client_max_body_size: 50m
```
