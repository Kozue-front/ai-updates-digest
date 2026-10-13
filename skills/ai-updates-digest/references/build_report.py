#!/usr/bin/env python3
"""data.json をテンプレートに流し込んで、1枚のHTMLレポートを作る。

使い方:
  python build_report.py data.json report.html
テンプレートは ../assets/report_template.html を使う。
"""
import json
import re
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "report_template.html"
CATS = {"モデル", "Claudeアプリ", "Claude Code", "API・Platform", "会社・その他"}
CONF = {"confirmed", "reported", "unverified"}
KINDS = {"new", "up", "change", "end", "fix"}
VERD = {"correct", "partly", "wrong", "unverified"}


def check(d):
    warns = []
    for k in ("title", "period", "items", "searched"):
        if k not in d:
            warns.append(f"'{k}' がありません")
    ids = set()
    for i, it in enumerate(d.get("items", [])):
        tag = f"items[{i}] {it.get('title', '')}"
        if it.get("category") not in CATS:
            warns.append(f"{tag}: category '{it.get('category')}' は5分類のどれでもありません")
        if it.get("confidence") not in CONF:
            warns.append(f"{tag}: confidence は confirmed/reported/unverified のどれか")
        if it.get("kind") not in KINDS:
            warns.append(f"{tag}: kind は new/up/change/end/fix のどれか")
        if not it.get("sources"):
            warns.append(f"{tag}: sources が空です(出典の無い項目は載せない)")
        if it.get("confidence") == "reported" and len(it.get("sources", [])) < 2:
            warns.append(f"{tag}: 🟡 には独立した出典が2本以上必要です")
        ids.add(it.get("id"))
    for h in d.get("highlights", []):
        if h.get("item_id") and h["item_id"] not in {i.get("id") for i in d.get("items", [])}:
            warns.append(f"highlight '{h.get('title', '')[:20]}': item_id が items にありません")
    for c in d.get("claims", []):
        if c.get("verdict") not in VERD:
            warns.append(f"claim '{c.get('claim', '')[:20]}': verdict は correct/partly/wrong/unverified")
    im = d.get("impact")
    if im is None:
        warns.append("'impact'(環境への影響)がありません")
    else:
        if not im.get("basis"):
            warns.append("impact.basis(誰の環境で判定したか)が空です")
        for r in im.get("rows", []):
            if r.get("verdict") not in {"replace", "combine", "action"}:
                warns.append(f"impact '{r.get('target')}': verdict は replace/combine/action")
            if r.get("verdict") == "replace" and r.get("decision") not in {"置き換える", "併用する", "今は様子見"}:
                warns.append(f"impact '{r.get('target')}': 🔁 の decision は 置き換える/併用する/今は様子見")
            for u in r.get("update_ids", []):
                if u not in ids:
                    warns.append(f"impact '{r.get('target')}': update_id '{u}' が items にありません")
    for m in d.get("missed_ids", []):
        if m not in ids:
            warns.append(f"missed_ids の '{m}' が items にありません")
    return warns


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    for w in check(data):
        print("注意:", w)
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = TEMPLATE.read_text(encoding="utf-8")
    html, n = re.subn(r"/\*__DATA__\*/.*?;\n", lambda m: payload + ";\n", html, count=1, flags=re.S)
    if n != 1:
        sys.exit("テンプレートに /*__DATA__*/ が見つかりません")
    title = data.get("title", "Claudeアプデ").replace("<", "").replace(">", "")
    html = html.replace("<title>Claudeアプデ</title>", f"<title>{title}</title>", 1)
    Path(sys.argv[2]).write_text(html, encoding="utf-8")
    print(f"書き出しました: {sys.argv[2]} (項目 {len(data.get('items', []))} 件)")


if __name__ == "__main__":
    main()
