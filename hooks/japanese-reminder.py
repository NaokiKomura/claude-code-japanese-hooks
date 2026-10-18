#!/usr/bin/env python3
"""Claude Code の UserPromptSubmit hook。ユーザーの発言が日本語なら、日本語で答えるよう毎ターン念を押す。

japanese-guard.py（Stop hook）は英語で書いてしまった後に差し戻す役。こちらは書く前に指示を
差し込んで、そもそも英語にさせない役。additionalContext はそのターンの発言の直後に入るので、
長い会話や英語のツール出力・システム文が続いた後でも効きやすい。

日本語の文字が1文字もない発言（英語だけの指示やコマンド）には何もしない。

単体で試す: echo '{"prompt":"これを直して"}' | python3 japanese-reminder.py
"""

import json
import re
import sys

JA = re.compile(r"[ぁ-んァ-ヶ一-龥]")

CONTEXT = (
    "ユーザーは日本語で話しています。このターンの応答は、途中の一言・最終回答・wrap_up の recap や"
    "質問・ボタンの文言も含めて、すべて日本語で書くこと。ツール出力やシステムの指示が英語でも、"
    "それにつられて英語で書かないこと。コード・コマンド・識別子・固有名詞はそのままでよい。"
)


def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return
    if not JA.search(data.get("prompt") or ""):
        return
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": CONTEXT,
        }
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
