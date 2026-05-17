#!/usr/bin/env python3
"""Helper: load JSON, count intros/flashcards, verify."""
import json, sys, os

def analyze(path):
    with open(path) as f:
        data = json.load(f)
    print(f"\n=== {data['id']}: {data['title']} ===")
    total_chars = 0
    for ch in data['chapters']:
        nfc = len(ch.get('flashcards', []))
        nqz = len(ch.get('quiz', []))
        intro_len = len(ch.get('intro', ''))
        total_chars += intro_len
        print(f"  {ch['id']} '{ch['title']}': intro={intro_len} chars, flashcards={nfc}, quiz={nqz}")
    print(f"  TOTAL intro chars: {total_chars}, total flashcards: {sum(len(ch.get('flashcards',[])) for ch in data['chapters'])}")

if __name__ == '__main__':
    for p in sys.argv[1:]:
        analyze(p)
