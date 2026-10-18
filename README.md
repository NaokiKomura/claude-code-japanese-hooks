# claude-code-japanese-hooks

Claude Code に日本語で指示しても、返答が英語になってしまうことがあります。
このリポジトリは、それを防ぐための hook を2つ収録しています。

| ファイル | イベント | 役割 |
|---|---|---|
| `hooks/japanese-reminder.py` | `UserPromptSubmit` | 発言に日本語が含まれていれば、「すべて日本語で書くこと」という指示をそのターンに差し込む（予防） |
| `hooks/japanese-guard.py` | `Stop` | そのターンの最終回答が英語主体なら、終了させずに英語の箇所だけ日本語で書き直させる（事後チェック） |

予防だけでは長い会話や英語のツール出力が続いたときに崩れることがあるため、事後チェックと組み合わせて使います。

## インストール

```bash
mkdir -p ~/.claude/hooks
cp hooks/*.py ~/.claude/hooks/
```

`~/.claude/settings.json` の `hooks` に次を追加します（既存の hook がある場合は配列に追記してください）。

```json
{
  "hooks": {
    "UserPromptSubmit": [
      { "hooks": [{ "type": "command", "command": "/usr/bin/python3 ~/.claude/hooks/japanese-reminder.py" }] }
    ],
    "Stop": [
      { "hooks": [{ "type": "command", "command": "/usr/bin/python3 ~/.claude/hooks/japanese-guard.py" }] }
    ]
  }
}
```

設定は新しいセッションから有効になります。標準ライブラリだけで動き、Python 3.9 以上で動作します。

### macOS での注意

`python3` を PATH 任せにせず、`/usr/bin/python3` のように絶対パスで呼ぶことをおすすめします。
Apple Silicon の Mac に Intel 版 Homebrew の Python（`/usr/local/bin/python3`）が残っていると、
`Bad CPU type in executable` で hook が起動できず、エラーが目立たないまま素通りしてしまいます。

## 判定の仕組み

### japanese-reminder.py

発言にひらがな・カタカナ・漢字が1文字でも含まれていれば、`additionalContext` で日本語指示を差し込みます。
英語だけの発言には何もしません。

### japanese-guard.py

- 検査対象は、そのターンの最後のツール呼び出しより後に書かれた本文（最終回答）だけです。
- コードブロック、インラインコード、URL、メールアドレス、Markdown リンクは数えません。
- 英字が 25 文字以上あり、かつ日本語の文字数の 3 倍を超えたら英語主体とみなします。
- 差し戻しは1ターンにつき1回だけです（`stop_hook_active` が立っていれば通す）。無限ループにはなりません。

しきい値は環境変数で変えられます。

| 環境変数 | 既定値 | 意味 |
|---|---|---|
| `JAPANESE_GUARD_MIN_LATIN` | `25` | これ未満の英字しかない本文は判定しない |
| `JAPANESE_GUARD_RATIO` | `3` | 英字数が日本語文字数のこの倍を超えたら英語主体 |
| `JAPANESE_GUARD_WAIT` | `3` | 最終回答が transcript に書き込まれるのを待つ上限（秒） |

## 動作確認

```bash
echo '{"prompt":"これを直して"}' | /usr/bin/python3 hooks/japanese-reminder.py
```

```bash
/usr/bin/python3 hooks/japanese-guard.py --check ~/.claude/projects/<プロジェクト>/<セッション>.jsonl
```

## ライセンス

MIT
