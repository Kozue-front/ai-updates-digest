#!/usr/bin/env python3
"""期間内に出た Claude Desktop(デスクトップアプリ)のバージョンと変更内容を出す。

公式の Claude Desktop Changelog は Markdown 版があり、各リリースが日付つきで並ぶ。
書き方は2通りに対応する: 旧 <Update label="v2.42304.0" description="2026-10-15"> /
新(2026-11〜)太字の版の行 **v6.28899.6** の次の行に日付。これを日付で絞り込む。標準ライブラリのみ。

使い方:
  python desktop_releases.py --since 2026-10-04 --until 2026-10-10
  python desktop_releases.py --days 7          # 今日を含む直近7日
  オプション --json で JSON 出力 / --all で 3P(他社クラウド経由)の節と Fixed 行も全文
日付は Changelog に書かれた日付(日本時間で解釈)。
"""
import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

# 2026-11 に URL が /docs/cowork/changelog に移った(旧 URL はリダイレクト)。
CHANGELOG_URL = "https://claude.com/docs/cowork/changelog.md"
PAGE_URL = "https://claude.com/docs/cowork/changelog"
JST = timezone(timedelta(hours=9))
# 旧形式: <Update label="v2.42304.0" description="2026-10-15"> ... </Update>
UPDATE_RE = re.compile(
    r'<Update\s+label="([^"]*)"\s+description="([^"]*)"[^>]*>(.*?)</Update>', re.S)
# 新形式(2026-11〜): 太字の版の行 → 空行 → 日付の行 → 本文
VERSION_LINE_RE = re.compile(r"^\s*\*\*(v\d+(?:\.\d+)+)\*\*\s*$")
DATE_LINE_RE = re.compile(r"^\s*(\d{4}-\d{2}-\d{2})\s*$")
SECTION_RE = re.compile(r"^\s*\*\*([^*]+)\*\*\s*$")


def parse_entries(text):
    """[(版, 日付の文字列, 本文)] を返す。旧形式で取れなければ新形式で読む。"""
    entries = UPDATE_RE.findall(text)
    if entries:
        return entries
    lines = text.splitlines()
    starts = [i for i, l in enumerate(lines) if VERSION_LINE_RE.match(l)]
    for n, i in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        label = VERSION_LINE_RE.match(lines[i]).group(1)
        date_s, body_start = "", i + 1
        for j in range(i + 1, min(i + 4, end)):
            m = DATE_LINE_RE.match(lines[j])
            if m:
                date_s, body_start = m.group(1), j + 1
                break
        entries.append((label, date_s, "\n".join(lines[body_start:end])))
    return entries


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "ai-updates-digest"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def split_sections(body):
    """'**General**' などの太字見出しで区切って [(見出し, [行...])] を返す。"""
    sections, name, buf = [], "", []
    for line in body.splitlines():
        m = SECTION_RE.match(line)
        if m:
            if buf:
                sections.append((name, buf))
            name, buf = m.group(1).strip(), []
        elif line.strip():
            buf.append(line.strip())
    if buf:
        sections.append((name, buf))
    return sections


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", help="YYYY-MM-DD (この日を含む)")
    ap.add_argument("--until", help="YYYY-MM-DD (この日を含む)")
    ap.add_argument("--days", type=int, help="今日を含む直近N日")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--all", action="store_true", help="3P の節と Fixed 行も全文を出す")
    a = ap.parse_args()

    today = datetime.now(JST).date()
    if a.days:
        since, until = today - timedelta(days=a.days - 1), today
    else:
        since = datetime.strptime(a.since, "%Y-%m-%d").date() if a.since else today - timedelta(days=6)
        until = datetime.strptime(a.until, "%Y-%m-%d").date() if a.until else today

    try:
        text = fetch(CHANGELOG_URL)
    except Exception as e:  # ネットワーク制限など
        print(f"ERROR: Claude Desktop Changelog を取得できませんでした: {e}", file=sys.stderr)
        print(f"→ {PAGE_URL} を直接開いてください(references/sources.md 参照)。", file=sys.stderr)
        sys.exit(2)

    rows, oldest = [], None
    for label, date_s, body in parse_entries(text):
        try:
            d = datetime.strptime(date_s.strip(), "%Y-%m-%d").date()
        except ValueError:
            continue  # 「Known issue」など日付でない項目
        oldest = d if oldest is None or d < oldest else oldest
        if not since <= d <= until:
            continue
        rows.append({
            "version": label.strip(),
            "date": str(d),
            "sections": [{"name": n, "lines": l} for n, l in split_sections(body)],
        })
    rows.sort(key=lambda r: r["date"], reverse=True)

    result = {
        "period": f"{since}〜{until}",
        "source": PAGE_URL,
        "oldest_entry_on_page": str(oldest) if oldest else None,
        "covers_period": bool(oldest and oldest <= since),
        "versions": rows,
    }
    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    print(f"期間: {result['period']}  バージョン数: {len(rows)}")
    print(f"出典: {PAGE_URL}")
    if not result["covers_period"]:
        print(f"注意: ページの一番古い項目が {result['oldest_entry_on_page']} で、期間の始まりまで届いていません")
    if not a.all:
        print("(既定では 3P の節は見出しのみ、Fixed 行は件数のみ。全文は --all)")
    for r in rows:
        print(f"\n## {r['version']}  ({r['date']})")
        for s in r["sections"]:
            lines = s["lines"]
            if not a.all and s["name"].startswith("3P"):
                print(f"[{s['name']}] ({len(lines)}行・他社クラウド経由の利用向け。省略)")
                continue
            print(f"[{s['name'] or '冒頭'}]")
            fixed = [] if a.all else [l for l in lines if re.match(r"^[*-]\s*Fixed\b", l)]
            for l in lines:
                if l not in fixed:
                    print(l)
            if fixed:
                print(f"* (Fixed {len(fixed)}件)")


if __name__ == "__main__":
    main()
