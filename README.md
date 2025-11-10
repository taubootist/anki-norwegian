# Steps

### 1: Run whisper on file
```
whisper "source-audio\Norwegian I - Unit XX.mp3" --model small --task transcribe --output_format json
```

Creates "Norwegian I - Unit XX.JSON"

✅ Explanation

whisper → runs OpenAI’s Whisper CLI.

"Norwegian I - Unit XX.mp3" → your source audio file.

* --model small → same model you used (fast, accurate enough for language lessons).
* --task transcribe → produces text output (not translation).
* --output_format json → saves a structured JSON file with start/end timestamps and text.

### 2: Minify the JSON file
```
python minify_segments.py "Norwegian I - Unit XX.json"
```

Creates "Norwegian I - Unit XX.JSON"

✅ Explanation

* Reads Whisper’s full JSON output.
* Extracts only the fields you need (start, end, text, etc.).
* Produces a smaller, cleaner file

### 3: Manually scrub the min.JSON file

* match english/norwegian translations
* remove duplicates, spurious entries

### 4: Create the audio files and Anki TSV file
```
python make_audio_and_anki.py "Norwegian I - Unit XX.min.json" "source-audio/Norwegian I - Unit XX.mp3"
```

Creates the folder "Norwegian I - Unit XX"

* Norwegian I - Unit XX.min.TSV
* audio folder with mp3s

### 5: Validate/Cleanup audio and TSV files
Use Audacity

### 6: Import into Anki

Steps:

* move the audio files to "C:\Users\tau\AppData\Roaming\Anki2\rwbootes\collection.media"
* In Anki
  * Click create deck, name it "Norwegian I - Unit XX"
  * Select import: 
    * select the TSV
    * select the correct deck
  * select Sync

### 7: Done!

# Python setup

## From scratch

```
# Create a 3.13 virtual environment
py -3.13 -m venv venv

# Activate it
.\venv\Scripts\activate

# Inside the venv, check version
python --version   # should now show 3.13.x

# Install packages in 3.13
pip install openai-whisper
pip install langdetect

# commit requirements
python -m pip freeze > requirements.txt
```

## Jumping back in

```
.\venv\Scripts\activate
```

## Kill environment
```
deactivate
```


