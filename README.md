# 🏕️ 童軍基礎技能入門 LLM Wiki

第十週作業｜用 LLM Wiki 做一份教學 HTML 簡報
靜宜大學 資工二A 蔡儀叡

- 作業首頁（loop/graph 設計、檢查紀錄、反思）：https://ray20070101-eng.github.io/scout-wiki/
- 教學簡報：https://ray20070101-eng.github.io/scout-wiki/slides/
- LLM Wiki：https://ray20070101-eng.github.io/scout-wiki/wiki/

## 結構
```
CLAUDE.md   Wiki 規則檔（v2）
raw/        18 篇原始資料（只讀）
wiki/       AI 維護的知識頁面（.md）＋網頁版（.html）、index、log
slides/     教學 HTML 簡報
tools/      lint.py（檢查 wiki）、check_slides.py（檢查簡報）、build.py（md → html）
```

## 檢查
```bash
python tools/lint.py          # wiki：來源、連結、覆蓋率、旗語對照、安全標示
python tools/check_slides.py  # 簡報：每張有 wiki 來源、旗語/規律/測驗與 wiki 一致
python tools/build.py         # 重新產生 wiki 網頁版
```
