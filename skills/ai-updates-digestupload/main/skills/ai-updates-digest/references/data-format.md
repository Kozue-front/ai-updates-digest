# レポートのデータ形式

`data.json` を作り、`python scripts/build_report.py data.json report.html` で HTML にする。
スクリプトは形式のチェックもする(「注意:」が出たら直してから出す)。

コード実行が使えない環境では、`assets/report_template.html` を読み、`/*__DATA__*/` から同じ行の `;` までをデータJSONに置き換え、`<title>` を書き換えて、そのまま HTML アーティファクトにする。

```json
{
  "title": "Claudeアプデ 2026-10-04〜10-10",
  "mode": "collect",
  "period": {"from": "2026-10-04", "to": "2026-10-10"},
  "generated_at": "2026-10-10",
  "highlights": [
    {"title": "Claude Haiku 5.5 が公開", "item_id": "haiku55", "why": "安価なモデルの選択肢が増え、社内の自動化(大量のタグ付けや要約)のコストを下げられる。"}
  ],
  "items": [
    {
      "id": "haiku55",
      "date": "2026-10-07",
      "category": "モデル",
      "kind": "new",
      "title": "Claude Haiku 5.5 公開",
      "summary": "何が変わったかを2〜3文で。",
      "audience": "全プラン / API",
      "confidence": "confirmed",
      "sources": [
        {"label": "Release notes 10/7", "url": "https://support.claude.com/...", "type": "official"}
      ],
      "history": "",
      "note": ""
    }
  ],
  "impact": {
    "basis": "作成者の環境:この会話で見えていた skill 12件・コネクタ 8件",
    "rows": [
      {"target": "brand-slides(組織で共有しているskill)", "update_ids": ["dsd-ga"], "verdict": "replace",
       "decision": "併用する", "reason": "理由を1〜2文", "keep": "skillにしか無いもの", "next_step": "持ち主に相談"}
    ],
    "no_impact": ["writing-style", "meeting-notes"]
  },
  "claims": [],
  "missed_ids": [],
  "searched": [
    {"source": "Help Center Release notes", "url": "https://support.claude.com/en/articles/12138966-release-notes", "status": "開けた", "range": "全期間", "count": "3"}
  ]
}
```

## フィールド

| フィールド | 内容 |
|---|---|
| `mode` | `collect`(収集)か `verify`(検証) |
| `highlights` | 要点3つ。読む人の仕事の目線で選ぶ。`item_id` に対応する項目の id を入れると、そのカテゴリのアイコンが付く |
| `items[].kind` | 更新の種類。アイコンと上部の集計に使う。`new`(新登場:新モデル・新機能・新コマンド)/ `up`(強化:ベータ→一般提供、値下げ、上限の緩和、対象プランの拡大)/ `change`(仕様変更:今の使い方に影響しうる変更、制限の強化、方針の改定)/ `end`(終了・期限:提供終了、サイト終了、非推奨化)/ `fix`(修正:バグ修正のまとめ) |
| `items[].date` | 公式の発表日(JST)。公式の日付が無ければ報道の日付にして `note` に「日付は報道ベース」と書く |
| `items[].category` | `モデル` / `Claudeアプリ` / `Claude Code` / `API・Platform` / `会社・その他` |
| `items[].confidence` | `confirmed`(✅)/ `reported`(🟡)/ `unverified`(⚠️) |
| `items[].sources[].type` | `official` / `press` / `x`(公式X)/ `tracker` |
| `items[].history` | 以前の発表からの変化。例「9/16 にベータ(Pro/Max)→ 10/8 に全プランで一般提供」。変化が無ければ空 |
| `impact.basis` | 誰の環境で判定したか(共有されても誤解されないように) |
| `impact.rows[].verdict` | `replace`(🔁)/ `combine`(➕)/ `action`(🛠️) |
| `impact.rows[].decision` | 🔁 は `置き換える` / `併用する` / `今は様子見`。➕・🛠️ は短い行動(例「12/14までに移行」) |
| `impact.rows[].update_ids` | 関係する `items[].id` |
| `impact.no_impact` | 影響の無かった skill・コネクタの名前 |
| `claims` | 検証モードのみ。`{"claim": "元の文", "verdict": "correct|partly|wrong|unverified", "correction": "正しい内容", "sources": [...]}` |
| `missed_ids` | 検証モードのみ。元のまとめに無かった更新の `items[].id` |
| `searched` | 探した場所すべて。開けなかった場所も載せる |

## Claude Code の載せ方

バージョンごとに1件にせず、「使う人に見える変化」ごとに1件にする(例:「`/mods` コマンド追加」)。細かい修正は、期間でまとめて1件「Claude Code 2.1.289〜2.1.296:細かい修正 ◯件」にしてよい。日付は npm の公開日(JST)。
