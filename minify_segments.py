import json, sys

# Usage: python simplify_segments.py "Norwegian I - Unit 01.json"

if len(sys.argv) < 2:
    print("Usage: python simplify_segments.py <input_json>")
    sys.exit(1)

input_path = sys.argv[1]
output_path = input_path.rsplit(".", 1)[0] + ".min.json"

with open(input_path, encoding="utf-8") as f:
    data = json.load(f)

segments = data.get("segments", [])

simple_segments = [
    {"start": seg.get("start"), "end": seg.get("end"), "english": "", "norwegian": seg.get("text", "").strip(), "notes": ""}
    for seg in segments if seg.get("text")
]

with open(output_path, "w", encoding="utf-8") as f:
    json.dump({"segments": simple_segments}, f, ensure_ascii=False, indent=2)

print(f"Wrote simplified file: {output_path}")
