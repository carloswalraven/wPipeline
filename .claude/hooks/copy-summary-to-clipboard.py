#!/usr/bin/env python3
"""Stop hook: copies Claude's last summary (plain text) to the macOS clipboard.

Reads the Stop hook's stdin JSON, finds transcript_path, and pulls the last
assistant text block from that JSONL transcript -- the same text shown on
screen, no ANSI codes or terminal decoration. Copies it via pbcopy.

Never blocks or errors the Stop event: any failure here is swallowed by the
caller (see .claude/settings.json, which appends `2>/dev/null || true`).
"""

import json
import os
import sys
import subprocess
import time


def last_assistant_text(transcript_path):
    last_text = None
    try:
        with open(transcript_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                if entry.get("type") != "assistant":
                    continue
                content = entry.get("message", {}).get("content")
                if not isinstance(content, list):
                    continue
                texts = [
                    block.get("text", "")
                    for block in content
                    if isinstance(block, dict) and block.get("type") == "text"
                ]
                if texts:
                    last_text = "".join(texts)
    except (FileNotFoundError, OSError):
        return None
    return last_text


def stable_last_assistant_text(transcript_path, max_wait=2.0, poll_interval=0.1):
    """Waits for the transcript file to stop changing before reading it.

    The Stop hook can fire before the final assistant message has been
    flushed to the transcript file, which made this script pick up the
    previous turn's text. Polling until both the file's mtime and the
    extracted text hold steady across two consecutive checks means the
    write has actually finished.
    """
    deadline = time.time() + max_wait
    prev_text = None
    prev_mtime = None
    stable_count = 0
    while time.time() < deadline:
        try:
            mtime = os.path.getmtime(transcript_path)
        except OSError:
            mtime = None
        text = last_assistant_text(transcript_path)
        if text is not None and text == prev_text and mtime == prev_mtime:
            stable_count += 1
            if stable_count >= 2:
                return text
        else:
            stable_count = 0
        prev_text, prev_mtime = text, mtime
        time.sleep(poll_interval)
    return prev_text


def main():
    payload = json.load(sys.stdin)
    transcript_path = payload.get("transcript_path", "")
    text = stable_last_assistant_text(transcript_path)
    if text:
        subprocess.run(["pbcopy"], input=text.encode("utf-8"))


if __name__ == "__main__":
    main()
