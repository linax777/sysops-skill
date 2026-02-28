---
alert_id: P001
component: nginx
action: restart
---

# SOP: 重新啟動 Nginx 服務

這是一份標準作業流程，主要用來響應 [[P001_HighCPU]] 告警。
在執行前，請確保你已經檢視過目前的連線數上限設定檔：[[nginx_config]]。

## 執行步驟

1. 登入目標機器。
2. 執行語法檢查：
   ```bash
   nginx -t
   ```
3. 確認沒問題後，執行 Reload 而不是 Restart，以避免中斷使用者的連線：
   ```bash
   systemctl reload nginx
   ```
4. 若 Reload 無效，才考慮阻斷式重啟：
   ```bash
   systemctl restart nginx
   ```
   
## 驗證
透過以下腳本追蹤 500 錯誤率是否下降：[[log_analysis_script]]。
