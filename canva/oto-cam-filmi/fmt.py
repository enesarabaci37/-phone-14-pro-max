import json, sys
pg = int(sys.argv[1]); locs = sys.argv[2].split(",")
d = json.load(open(f"p{pg}.json")); pid = d["ops"][0]["page_id"]
texts = [o for o in d["ops"] if o["type"] == "add_text"]
assert len(texts) == len(locs), (len(texts), len(locs))
out = []
for o, l in zip(texts, locs):
    loc = f"{pid}-{l}"
    out.append({"type": "format_text", "locator_id": loc, "formatting": d["fmt"][o["text"]]})
    if o["text"] == "TEL":
        out.append({"type": "position_element", "locator_id": loc, "top": 1248, "left": 104})
    elif o["text"] == "0534 080 26 79":
        out.append({"type": "position_element", "locator_id": loc, "top": 1237, "left": 164})
    elif "/10" in o["text"]:
        out.append({"type": "position_element", "locator_id": loc, "top": 1260, "left": 668})
print(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
