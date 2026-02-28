---
name: sysops-skill
description: 從系統維運知識庫 (SysOps Knowledge Base) 檢索與回答問題。當使用者詢問關於系統架構、SOP、告警處理建議或系統參數時使用 (例如：「查詢 Nginx 的配置參數」或「如何處理告警 ID 1234」)。不適用於撰寫新程式碼、修改系統設定、單純除錯或進行一般網路搜尋。
---

# 系統維運知識庫檢索 (sysops-skill)

此技能定義了在「系統維運知識庫 (Knowledge Base)」中檢索資訊的標準作業程序。

## 資源結構
- `SKILL.md`: 核心檢索邏輯與導航步驟。
- `assets/reply_template.md`: 最後輸出給使用者的回覆格式範本。

## 目標知識庫根目錄定位
預設的知識庫分析目標為當前專案下的 `./references/`。 
如果使用者在對話中明確指定了其他路徑，請使用使用者指定的路徑作為知識庫根目錄。
**注意**：切勿使用 glob 猜測目錄存在與否。請使用 shell 功能 (如 `test -d`) 確認目錄是否存在。如果目標目錄不存在，請停止執行並詢問使用者的實際知識庫路徑。

## 執行步驟 (Execution Steps)

Step 1: Extract Keywords and Constraints
從使用者的提問中提取 3-8 個核心關鍵字 (包含可能的英文縮寫、同義詞、系統名稱如 Nginx)。同時提取任何時間或範圍限制。

Step 2: Check for Fast-Path Constraints
評估是否有精確條件可以直接跳過層層目錄探索：
- 若問題含有明確的「告警 ID」或「錯誤碼」：
  - **[Obsidian 環境]** 若環境支援 `obsidian` CLI (利用 `command -v obsidian` 確認)：
    - 優先執行 `obsidian bases query "SELECT SOP_Path FROM alert_db.base WHERE alert_id = '<告警ID>'"` (假設存在標準 `.base` 映射結構)。
    - 或執行 `obsidian search query="[alert_id:<告警ID>] path:01_triage_rules/" limit=3 format=json` 快速定位。
  - **[無 Obsidian 環境]** 直接並優先搜尋知識庫內的 `01_triage_rules/alarm_mapping/` 目錄或 `symptoms_check.md`，使用 `grep` 檢索。
  成功命中後跳至 Step 4。
- 若問題含有確切的「檔案名稱」：直接遞迴尋找該檔案名稱。跳至 Step 4。
- 若問題無精確條件，請進入 Step 3。

Step 3: Navigate Catalog Indexes (index.md)
優先嘗試利用環境支援的超級檢索工具，若無則依賴 `index.md` 探勘縮小範圍：
1. **[Obsidian 強化檢索]** 若系統中有安裝 `obsidian` CLI (利用 `command -v obsidian` 確認)：
   - 嘗試執行 `obsidian search query="<關鍵字>" limit=5 format=json`。
   - Obsidian 的搜尋自帶全文檢索與標籤索引 (`tag:#標籤`) 能力，能極快給出命中的檔案路徑。
   - 若成功取得候選檔案，整理至候選清單後直接進入 Step 4。
2. **[無 Obsidian 的傳統探勘]** 若執行失敗或無 `obsidian` 可用，改透過傳統 `index.md` 探勘：
   - 從知識庫根目錄開始，讀取當前目錄的 `index.md` (前 300 行)。
   - 掃描檔案內容的 `Tags` 欄位與目錄/檔案用途說明。
   - 根據提取的關鍵字，選出最相關的子目錄或候選業務檔案。
   - **決策**：如果選出的是子目錄，請進入該子目錄，並重複本探勘步驟。如果選出的是具體業務檔案 (例如 `.md`, `.yaml`, `.txt`)，請將其列入候選清單，並進入 Step 4。

Step 4: Search Selected Files & Progressive Disclosure
對於清單中的每一個候選檔案，執行漸進式局部檢索 (至多嘗試 5 次)：
1. 落實「漸進式揭露 (Progressive Disclosure)」，優先探索檔案間的拓樸關聯：
   - **[Obsidian 環境]** 
     - **Backlinks (反向連結)**：利用 `obsidian backlinks "<目標檔案徑路或標題>"`，自動發掘有哪些後續處理 SOP、Config 文件引用了當前錯誤。
     - **屬性與內容限縮**：利用 `obsidian search query="path:<檔案路徑> <進一步關鍵字>"` 或 `[<屬性名稱>:<值>]` 進一步收斂上下文。
   - **[無 Obsidian 環境]** 優先使用 `grep` 搜尋關鍵字或 `find` 搭配 `grep`。
2. 針對命中的行數，僅讀取匹配區段附近的上下文（例如前後 50 行），絕對不要一次性讀取整份巨大檔案。
3. 若當前檔案已提供足夠解答，跳至 Step 5。
4. 若資訊不足，切換至清單中的下一個候選檔案並重複。

Step 5: Format the Output
參考並嚴格遵守 `./assets/reply_template.md` 中的格式回覆使用者。
若經過上述流程仍找不到足夠的資訊，請在輸出中明確說明，並提示使用者給予更多限制範圍。

## 目錄設計指南 (針對知識庫維護者)
為確保檢索效率極大化，知識庫請遵守以下「物件與任務導向 (Object & Task-Oriented)」的資料庫化原則：
- **屬性化 (Properties)**：實體文件 (特別是位於 `02_procedures/` 等深層目錄下的 SOP) 都應在檔案開頭加入 Markdown YAML Frontmatter (例如 `alert_id: P001`, `component: postgresql`)，提升屬性查詢精確度。
- **維護映射表 (.base)**：如果存在核心對應表（如告警 ID 對應特定文件），請建立 `.base` 檔案（例如 `alert_db.base`），將這類邏輯結構化，方便 Agent 利用 `obsidian bases query` 進行 SQL 級別的精準打擊。
- **擁抱反向連結**：SOP 文件內部請大量使用 WikiLink (`[[文件名稱]]`) 關聯到對應的 Alarm 定義檔或 Config，如此 Agent 方可經由 Step 4 的 Backlinks 查詢，實現漸進式揭露。
- **摘要式群組**：在領域大類中僅列出重點入口與目錄用途，不要在 `index.md` 中窮舉底層所有檔案。
- **標籤化**：在底層葉節點目錄中強制加上 `Tags: [標籤]` 前綴以利自動化檢索。