#!/usr/bin/env python3
import hashlib, json, pathlib, sys
root = pathlib.Path(__file__).resolve().parent.parent / "assets" / "builtin-libraries"
manifest = json.loads((root / "manifest.json").read_text())
for entry in manifest.get("assets", []):
    p = root / entry["filename"]
    if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != entry["sha256"]:
        print(f"invalid builtin asset: {p}", file=sys.stderr); raise SystemExit(1)
    data = json.loads(p.read_text())
    names = {i.get("name") for i in data.get("libraryItems", [])}
    if not {"Database","Component","Person","Web App","deploy","Lambda","S3","CloudFront","DynamoDB","EventBridge","SQS","SNS","AppSync","Aurora","Task","Start","End"} <= names:
        print("builtin core item set incomplete", file=sys.stderr); raise SystemExit(1)
print("builtin libraries ok")
