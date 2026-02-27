---
name: sysops-linter-skill
description: 用來驗證與評估系統維運知識庫 (Sysops Knowledge Base) 是否符合格式規範的稽核技能。當使用者要求「檢查知識庫健康度」、「驗證文件撰寫格式」或「找出不符合標籤規範的文件」時使用。請勿用於一般問題的資料檢索或回答維運問題。
---

# 系統維運知識庫驗證與稽核 (sysops-linter-skill)

此技能專門用來靜態掃描維運知識庫目錄，抓出違反「機器親和性撰寫指南」(例如檔案過大、遺漏標籤、非純文字檔案) 的項目，並產生標準化的健康度報告。

## 資源結構
- `SKILL.md`: 核心驗證流程與執行步驟。
- `scripts/validate_kb.py`: 實際執行目錄掃描與規則檢查的輕量 Python 工具程式。
- `assets/report_template.md`: 最後輸出給使用者的驗證報告範本。

## 目標知識庫根目錄定位
預設的知識庫目標為當前專案下的 `./references/`。 
如果使用者明確指定了其他需要檢查的目錄路徑，請改用使用者指定的路徑。
在執行腳本之前，請先使用 `test -d <目錄>` 確認目標目錄確實存在。

## 執行步驟 (Execution Steps)

Step 1: Check Target Directory
確認使用者要驗證的目標知識庫目錄 (預設為 `./references/`)。
使用 `test -d <目標目錄>` 檢查該目錄是否存在。若不存在，請中斷執行並詢問使用者實際的目錄位置。

Step 2: Run Validation Script
執行內建的驗證腳本來掃描目標目錄：
```bash
python .agent/skills/sysops-linter-skill/scripts/validate_kb.py <目標目錄>
```
這支腳本將會進行以下檢查，並直接在標準輸出 (stdout) 顯示發現的問題：
- **Large Files**: 行數大於 500 行的超大型 Markdown 檔案。
- **Invalid Formats**: 混入知識庫的非純文字檔案 (如 pdf, docx, xlsx)。
- **Missing Tags**: 最底層 (無子目錄) 的 `index.md` 檔案中，缺少 `Tags: [...]` 格式的項目。

Step 3: Analyze Script Output
讀取 `validate_kb.py` 的執行結果 (stdout/stderr)。若腳本發生未預期的例外錯誤，請將錯誤訊息回報給使用者。

Step 4: Format the Audit Report
將 Step 3 取得的掃描結果，按照 `.agent/skills/sysops-linter-skill/assets/report_template.md` 所定義的格式，產生最終的驗證報告並輸出給使用者。
- 若腳本沒有發現任何問題，請在報告中給予綠色的勾勾或恭喜訊息。
- 若發現特定違規，請依範本清楚列出檔名及違規原因。
