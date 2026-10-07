import os
import csv
import uuid
import numpy as np
import scipy.io.wavfile as wavfile
import traceback

# Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXTS_FILE = os.path.join(PROJECT_ROOT, "data", "raw", "texts.txt")
AUDIO_DIR = os.path.join(PROJECT_ROOT, "data", "raw", "audio")
METADATA_FILE = os.path.join(PROJECT_ROOT, "data", "metadata", "manifest.csv")

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(os.path.dirname(METADATA_FILE), exist_ok=True)

# Load sentences from all .txt files in data/raw
sentences_by_category = {}
category_indices = {}

RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
if os.path.exists(RAW_DIR):
    for filename in os.listdir(RAW_DIR):
        if filename.endswith(".txt"):
            raw_cat = filename.replace(".txt", "").capitalize()
            
            # Map raw filename to beautifully formatted UI names
            display_map = {
                "Bangla": "বাংলা (Bangla) - English",
                "Chakma": "𑄌𑄋𑄴𑄟 (বাংলা | Chakma) - English",
                "Pali": "Pāḷi (পাল়ি | 𑄛𑅄𑄨) - English",
                "English": "English (বাংলা | 𑄌𑄋𑄴𑄟 | Pāḷi)"
            }
            cat_name = display_map.get(raw_cat, f"{raw_cat} - English")
            
            sentences_by_category[cat_name] = []
            category_indices[cat_name] = 0
            
            file_path = os.path.join(RAW_DIR, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if ". " in line[:4]:
                            line = line.split(". ", 1)[1]
                        # Remove further index numbers up to 5 chars (e.g. '123. ')
                        elif ". " in line[:6] and line[:line.find(". ")].isdigit():
                            line = line.split(". ", 1)[1]
                            
                        if "|" in line:
                            transcript, context = line.split("|", 1)
                            sentences_by_category[cat_name].append((transcript.strip(), context.strip()))
                        else:
                            sentences_by_category[cat_name].append((line, ""))

if not sentences_by_category:
    sentences_by_category["Default"] = [("Error: no text files or sentences found in data/raw.", "")]
    category_indices["Default"] = 0

def normalize_audio(filepath_or_tuple):
    if isinstance(filepath_or_tuple, str):
        sr, data = wavfile.read(filepath_or_tuple)
    else:
        sr, data = filepath_or_tuple
        
    if data.dtype == np.int16:
        data = data.astype(np.float32)
        max_val = np.max(np.abs(data))
        if max_val > 0:
            data = data / max_val * 32767.0
        data = data.astype(np.int16)
    elif data.dtype in (np.float32, np.float64):
        max_val = np.max(np.abs(data))
        if max_val > 0:
            data = data / max_val
    return sr, data

def get_recorded_manifest():
    records = []
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            if not headers:
                return records
            
            has_lang = "language" in headers
            has_status = "status" in headers
            
            for row in reader:
                if len(row) >= 2:
                    path = row[0]
                    trans = row[1]
                    # Backwards compatibility
                    lang = row[headers.index("language")] if has_lang and len(row) > headers.index("language") else "Unknown"
                    status = row[headers.index("status")] if has_status and len(row) > headers.index("status") else "Ready"
                    records.append([path, trans, lang, status])
    return records

def save_manifest(records):
    # records is a list of [path, trans, lang, status]
    with open(METADATA_FILE, "w", encoding="utf-8", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["file_path", "transcript", "language", "status"])
        for r in records:
            writer.writerow(r)

