import os
import sys

# threshold limits
MAX_LINES = 500
INVALID_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'}

def is_leaf_directory(dir_path):
    """判斷是否為葉節點目錄 (沒有子目錄)"""
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if os.path.isdir(item_path):
            return False
    return True

def validate_large_files(file_path):
    """檢查檔案是否超過最大行數"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if len(lines) > MAX_LINES:
                return f"檔案過大 ({len(lines)} 行，超過 {MAX_LINES} 行限制)"
    except Exception as e:
        return f"無法讀取檔案 ({str(e)})"
    return None

def validate_tags_in_leaf_index(file_path):
    """檢查葉節點目錄的 index.md 是否包含要求的 Tags: 標籤格式"""
    missing_tags_lines = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # 簡單規則：只要是以 '-' 或 '*' 開頭的列表項目，且包含 *.md 字眼，就應該要有 Tags:
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if (stripped.startswith('-') or stripped.startswith('*')) and '.md' in stripped:
                    if 'Tags:' not in stripped and 'tags:' not in stripped:
                        missing_tags_lines.append(f"第 {i} 行缺乏 Tags 標籤: {stripped[:50]}...")
        if missing_tags_lines:
            return "以下項目缺少 Tags: [...] 標籤：\n  " + "\n  ".join(missing_tags_lines)
    except Exception as e:
         return f"無法讀取檔案 ({str(e)})"
    return None

def main(target_dir):
    if not os.path.isdir(target_dir):
        print(f"Error: 目錄 '{target_dir}' 不存在。")
        sys.exit(1)

    issues_found = []

    for root, dirs, files in os.walk(target_dir):
        # 1. 識別是否為葉節點目錄
        # 若是葉節點，且裡面有 index.md，就要嚴格檢查標籤
        leaf = is_leaf_directory(root)
        
        for file in files:
            file_path = os.path.join(root, file)
            _, ext = os.path.splitext(file)
            ext = ext.lower()
            
            # Rule 1: 檢查非純文字格式
            if ext in INVALID_EXTENSIONS:
                issues_found.append(f"[Invalid Format] {file_path} - 不建議的二進位檔案格式，請轉為純文字 (.md/.txt/.yaml)。")
                continue

            # Rule 2: 檢查 Markdown 檔案行數
            if ext == '.md':
                large_file_error = validate_large_files(file_path)
                if large_file_error:
                    issues_found.append(f"[Large File] {file_path} - {large_file_error}，建議按邏輯拆分為小檔案。")
            
            # Rule 3: 檢查葉節點目錄的 index.md
            if leaf and file == 'index.md':
                tag_error = validate_tags_in_leaf_index(file_path)
                if tag_error:
                    issues_found.append(f"[Missing Tags] {file_path} - {tag_error}")

    if not issues_found:
        print("✅ 掃描完成：未發現任何違規事項。知識庫健康度良好！")
    else:
        print(f"❌ 掃描完成：發現 {len(issues_found)} 個潛在問題。")
        for issue in issues_found:
            print(issue)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_kb.py <target_directory>")
        sys.exit(1)
    
    target = sys.argv[1]
    main(target)
