import json
import os
import pprint

def read_jsonl(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i == 2:
                break
            yield json.loads(line)

def main():
    print("Current working directory:", os.getcwd())
    for entry in read_jsonl("kaikki-dict.jsonl"):
        pprint.pprint(entry)

if __name__ == "__main__":
    main()
