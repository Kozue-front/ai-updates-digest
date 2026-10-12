#!/usr/bin/env python3
"""期間内に公開された Claude Code のバージョンと CHANGELOG 本文を出す。

CHANGELOG.md には日付が無いので、npm レジストリの公開日時(公式の公開記録)で
期間を絞り込む。標準ライブラリのみ。

使い方:
  python claude_code_releases.py --since 2026-10-04 --until 2026-10-10
  python claude_code_releases.py --days 7          # 今日を含む直近7日
  オプション --json で JSON 出力
日付は日本時間(JST)で解釈する。
"""
import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

NPM_URL = "https://registry.npmjs.org/@anthropic-ai/claude-code"
CHANGELOG_URL = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
JST = timezone(timedelta(hours=9))


def fetch(url, accept=None):
    req = urllib.request.Request(url, headers={"User-Agent": "ai-updates-digest"})
    if accept:
        req.add_header("Accept", accept)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def parse_changelog(text):
    """'## 2.1.295' 形式の見出しで区切って {version: body} を返す。"""
    sections, current, buf = {}, None, []
    for line in text.splitlines():
        m = re.match(r"^##\s+v?(\d+\.\d+\.\d+)\s*$", line.strip())
        if m:
            if current:
                sections[current] = "\n".join(buf).strip()
            current, buf = m.group(1), []
        elif current:
            buf.append(line)
    if current:
        sections[current] = "\n".join(buf).strip()
    return sections


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", help="YYYY-MM-DD (JST, この日を含む)")
    ap.add_argument("--until", help="YYYY-MM-DD (JST, この日を含む)")
    ap.add_argument("--days", type=int, help="今日を含む直近N日")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--all", action="store_true", help="Fixed 行も含めて全文を出す")
    a = ap.parse_args()

    today = datetime.now(JST).date()
    if a.days:
        since, until = today - timedelta(days=a.days - 1), today
    else:
        since = datetime.strptime(a.since, "%Y-%m-%d").date() if a.since else today - timedelta(days=6)
        until = datetime.strptime(a.until, "%Y-%m-%d").date() if a.until else today

    errors = []
    try:
        times = json.loads(fetch(NPM_URL, "application/json"))["time"]
    except Exception as e:  # ネットワーク制限など
        print(f"ERROR: npm レジストリを取得できませんでした: {e}", file=sys.stderr)
        print("→ references/sources.md の手動手順に切り替えてください。", file=sys.stderr)
        sys.exit(2)
    try:
        changelog = parse_changelog(fetch(CHANGELOG_URL))
    except Exception as e:
        changelog = {}
        errors.append(f"CHANGELOG を取得できませんでした: {e}")

    rows = []
    for ver, ts in times.items():
        if ver in ("created", "modified") or "-" in ver:  # プレリリースは除外
            continue
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(JST)
        if since <= dt.date() <= until:
            rows.append({
                "version": ver,
                "published_jst": dt.strftime("%Y-%m-%d %H:%M"),
                "in_changelog": ver in changelog,
                "changes": changelog.get(ver, ""),
            })
    rows.sort(key=lambda r: r["published_jst"], reverse=True)

    result = {
        "period_jst": f"{since}〜{until}",
        "date_source": "npm registry publish time (公式の公開記録)",
        "versions": rows,
        "not_in_changelog": [r["version"] for r in rows if not r["in_changelog"]],
        "errors": errors,
    }
    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    print(f"期間(JST): {result['period_jst']}  バージョン数: {len(rows)}")
    print(f"日付の出典: {result['date_source']}")
    for e in errors:
        print("注意:", e)
    if result["not_in_changelog"]:
        print("CHANGELOGに記載なし:", ", ".join(result["not_in_changelog"]))
    if not a.all:
        print("(既定では Fixed 行は件数のみ表示。全文は --all)")
    for r in rows:
        print(f"\n## {r['version']}  ({r['published_jst']} JST)")
        if not r["changes"]:
            print("(CHANGELOGに記載なし)")
            continue
        if a.all:
            print(r["changes"])
            continue
        lines = [l for l in r["changes"].splitlines() if l.strip()]
        fixed = [l for l in lines if re.match(r"^\s*-\s*(\[[^\]]+\]\s*)?(\w+:\s*)?Fixed\b", l)]
        for l in lines:
            if l not in fixed:
                print(l)
        if fixed:
            print(f"- (Fixed {len(fixed)}件)")


if __name__ == "__main__":
    main()
