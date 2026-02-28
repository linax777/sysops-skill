---
alert_id: P001
component: nginx
severity: high
---

# P001: Nginx High CPU

當 Prometheus 觸發告警 `P001` 時，表示 Web Server 層載入過重。

## 處置方針

1. 請立即調閱目標機器日誌，可參考腳本：[[log_analysis_script]]。
2. 若確認為連線數異常暴增引發的擁塞，請參照 SOP 執行重啟：[[SOP_Restart_Nginx]]。
3. 如果是日常負載，後續應提報單據修改設定閥值：[[nginx_config]]。
