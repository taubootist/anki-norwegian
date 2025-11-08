import json
import re
import sys
import subprocess
from pathlib import Path
import shutil

# Config: silence trim level (in dB)
SILENCE_THRESHOLD = -110  # less negative = more trimming, more negative = less trimming

# Usage:
#   python make_audio_and_anki.py "Norwegian I - Unit XX.min.json" "source-audio/Norwegian I - Unit XX.mp3"

if len(sys.argv) < 3:
    print("Usage: python make_audio_and_anki.py <pairs.min.json> <source_audio.mp3>")
    sys.exit(1)

json_path = Path(sys.argv[1])
audio_src = Path(sys.argv[2])

if not json_path.exists():
    print(f"JSON file not found: {json_path}")
    sys.exit(1)

if not audio_src.exists():
    print(f"Audio file not found: {audio_src}")
    sys.exit(1)

# Project structure:
# ./<unit_name>/
#     <json>.tsv
#     audio/
unit_dir = Path(audio_src.stem)          # e.g. "Norwegian I - Unit 01"
audio_dir = unit_dir / "audio"           # e.g. "Norwegian I - Unit 01/audio"
unit_dir.mkdir(parents=True, exist_ok=True)

# Clean and recreate the audio folder
if audio_dir.exists():
    print(f"Cleaning existing audio folder: {audio_dir}")
    shutil.rmtree(audio_dir)
audio_dir.mkdir(parents=True, exist_ok=True)

# TSV goes in the unit folder, based on the JSON name
anki_tsv = unit_dir / (json_path.stem + ".tsv")  # e.g. "Norwegian I - Unit 01/Norwegian I - Unit 01.min.tsv"


def make_filename_from_norwegian(text: str) -> str:
    text = (text or "").strip()
    text = text.replace("?", "")  # remove question marks
    text = re.sub(r'[\"*:<>/\\|]', "", text)  # remove illegal filename chars
    text = re.sub(r"\s+", "_", text)  # spaces → underscores
    if not text:
        text = "phrase"
    return f"{text}.mp3"


# Load JSON data
with json_path.open(encoding="utf-8") as f:
    data = json.load(f)

segments = data.get("segments", [])
tsv_lines = []

for i, entry in enumerate(segments, start=1):
    english = (entry.get("english") or "").strip()
    norwegian = (entry.get("norwegian") or "").strip()

    # skip completely empty lines
    if not english or not norwegian:
        continue

    start = entry["start"]
    end = entry["end"]

    filename = make_filename_from_norwegian(norwegian)
    final_path = audio_dir / filename

    # temp raw slice path
    raw_path = audio_dir / f"__tmp_{i}.mp3"

    # 1) slice the audio (no trimming, just the segment)
    cmd_slice = [
        "ffmpeg",
        "-y",
        "-ss", str(start),
        "-to", str(end),
        "-i", str(audio_src),
        "-acodec", "copy",
        str(raw_path),
    ]
    subprocess.run(cmd_slice, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 2) trim silence on the sliced clip
    cmd_trim = [
        "ffmpeg",
        "-y",
        "-i", str(raw_path),
        "-af",
        (
            f"silenceremove="
            f"start_periods=1:start_threshold={SILENCE_THRESHOLD}dB:"
            f"stop_periods=1:stop_threshold={SILENCE_THRESHOLD}dB:"
            f"detection=peak"
        ),
        str(final_path),
    ]
    subprocess.run(cmd_trim, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # remove temp raw slice
    try:
        raw_path.unlink()
    except FileNotFoundError:
        pass

    audio_tag = f"[sound:{filename}]"
    # 2-column TSV: English<TAB>Norwegian + space + audio_tag
    back_field = f"{norwegian} {audio_tag}"
    tsv_lines.append(f"{english}\t{back_field}")

# Write Anki TSV into the unit folder
with anki_tsv.open("w", encoding="utf-8", newline="") as f:
    f.write("\n".join(tsv_lines))

print(f"\n✅ Created {len(tsv_lines)} clips in: {audio_dir}")
print(f"✅ Anki TSV written to: {anki_tsv}")
