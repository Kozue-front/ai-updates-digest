# 情報源の一覧と読み方

上から順に回る。各情報源の「落とし穴」は、実際に過去の調査で起きたこと。

## 公式(✅ の根拠にできる)

### 1. Claude Resources(記事一覧)— 最初に読む
- URL: https://claude.com/resources/articles
- 中身: claude.com の製品発表に加えて、anthropic.com/news・claude.dev/blog(開発者向け)の記事も **日付つきで1つの一覧に集まる**。新しいアーティファクトの種類、プラン変更、新機能の発表はまずここに出る。
- 読み方: 一覧の一番古い日付が期間の始まりより新しければ、まだ続きがある(1ページ約11件)。次のページを読むか、`site:claude.com/resources/articles` を期間の機能名・月で検索して補う。期間の始まりまで届いたかを「読めた範囲」に書く。
- 落とし穴: 2026-10-08 の「Dashboards / Motion」と「Docs・Slides・Design のベータ終了・全プラン展開」は、ここにしか載らず Release notes にもブログ一覧にも出なかった。この一覧を飛ばすと同じ見落としが起きる。

### 2. Claude Help Center の Release notes
- URL: https://support.claude.com/en/articles/12138966-release-notes
- 中身: Claudeアプリ(チャット・Cowork・モバイル・連携)、モデル、API の主要な発表を日付つきで載せる。
- 落とし穴: 全部は載らない(上の Dashboards / Motion の例)。日付は「その項目の発表日」で、その後の変化は別の日付・別の記事に書かれる。

### 3. Claude Platform の Release notes
- URL: https://platform.claude.com/docs/en/release-notes/overview
- 中身: API・SDK・モデルの公開と提供終了・料金・Managed Agents など。日付つきで細かい。
- 落とし穴: ページが長く、1回の取得で途中までしか読めない。取得結果に「続きがある」旨が出たら、offset を指定して続きを読み、**期間の始まりの日付まで届いたか** を確かめる。届かなかったら「読めた範囲」として記録する。

### 3b. ブログ
- https://claude.com/blog と https://claude.dev/blog(開発者向け)
- 1 の一覧に大半は出るので、1 で拾えなかった記事の確認用。

### 4. Anthropic News
- URL: https://www.anthropic.com/news
- モデルの個別ページ: https://www.anthropic.com/claude/(モデル名) など
- 中身: 会社の発表・提携・研究・モデルの発表。
- 落とし穴: ここに無いから「発表されていない」とは言えない(上の 1 を参照)。

### 5. Claude Code
- CHANGELOG: https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md
- 公開日時: https://registry.npmjs.org/@anthropic-ai/claude-code の `time` フィールド(バージョンごとの npm 公開日時。UTC)
- **まず `scripts/claude_code_releases.py --since YYYY-MM-DD --until YYYY-MM-DD` を実行する。** 期間内のバージョンと、その CHANGELOG 本文をまとめて出す。
- 手動でやる場合:
  1. CHANGELOG には日付が無い。見出しはバージョン番号だけ。
  2. npm の `time` で各バージョンの公開日時を引く(`npm view @anthropic-ai/claude-code time --json` でも可)。日本時間では +9時間 になることに注意。
  3. CHANGELOG は長いので、期間の最初のバージョンまで読み切れたか確かめる。
- 落とし穴: CHANGELOG は細かい修正が大半。レポートには「使う人に見える変化」(新コマンド、新しい設定、skills / plugins / hooks / mods の仕様変更、モデルの切り替え、料金や上限に関わるもの)を選んで載せ、バグ修正は「その他◯件」とまとめる。

### 6. X(公式アカウントと社員)
- 公式: @claudeai / @AnthropicAI
- Anthropic 社員の個人アカウント: Claude Code チームのメンバーなど(例: @trq212)。機能の背景や段階展開を話すことがある
- 更新を流している非公式・運営元不明のアカウント: 見落とし探しには使えるが、公式扱いしない
- 読み方: 直接は開けないことが多い。`site:x.com/claudeai 機能名` のように検索して投稿文を拾う。ブラウザ操作のツールが使える環境なら直接開いてよい。**報道記事が X 投稿の URL を引用していることが多い**ので、報道から辿るのが早い。
- 位置づけ: 第一報と「何が話題か」を知る入口。多くは公式サイトの発表を紹介しているので、元の公式ページを見つけたらそちらを出典にする。公式アカウントの投稿で本文を読めたものは ✅ の根拠にしてよい。社員の個人アカウントは公式発表ではないので、公式ページが見つからなければ 🟡 止まり(他の独立ソースと一致する場合)。

## 非公式(候補探しに使う。✅ の根拠にはしない)

### 7. Releasebot
- https://releasebot.io/updates/anthropic と https://releasebot.io/updates/anthropic/claude-code
- 見落とし防止のチェックリストとして使う。日付は「トラッカーが最初に見た日」で公式ではない。抜けている期間もある。

### 8. 報道
- 英語: TechCrunch、The Verge、Engadget、The Decoder、VentureBeat など
- 日本語: 窓の杜、ITmedia、Classmethod DevelopersIO(Claude Code の「cc-updates」連載がバージョンごとに詳しい)
- 使い方: 見落とし防止の検索に使う(例:`Anthropic Claude 発表 2026年10月`、`Claude 新機能 ベータ`)。記事が引用している公式URL・X投稿のURLを開き、そちらで確認する。
- 公式が見つからない項目を 🟡 にするには、**独立した** 報道2本以上の一致が要る(同じ記事の転載やまとめサイト同士は1本と数える)。

## 「探した場所」の記録例

| 情報源 | 状態 | 読めた範囲 | 件数 |
|---|---|---|---|
| Help Center Release notes | 開けた | 全期間 | 3 |
| Platform Release notes | 開けた(2回に分けて取得) | 10/10〜10/01(期間をカバー) | 6 |
| Claude Code CHANGELOG + npm | スクリプトで取得 | 2.1.289〜2.1.296 | 8バージョン |
| 公式X | 検索経由 | 投稿3件を確認 | 1 |
