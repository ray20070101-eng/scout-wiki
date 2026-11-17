"""簡報檢查腳本（Check 節點）：確認 slides/index.html 的內容都能追溯回 wiki
用法：在 scout-wiki 資料夾執行  python tools/check_slides.py
檢查項目：
  1. 每張投影片都有 data-src，且指向存在的 wiki 頁面
  2. 每張投影片左下角都有「來源：」標示
  3. 旗語 FLAGS 資料與 wiki/旗語字母表.md 逐項一致
  4. 童軍規律 12 條名稱與順序和 wiki 一致
  5. 小測驗答案和 wiki 內容一致
  6. 列出 wiki 中沒有被簡報用到的頁面（資訊）
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
html = (ROOT / "slides" / "index.html").read_text(encoding="utf-8")
pages = {p.stem: p.read_text(encoding="utf-8") for p in (ROOT / "wiki").glob("*.md")}
errors, info = [], []

slides = re.findall(r'<section class="slide[^"]*" data-src="([^"]*)">(.*?)</section>', html, re.S)
used = set()
for i, (src, body) in enumerate(slides, 1):
    for s in src.split(","):
        if s not in pages:
            errors.append(f"[來源不存在] 第 {i} 張 data-src={s}")
        used.add(s)
    if 'class="src"' not in body:
        errors.append(f"[缺來源標示] 第 {i} 張沒有左下角來源")
    for code in re.findall(r"<code>wiki/(.+?)\.md</code>", body):
        if code not in pages:
            errors.append(f"[來源不存在] 第 {i} 張標示 wiki/{code}.md")

# 3. 旗語
CIRC = "①②③④⑤⑥⑦⑧"
js = dict((k, (int(a), int(b))) for k, a, b in
          re.findall(r"'?([A-Z]|取消|數字符號)'?:\[(\d),(\d)\]", html))
wiki = {k: (CIRC.index(a) + 1, CIRC.index(b) + 1) for k, a, b in
        re.findall(r"([A-Z]|取消|數字符號)(?:（[^）]*）)?＝([①-⑧])＋([①-⑧])",
                   pages["旗語字母表"].split("## 練習")[0])}
for k in sorted(set(js) | set(wiki)):
    if js.get(k) != wiki.get(k):
        errors.append(f"[旗語不一致] {k}: 簡報={js.get(k)} wiki={wiki.get(k)}")

# 4. 規律
wiki_rules = re.findall(r"^\| (\d+) \| (\S+) \|", pages["童軍精神"], re.M)
slide_rules = re.findall(r"<i>(\d+)</i><b>(\S+?)</b>", html)
if [r for _, r in wiki_rules] != [r for _, r in slide_rules]:
    errors.append(f"[規律不一致] wiki={wiki_rules} 簡報={slide_rules}")

# 5. 小測驗
facts = {1: ("勇敢", "| 10 | 勇敢 |" in pages["童軍精神"]),
         2: ("接繩結", "粗細不同" in pages["接繩結"]),
         3: ("稱人結", "不會縮緊" in pages["稱人結"]),
         4: ("③＋⑧", "S＝③＋⑧" in pages["旗語字母表"])}
for n, (a, opts) in enumerate(re.findall(r'<div class="q" data-a="(\d)">.*?<div class="opts">(.*?)</div>', html, re.S), 1):
    chosen = re.findall(r"<button>(.*?)</button>", opts)[int(a)]
    want, ok = facts[n]
    if chosen != want or not ok:
        errors.append(f"[測驗答案錯] 第 {n} 題 標成「{chosen}」，wiki 依據為「{want}」({'有' if ok else '找不到'})")

unused = sorted(set(pages) - used - {"log"})
info.append(f"簡報未直接使用的 wiki 頁面（{len(unused)}）：{'、'.join(unused)}")

print(f"投影片 {len(slides)} 張｜引用 wiki 頁面 {len(used)} 個｜旗語比對 {len(js)} 項｜規律 {len(slide_rules)} 條")
for e in errors:
    print("❌", e)
for m in info:
    print("ℹ️ ", m)
print("結果：", "通過" if not errors else f"{len(errors)} 個錯誤")
sys.exit(1 if errors else 0)
