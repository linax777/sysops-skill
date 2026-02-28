# Sysops-Skill (系統維運知識庫檢索助手)

本專案是一個實驗性的概念項目，旨在為系統維運團隊提供一個**高效能、低幻覺、且支援無限擴充**的知識庫檢索 Agent 解決方案。

本專案 fork 自 [ConardLi/rag-skill](https://github.com/ConardLi/rag-skill)，並特別針對系統維運情境（SOP、Troubleshooting、架構文件等）進行深度的目錄結構最佳化與檢索邏輯強化。

---

## 🌟 為什麼需要 Sysops-Skill？

傳統基於 RAG (Retrieval-Augmented Generation) 的知識庫在面對龐大且結構複雜的企業維運文件時，常遇到以下痛點：

1. **Context Window 爆滿**：將整份除錯手冊或架構文件塞入 LLM 往往導致 Token 消耗劇增，甚至遺漏細節（Lost in the middle）。
2. **缺乏全域視角**：傳統向量檢索片段缺乏上下文，LLM 難以理解整個系統運作邏輯。
3. **過度依賴向量檢索**：許多維運問題（例如特定告警代碼 OOM、502）有明確解答，不應盲目透過向量相似度亂找。
4. **向量檢索相似度不等於相關性**：在維運場景中，檢索到的段落可能「看起來很像」，但邏輯上無法解決深層問題的內容，容易給出東拼西湊的答案。
5. **粗糙的Chunk 切分破壞上下文邏輯**：盲目按字數切分容易將「一個故障 + 一個根因 + 一個解決方案」的完整邏輯切斷。

### Sysops-Skill 的解決方案：漸進式檢索與分層索引

本專案引入了以下設計理念：

- **不需要向量資料庫**：直接操作本地目錄與檔案，不需要額外的向量資料庫。花精力在維護你的維運文件品質，而不是向量資料庫的建置。
- **分層目錄索引 (Hierarchical Indexing)**：使用多級 `index.md` 架構建立知識地圖，讓 Agent 像人類一樣「先看目錄，再看章節，最後翻閱細節」。
- **漸進式局部讀取 (Progressive Reading)**：利用命令列工具（如 `grep`、局部讀取）精準定位問題段落，避免一次性戴入數百頁文件。
- **快速直達通道 (Fast-Path)**：針對告警 ID、已知錯誤碼與常用系統元件建立捷徑，跳過不必要的目錄探索以極大化檢索效率。

---

## 📁 知識庫目錄架構

本專案預設採用四層架構，幫助 Agent 快速聚焦問題領域，你可以依照你的需求調整：

```text
├── SKILL.md                 # Agent 檢索指令核心指南
├── references_example/      # 範例知識庫目錄 (體驗用黃金範本，展示 YAML 屬性、Bases 與反向連結等進階操作)
│   ├── 01_triage_rules/     # 第一層：快速分選 (如：告警 ID 對照表、初判邏輯)
│   ├── 02_procedures/       # 第二層：標準作業流程 (如：Troubleshooting SOP、系統變更SOP)
│   ├── 03_system_context/   # 第三層：深度細節 (如：系統架構、資源清單、配置基準)
│   └── 04_atomic_assets/    # 第四層：可組合件 (如：腳本、日誌分析 Prompt 片段)
├── references/              # 實戰知識庫根目錄 (請依照上述架構自行建立自己的知識庫)
├── assets/                  # 靜態資源 (SOP 圖片等，讓 markdown 檔案可以引用方便人類閱讀)
└── tests/                   # 模擬測試案例
```

*每一層目錄皆應包含 `index.md` 文件作為該層的導航地圖。您可以直接參考 `references_example/` 目錄，了解如何撰寫包含屬性標籤與 WikiLinks 取向的維運文件。*

---

## 🤖 內建 Agent Skills

本專案提供兩個設計給 LLM/Agent 使用的專屬技能 (Skills)：

1.  **`sysops-skill` (知識庫檢索助手)**
    *   **用途**：當使用者詢問關於系統架構、SOP、告警處理建議或系統參數時使用。
    *   **特點**：精確控制讀取範圍與 Token 消耗，不使用傳統 RAG 向量搜尋，避免幻覺並保持上下文。
2.  **`sysops-linter-skill` (知識庫格式稽核員)**
    *   **用途**：當使用者要求「檢查知識庫健康度」、「驗證文件撰寫格式」或「找出不符合標籤規範的文件」時使用。
    *   **特點**：執行靜態 Python 分析腳本掃描知識庫。具備兩種等級的檢查：
        *   **嚴格違規檢查**：瞬間揪出超過 500 行的過大檔案、缺少 `Tags:` 的 `index.md` 項目，以及混入的二進位檔案 (如 PDF, Word)。
        *   **進階優化提醒 (Soft Checks)**：自動檢查 Markdown 檔案是否具備 Obsidian 支援的 YAML Frontmatter (如 `alert_id:`) 屬性。以「建議」而非「報錯」的形式，溫和地引導維護團隊採用漸進式揭露的最佳實踐。

---

## 🚀 核心工作流程

當 Agent 使用本 Skill 時，將遵循以下高效檢索路徑：

1. **捷徑判定 (Fast-Path)**
   - 若詢問包含具體告警 ID / 錯誤碼，直接進入 `01_triage_rules/` 搜索。
   - 若包含特定服務名稱，直接鎖定 `03_system_context/` 相關目錄。
2. **目錄導航 (Index Navigation)**
   - 藉由讀取 `index.md` 中的 `Tags:` 標籤與摘要，快速決定往下鑽取的子目錄。
   - 限定範圍後再執行搜尋，避免全域檢索產生的雜訊。
3. **區塊檢索與組裝 (Chunk Retrieval & Synthesis)**
   - 精準命中目標後，僅讀取命中行附近上下文（例如前後 50 行），最終組合給出答案。

---

## 🎯 文件撰寫指南 (Document Authoring Guidelines)

為了讓 Agent 檢索更快且避免 Token 浪費與幻覺 (Lost in the middle)，知識庫維護者應遵循以下撰寫原則：

### 1. `index.md` 目錄設計原則

*   **摘要式群組 (針對上層目錄)**：
    在領域大類（如 `03_system_context/`）的 `index.md` 中，**不要**窮舉所有底層檔案。
    *   **最佳作法**：僅列出重要的「子目錄用途」與「關鍵入口檔案」。
    *   **範例**：
        ```markdown
        - 目錄 `architecture/` : 存放各系統的架構圖與總體設計
        - 目錄 `configurations/` : 存放 Nginx, Redis 等配置基準
        ```

*   **標籤化與窮舉 (針對底層葉節點目錄)**：
    只有在最底層的目錄，檔案數量有限且分類夠細的時候，才在該目錄的 `index.md` 中窮舉所有檔案。
    *   **最佳作法**：強制加入 `Tags: [標籤]` 前綴，並附上精煉的一句話摘要。這能讓 Agent 直接判定目標，不需猜測檔案內容。
    *   **範例**：
        ```markdown
        - [nginx_tuning.md] Tags: [Nginx, performance, proxy] - Nginx 效能調優與反向代理基準設定
        - [redis_cluster.md] Tags: [Redis, cluster, cache] - Redis 分散式叢集配置參數
        ```

### 2. 💡 內容實作建議

1.  **分離龐大的檔案內容**
    *   單一個 Markdown 檔案如果超過 500 行，請考慮將內容依邏輯拆分成多個小檔案。
    *   運用 `index.md` 提供這些小檔案的入口與索引。

2.  **使用純文字檔案與標準格式**
    *   絕對避免使用 PDF、Word 等非純文字格式，這會巨幅增加 Agent 檢索與解析的難度與出錯率。本 Skill 假設所有文件皆為純文字檔案 (.md, .txt, .yaml, .json 等)。
    *   **針對系統數據與參數 (如 JSON/YAML/CSV)**：雖然系統參數可以直接儲存為原始的 JSON 或 YAML 供工程師閱讀，但若要**最大化 Obsidian 的圖譜檢索效益**，強烈建議將這些數據「包裹」在一份 Markdown (`.md`) 檔案中。您可以將欄位定義在 YAML Frontmatter 裡，或利用 Markdown Table 呈現。
    *   **針對超大型原始數據 (巨型 Log 或 Config)**：如果原始資料檔非常巨大(例如超過 500 行)，**請保留原有的 `.json` 或 `.csv` 檔案**。但為了確保它不是圖譜中的孤島，請建立一個同名的 `.md` 檔案作為「代理 (Proxy/Wrapper)」。在這個 `.md` 檔案中加入 `Tags`、說明，並附上 `[點擊查看原始資料檔](./raw_data.json)` 的相對連結。這樣 Agent 就能透過檢視 `.md` 的屬性，在必要時精準下鑽到真正的巨型資料檔。
    *   系統架構圖考慮轉換成 Mermaid 語法繪製，方便 Agent 直接結合架構脈絡回答問題。

3.  **提供明確的標題與結構**
    *   為每個檔案提供精確的 `# 頂層標題`。
    *   善用 `##` 和 `###` 來劃分段落，讓 Agent 在局部讀取 (`grep` 附近的行數) 時，能輕易掌握當前的上下文。

---

## 👨‍💻 人類工程師手動檢索指南 (CLI Cheat Sheet)

這套「分層導航 + 標籤索引」不僅適用於 AI Agent，對人類工程師日常維運也非常友善。當您不使用 AI 助理時，推薦搭配終端機 (`grep`) 或編輯器 (如 VSCode/Obsidian 的搜尋功能) 來手動發揮本架構的最高效率：

### 1. 快速直達 (Fast-Path)
當您明確知道遇到的錯誤碼或告警時，直接鎖定 `01_triage_rules/` 尋找：
```bash
# 尋找特定的告警或錯誤碼 (例如 OOM)
grep -rin "OOM" references/01_triage_rules/
```

### 2. 把 `index.md` 當作查閱樞紐
遇到不知道在哪裡的問題，不要盲目全域搜尋所有文件，**只搜尋**帶有 `Tags:` 的 `index.md` 索引檔：
```bash
# 只搜尋所有索引檔中，標籤含有 DB 或 MySQL 的項目
grep -rin "MySQL" references/**/index.md
```
這會瞬間回傳類似：`references/02_procedures/index.md: - [db_backup.md] Tags: [DB, MySQL] - 資料庫備份SOP`，幫助您精準定位文件。

### 3. 限縮範圍的全域搜尋
若必須透過關鍵字全文檢索，請先想好它屬於哪一層，再限制 `grep` 的目錄以減少雜訊：
```bash
# 在系統配置與架構區，尋找所有包含 Nginx 的段落
grep -rin "Nginx" references/03_system_context/
```

---

## 💎 Obsidian 增強檢索 (進階推薦)

雖然本專案使用標準的 Unix 工具 (`grep`) 作為基準檢索機制，但我們**強烈推薦**您使用 [Obsidian](https://obsidian.md/) 搭配其官方 CLI 工具來維護與檢索知識庫。

當您的環境支援 `obsidian` CLI 時，`sysops-skill` AI 助手將自動升級為強大的「圖譜式檢索系統」，具備以下顛覆性的優勢：

1.  **資料庫化查詢 (Bases)**：
    利用 YAML Frontmatter (`--- alert_id: P001 ---`) 與映射文件 (`.base`)，Agent 能夠像執行 SQL 語句般下達 `obsidian bases query`，絕對精準鎖定特定告警對應的 SOP，從根源消滅全文檢索帶來的幻覺 (Zero Hallucination)。
2.  **漸進式揭露 (Progressive Disclosure) 與反向連結 (Backlinks)**：
    透過在文件中使用 `[[WikiLinks]]`，您的文件將形成一個知識圖譜。Agent 可利用 `obsidian backlinks` 主動發現「有哪些後續處理腳本或配置檔，關聯了當前的這份 SOP」，實現如人類工程師般「順藤摸瓜」的進階除錯思維。
3.  **極速全文與屬性搜尋**：
    透過 `obsidian search` 直接調用 Obsidian 優異的本機索引引擎，支援強大的標籤 (`tag:#DB`) 與屬性範圍限縮，大幅降低無效檢索時間。

**💡 給維護者的建議：** 
在您的 SOP 檔案開頭加入 YAML 屬性，並多加利用 `[[文件名稱]]` 建立關聯，您的 AI 助手會變得前所未有的聰明！並可利用內建的 `sysops-linter-skill` 隨時檢查文件是否符合這些優化規範。

---

## 🤝 致謝與貢獻

本項目設計靈感與基礎框架來自 [ConardLi/rag-skill](https://github.com/ConardLi/rag-skill)，感謝原作者展示了如何利用 Claude/Codex/Antigravity/Opencode 等 Agent 工具將本地知識庫發揮到語義搜尋的極致。

本專案作為概念驗證（PoC），歡迎任何人基於此架構發展適合您公司內部的維運 AI 助理！
