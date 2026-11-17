"""把 wiki/*.md 轉成網頁（wiki/*.html），讓 GitHub Pages 可以直接瀏覽。
[[頁面名稱]] 會轉成 <a href="頁面名稱.html">。
用法：python tools/build.py   （需要 pip install markdown）
"""
import re
from pathlib import Path
import markdown

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"

TPL = """<!DOCTYPE html>
<html lang="zh-Hant"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}｜童軍基礎技能入門 Wiki</title>
<style>
body{{margin:0;background:#fbf8f0;color:#1f2a22;font-family:"Noto Sans TC","Microsoft JhengHei","PingFang TC",sans-serif;line-height:1.75}}
header{{background:#2f5d3a;color:#fff;padding:14px 24px;display:flex;gap:18px;align-items:center;flex-wrap:wrap}}
header a{{color:#fff;text-decoration:none;font-weight:700}} header span{{opacity:.7}}
main{{max-width:820px;margin:0 auto;padding:28px 22px 60px}}
h1{{color:#2f5d3a;margin-top:0}} h2{{color:#2f5d3a;border-bottom:2px solid #e4dcc6;padding-bottom:4px;margin-top:32px}}
a{{color:#3f7a4d}} blockquote{{margin:0 0 18px;padding:10px 16px;background:#efe6cf;border-left:5px solid #e9b923;border-radius:6px}}
table{{border-collapse:collapse;width:100%;margin:10px 0}} th,td{{border:1px solid #d9cfb4;padding:6px 10px;text-align:left}} th{{background:#efe6cf}}
code{{background:#efe6cf;padding:1px 6px;border-radius:4px}} pre{{background:#1f2a22;color:#e8f0e6;padding:14px;border-radius:8px;overflow:auto}} pre code{{background:none;color:inherit}}
.src{{font-size:14px;color:#5d6b60}}
</style></head><body>
<header><a href="../index.html">🏕️ 作業首頁</a><span>|</span><a href="index.html">Wiki 目錄</a><a href="../slides/index.html">教學簡報</a><a href="log.html">執行紀錄</a></header>
<main>{body}</main></body></html>"""


def build():
    names = {p.stem for p in WIKI.glob("*.md")}
    for p in sorted(WIKI.glob("*.md")):
        text = p.read_text(encoding="utf-8")
        text = re.sub(r"\[\[(.+?)\]\]",
                      lambda m: f"[{m.group(1)}]({m.group(1)}.html)" if m.group(1) in names else m.group(0),
                      text)
        text = re.sub(r"^(來源：.+)$", r'<p class="src">\1</p>', text, flags=re.M)
        # Python-Markdown 要求清單前有空行，否則會黏成一段
        text = re.sub(r"(?m)^(?!\s*(?:[-*]|\d+\.)\s)(?=\S)(.+)\n(?=(?:[-*]|\d+\.)\s)", r"\1\n\n", text)
        body = markdown.markdown(text, extensions=["tables", "fenced_code"])
        title = re.search(r"^# (.+)$", p.read_text(encoding="utf-8"), re.M).group(1)
        (WIKI / f"{p.stem}.html").write_text(TPL.format(title=title, body=body), encoding="utf-8")
        print("✓", p.stem + ".html")


if __name__ == "__main__":
    build()
