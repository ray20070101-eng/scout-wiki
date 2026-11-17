"""LLM Wiki 檢查腳本（Lint 節點）
用法：在 scout-wiki 資料夾執行  python tools/lint.py
檢查項目：
  1. 每個頁面都有「來源：」且指向存在的 raw 檔
  2. [[連結]] 都指向存在的頁面
  3. 每篇 raw 資料都至少被一個頁面引用（覆蓋率）
  4. 旗語字母對照：wiki 與 raw 逐字比對
  5. 安全相關頁面（救援、急救、承重）必須有 ⚠️
  6. raw 資料缺來源網址 → 警告
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW, WIKI = ROOT / "raw", ROOT / "wiki"
SKIP = {"index", "log"}
SAFETY_WORDS = ["救援", "急救", "承重"]

errors, warnings = [], []
raw_files = {p.name for p in RAW.glob("*.txt")}
pages = {p.stem: p.read_text(encoding="utf-8") for p in WIKI.glob("*.md")}
cited = set()

for name, text in pages.items():
    # 2. 連結
    for link in re.findall(r"\[\[(.+?)\]\]", text):
        if link not in pages:
            errors.append(f"[斷掉的連結] {name}.md → [[{link}]]")
    if name in SKIP:
        continue
    # 1. 來源
    m = re.search(r"^來源：(.+)$", text, re.M)
    if not m:
        errors.append(f"[缺來源] {name}.md 沒有「來源：」行")
        continue
    for ref in re.findall(r"raw/([^\s、（）]+\.txt)", m.group(1)):
        if ref in raw_files:
            cited.add(ref)
        else:
            errors.append(f"[來源不存在] {name}.md 引用 raw/{ref}")
    # 5. 安全標示
    if any(w in text for w in SAFETY_WORDS) and "⚠️" not in text:
        errors.append(f"[缺安全標示] {name}.md 提到安全相關內容但沒有 ⚠️")

# 3. 覆蓋率
for f in sorted(raw_files - cited):
    errors.append(f"[未被引用] raw/{f} 沒有任何 wiki 頁面使用")

# 4. 旗語字母比對
pat = re.compile(r"([A-Z]|取消|數字符號)(?:（[^）]*）)?＝([①-⑧])＋([①-⑧])")
def flag_map(text):
    return {k: (a, b) for k, a, b in pat.findall(text)}
raw_flags = {}
for f in ["16_旗語字母A到N.txt", "17_旗語字母O到Z.txt"]:
    raw_flags.update(flag_map((RAW / f).read_text(encoding="utf-8").split("【檢索練習問題】")[0]))
wiki_flags = flag_map(pages.get("旗語字母表", "").split("## 練習")[0])
for k, v in raw_flags.items():
    if wiki_flags.get(k) != v:
        errors.append(f"[旗語不一致] {k}: raw={v} wiki={wiki_flags.get(k)}")
letters = {k for k in raw_flags if len(k) == 1}
if len(letters) != 26:
    warnings.append(f"[旗語] raw 只找到 {len(letters)} 個字母")

# 6. raw 來源網址
for f in sorted(raw_files):
    if re.search(r"^來源網址：\s*$", (RAW / f).read_text(encoding="utf-8"), re.M):
        warnings.append(f"[無來源網址] raw/{f}（團長自編筆記）")

print(f"頁面 {len(pages)} 個｜raw {len(raw_files)} 篇｜已引用 {len(cited)} 篇｜旗語比對 {len(raw_flags)} 項")
for e in errors:
    print("❌", e)
for w in warnings:
    print("⚠️ ", w)
print("結果：", "通過" if not errors else f"{len(errors)} 個錯誤")
sys.exit(1 if errors else 0)
