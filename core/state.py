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
RECORD_AUDIO_DIR = os.path.join(AUDIO_DIR, "record")
TTS_AUDIO_DIR = os.path.join(AUDIO_DIR, "tts")
TTS_CACHE_DIR = os.path.join(AUDIO_DIR, "tts_cache")
MANUAL_AUDIO_DIR = RECORD_AUDIO_DIR  # Alias for backward compatibility
METADATA_DIR = os.path.join(PROJECT_ROOT, "data", "metadata")

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(RECORD_AUDIO_DIR, exist_ok=True)
os.makedirs(TTS_AUDIO_DIR, exist_ok=True)
os.makedirs(TTS_CACHE_DIR, exist_ok=True)
os.makedirs(METADATA_DIR, exist_ok=True)

# Load sentences from all .txt files in data/raw
sentences_by_category = {}
category_indices = {}
category_files = {}

RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
if os.path.exists(RAW_DIR):
    for filename in sorted(os.listdir(RAW_DIR)):
        if filename.endswith(".txt"):
            raw_cat = filename.replace(".txt", "").capitalize()
            
            # Map raw filename to pattern: language name first, followed by a long dash (—)
            display_map = {
                "Bangla": "বাংলা — বাংলা (Bengali) - English",
                "Chakma": "𑄌𑄇𑄴𑄟 — 𑄌𑄇𑄴𑄟 (Bengali | Chakma) - English",
                "Pali": "Pāḷi — Pāḷi (পাল়ি | 𑄛𑅄𑄨) - English",
                "English": "English — English (Bengali | 𑄌𑄇𑄴𑄟 | Pāḷi)"
            }
            cat_name = display_map.get(raw_cat, f"{raw_cat} — {raw_cat} - English")
            
            sentences_by_category[cat_name] = []
            category_indices[cat_name] = 0
            
            file_path = os.path.join(RAW_DIR, filename)
            category_files[cat_name] = file_path
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

def get_clean_language_name(cat_or_lang):
    if not cat_or_lang:
        return "Unknown"
    s = str(cat_or_lang).strip()
    # If formatted as "Language — Description", inspect the primary language part first!
    primary = s.split(" — ")[0].strip() if " — " in s else s
    
    # Check primary portion first
    if primary in ["English", "english"]:
        return "English"
    elif "Bengali" in primary or "Bangla" in primary or "বাংলা" in primary:
        return "Bengali"
    elif "Chakma" in primary or "𑄌𑄇𑄴𑄟" in primary or "𑄌𑄋𑄴𑄟" in primary:
        return "Chakma"
    elif "Pali" in primary or "Pāḷi" in primary or "পাল়ি" in primary or "𑄛𑅄𑄨" in primary:
        return "Pali"

    # Fallback checks on entire string
    if s.lower().startswith("english"):
        return "English"
    elif "Chakma" in s or "𑄌𑄇𑄴𑄟" in s or "𑄌𑄋𑄴𑄟" in s:
        return "Chakma"
    elif "Pali" in s or "Pāḷi" in s or "পাল়ি" in s or "𑄛𑅄𑄨" in s:
        return "Pali"
    elif "Bangla" in s or "Bengali" in s or "বাংলা" in s:
        return "Bengali"
    elif "English" in s:
        return "English"
        
    return primary

def get_language_prefix(cat_or_lang):
    clean = get_clean_language_name(cat_or_lang).lower()
    if clean.startswith("ch") or "chakma" in clean:
        return "ch"
    elif clean.startswith("pl") or "pali" in clean:
        return "pl"
    elif clean.startswith("bn") or "bengali" in clean or "bangla" in clean:
        return "bn"
    elif clean.startswith("en") or "english" in clean:
        return "en"
    return "uk"

def has_chakma_script(text):
    return any(0x11100 <= ord(c) <= 0x1114F for c in text) if text else False

def chakma_to_bengali(text):
    if not text:
        return ""
    # Compound independent vowels first
    replacements = [
        ('𑄃𑄨', 'ই'), ('𑄃𑄩', 'ঈ'), ('𑄃𑄪', 'উ'), ('𑄃𑄫', 'ঊ'),
        ('𑄃𑄬', 'এ'), ('𑄃𑄭', 'ঐ'), ('𑄃𑄮', 'ও'), ('𑄃𑄯', 'ঔ'),
        ('𑄃𑄧', 'আ'), ('𑄋𑄴', 'ং'),
    ]
    for k, v in replacements:
        text = text.replace(k, v)
        
    char_map = {
        '𑄀': 'ঁ', '𑄁': 'ং', '𑄂': 'ঃ', '𑄃': 'আ', '𑄄': 'ই', '𑄅': 'উ', '𑄆': 'এ',
        '𑄇': 'ক', '𑄈': 'খ', '𑄉': 'গ', '𑄊': 'ঘ', '𑄋': 'ঙ', '𑄌': 'চ', '𑄍': 'ছ',
        '𑄎': 'জ', '𑄏': 'ঝ', '𑄐': 'ঞ', '𑄑': 'ট', '𑄒': 'ঠ', '𑄓': 'ড', '𑄔': 'ঢ',
        '𑄕': 'ণ', '𑄖': 'ত', '𑄗': 'থ', '𑄘': 'দ', '𑄙': 'ধ', '𑄚': 'ন', '𑄛': 'প',
        '𑄜': 'ফ', '𑄝': 'ব', '𑄞': 'ভ', '𑄟': 'ম', '𑄠': '্য', '𑄡': 'য', '𑄢': 'র',
        '𑄣': 'ল', '𑄤': 'ব', '𑄥': 'স', '𑄦': 'হ',
        '𑄧': 'া', '𑄨': 'ি', '𑄩': 'ী', '𑄪': 'ু', '𑄫': 'ূ', '𑄬': 'ে', '𑄭': 'ৈ',
        '𑄮': 'ো', '𑄯': 'ৌ', '𑄰': 'ৈ', '𑄱': 'ৈ', '𑄲': 'ো',
        '𑄳': '্', '𑄴': '্', '𑄶': '।', '।': '।'
    }
    res = ''.join(char_map.get(ch, ch) for ch in text)
    return res.replace('্্', '্')

def resolve_tts_spoken_text(transcript, context=None, voice_type="Bangla (BD)", category_or_lang=None):
    if not transcript:
        return ""
    tts_text = transcript.strip()
    
    if not context:
        import unicodedata
        import difflib
        def _norm(s):
            return unicodedata.normalize('NFC', s.replace(' ', '').strip())
        trans_norm = _norm(transcript)
        for cat_name, sents in sentences_by_category.items():
            for t, c in sents:
                if t.strip() == transcript.strip() or _norm(t) == trans_norm:
                    context = c
                    break
            if context:
                break
        if not context:
            all_raw = []
            raw_map = {}
            for cat_name, sents in sentences_by_category.items():
                for s in sents:
                    if len(s) > 1 and s[1]:
                        all_raw.append(s[0])
                        raw_map[s[0]] = s[1]
            matches = difflib.get_close_matches(transcript.strip(), all_raw, n=1, cutoff=0.55)
            if matches:
                context = raw_map[matches[0]]
                
    vt = voice_type or ""
    is_chakma_voice = ("Chakma" in vt or "Bangla" in vt or "Bengali" in vt)
    is_chakma_content = (has_chakma_script(transcript) or "Chakma" in str(category_or_lang))

    if is_chakma_voice and is_chakma_content:
        if context and "(" in context and "|" in context:
            tts_text = context.split("|")[0].replace("(", "").strip()
        elif context and "(" in context and ")" in context:
            inner = context.split("(")[1].split(")")[0].strip()
            if "|" in inner:
                inner = inner.split("|")[0].strip()
            if not has_chakma_script(inner) and len(inner) > 0:
                tts_text = inner
        else:
            tts_text = chakma_to_bengali(transcript)
    elif "English" in vt and not transcript.isascii():
        if context and "—" in context:
            tts_text = context.split("—")[-1].strip()
        elif context and "(" in context and "|" in context:
            parts = context.split("|")
            for p in parts[1:]:
                clean_p = p.replace(")", "").strip()
                if clean_p.isascii() and len(clean_p) > 1:
                    tts_text = clean_p
                    break

    # Final safeguard: ensure no Chakma script character leaks to edge-tts
    if has_chakma_script(tts_text):
        tts_text = chakma_to_bengali(tts_text)
        
    return tts_text.strip() if tts_text.strip() else transcript

def get_context_for_transcript(transcript, lang=None):
    if not transcript:
        return ""
    import unicodedata
    import difflib
    def _norm(s):
        return unicodedata.normalize('NFC', s.replace(' ', '').strip())
    trans_norm = _norm(transcript)
    
    # 1. Exact or normalized search in sentences_by_category
    for cat_name, sents in sentences_by_category.items():
        clean_cat = get_clean_language_name(cat_name)
        if lang and clean_cat != lang and lang != "Unknown":
            continue
        for t, c in sents:
            if t.strip() == transcript.strip() or _norm(t) == trans_norm:
                return c
                
    # 2. Search across all categories if filtered search did not find it
    for cat_name, sents in sentences_by_category.items():
        for t, c in sents:
            if t.strip() == transcript.strip() or _norm(t) == trans_norm:
                return c
                
    # 3. Fuzzy match
    all_raw = []
    raw_map = {}
    for cat_name, sents in sentences_by_category.items():
        for s in sents:
            if len(s) > 1 and s[1]:
                all_raw.append(s[0])
                raw_map[s[0]] = s[1]
    matches = difflib.get_close_matches(transcript.strip(), all_raw, n=1, cutoff=0.55)
    if matches:
        return raw_map[matches[0]]
        
    return ""



def remove_file_safely(abs_path):
    try:
        if abs_path and os.path.isfile(abs_path):
            os.remove(abs_path)
    except Exception as e:
        print(f"Warning: could not delete old file {abs_path}: {e}")

def clear_tts_cache():
    count = 0
    if os.path.exists(TTS_CACHE_DIR):
        for fname in os.listdir(TTS_CACHE_DIR):
            fpath = os.path.join(TTS_CACHE_DIR, fname)
            try:
                if os.path.isfile(fpath):
                    os.remove(fpath)
                    count += 1
            except Exception as e:
                print(f"Error deleting cache file {fpath}: {e}")
    return count

def get_recorded_manifest(verify_local_storage=True):
    records = []
    seen_paths = set()
    if os.path.exists(METADATA_DIR):
        for fname in sorted(os.listdir(METADATA_DIR)):
            if fname.endswith("_manifest.csv"):
                mf_path = os.path.join(METADATA_DIR, fname)
                try:
                    entries_to_keep = []
                    manifest_modified = False
                    with open(mf_path, "r", encoding="utf-8") as f:
                        reader = list(csv.reader(f))
                        if reader and len(reader) > 1:
                            headers = reader[0]
                            entries_to_keep.append(headers)
                            lang_idx = headers.index("language") if "language" in headers else -1
                            status_idx = headers.index("status") if "status" in headers else -1
                            for row in reader[1:]:
                                if len(row) >= 2 and row[0] not in seen_paths:
                                    rel_path = row[0].strip()
                                    abs_path = os.path.normpath(os.path.join(PROJECT_ROOT, rel_path))
                                    
                                    # Verify physical file existence in local storage
                                    if verify_local_storage:
                                        if not os.path.isfile(abs_path) or os.path.getsize(abs_path) == 0:
                                            # Audio file was deleted from local storage, exclude and reconcile
                                            manifest_modified = True
                                            continue
                                            
                                    seen_paths.add(row[0])
                                    lang = row[lang_idx] if lang_idx != -1 and len(row) > lang_idx else "Unknown"
                                    status = row[status_idx] if status_idx != -1 and len(row) > status_idx else "Ready"
                                    records.append([row[0], row[1], lang, status])
                                    entries_to_keep.append(row)
                                    
                    # Reconcile manifest CSV if any audio file was deleted from local storage
                    if manifest_modified:
                        with open(mf_path, "w", encoding="utf-8", newline='') as f:
                            writer = csv.writer(f)
                            writer.writerows(entries_to_keep)
                except Exception as e:
                    print(f"Error reading {mf_path}: {e}")
                    
    return records


def save_manifest(records):
    # Save into language-specific manifests
    grouped = {}
    for r in records:
        if len(r) >= 3:
            prefix = get_language_prefix(r[2])
            grouped.setdefault(prefix, []).append(r)
            
    for prefix in ["bn", "ch", "pl", "en"]:
        mf_path = os.path.join(METADATA_DIR, f"{prefix}_manifest.csv")
        entries = grouped.get(prefix, [])
        with open(mf_path, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["file_path", "transcript", "language", "status"])
            for e in entries:
                writer.writerow(e)

def save_audio_file(audio_source, is_tts=False, language="Unknown"):
    import shutil
    ext = ".mp3" if (isinstance(audio_source, str) and audio_source.lower().endswith(".mp3")) else ".wav"
    lang_prefix = get_language_prefix(language)
    rand_id = uuid.uuid4().hex[:10]
    filename = f"{lang_prefix}_{rand_id}{ext}"
    target_dir = TTS_AUDIO_DIR if is_tts else RECORD_AUDIO_DIR
    target_abs_path = os.path.join(target_dir, filename)
    target_rel_path = os.path.relpath(target_abs_path, PROJECT_ROOT)

    if isinstance(audio_source, str) and audio_source.lower().endswith(".mp3"):
        shutil.copyfile(audio_source, target_abs_path)
    else:
        sr, data = normalize_audio(audio_source)
        wavfile.write(target_abs_path, sr, data)

    return target_rel_path, target_abs_path

def record_audio_entry(rel_path, transcript, language, status="Ready", is_tts=False):
    clean_trans = transcript.strip()
    new_abs_path = os.path.join(PROJECT_ROOT, rel_path)
    lang_prefix = get_language_prefix(language)
    target_manifest = os.path.join(METADATA_DIR, f"{lang_prefix}_manifest.csv")
    
    # Check all manifests in METADATA_DIR for old entry with same transcript
    if os.path.exists(METADATA_DIR):
        for fname in os.listdir(METADATA_DIR):
            if fname.endswith("_manifest.csv"):
                mf_path = os.path.join(METADATA_DIR, fname)
                entries = []
                modified = False
                try:
                    with open(mf_path, "r", encoding="utf-8") as f:
                        reader = list(csv.reader(f))
                        if reader:
                            for row in reader[1:]:
                                if len(row) >= 2 and row[1].strip() == clean_trans:
                                    # Delete old audio file from disk
                                    old_abs_path = os.path.join(PROJECT_ROOT, row[0])
                                    if os.path.abspath(old_abs_path) != os.path.abspath(new_abs_path):
                                        remove_file_safely(old_abs_path)
                                    modified = True
                                else:
                                    entries.append(row)
                    if modified:
                        with open(mf_path, "w", encoding="utf-8", newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow(["file_path", "transcript", "language", "status"])
                            writer.writerows(entries)
                except Exception as e:
                    print(f"Error updating {mf_path}: {e}")
                    
    # Append or add to target manifest
    target_entries = []
    if os.path.exists(target_manifest):
        try:
            with open(target_manifest, "r", encoding="utf-8") as f:
                reader = list(csv.reader(f))
                if reader and len(reader) > 1:
                    target_entries = [r for r in reader[1:] if len(r) >= 2 and r[1].strip() != clean_trans]
        except Exception:
            target_entries = []
            
    target_entries.append([rel_path, transcript, language, status])
    with open(target_manifest, "w", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["file_path", "transcript", "language", "status"])
        writer.writerows(target_entries)
        
    return get_recorded_manifest()

def update_raw_sentence(category, old_transcript, new_transcript, new_context):
    file_path = category_files.get(category)
    if not file_path or not os.path.isfile(file_path):
        clean_lang = get_clean_language_name(category).lower()
        if "chakma" in clean_lang:
            file_path = os.path.join(RAW_DIR, "chakma.txt")
        elif "pali" in clean_lang:
            file_path = os.path.join(RAW_DIR, "pali.txt")
        elif "bengali" in clean_lang or "bangla" in clean_lang:
            file_path = os.path.join(RAW_DIR, "bangla.txt")
        elif "english" in clean_lang:
            file_path = os.path.join(RAW_DIR, "english.txt")
            
    if not file_path or not os.path.isfile(file_path):
        return False, f"Could not find raw data file for {category}."

    clean_old = old_transcript.strip()
    clean_new_trans = new_transcript.strip()
    clean_new_ctx = new_context.strip() if new_context else ""

    if not clean_new_trans:
        return False, "Sentence transcript cannot be empty."

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        return False, f"Failed to read file: {e}"

    found = False
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            new_lines.append(line)
            continue

        prefix = ""
        content = stripped
        if ". " in content[:4]:
            prefix, content = content.split(". ", 1)
            prefix += ". "
        elif ". " in content[:6] and content[:content.find(". ")].isdigit():
            prefix, content = content.split(". ", 1)
            prefix += ". "

        import unicodedata
        def _norm(s):
            return unicodedata.normalize('NFC', s.replace(' ', '').strip())

        line_trans = content.split("|", 1)[0].strip() if "|" in content else content.strip()

        if not found and (line_trans == clean_old or _norm(line_trans) == _norm(clean_old)):
            found = True
            if clean_new_ctx:
                updated_line = f"{prefix}{clean_new_trans} | {clean_new_ctx}\n"
            else:
                updated_line = f"{prefix}{clean_new_trans}\n"
            new_lines.append(updated_line)
        else:
            new_lines.append(line)

    if not found:
        return False, f"Could not find exact sentence in {os.path.basename(file_path)}."

    # Write file safely
    try:
        temp_path = file_path + ".tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        os.replace(temp_path, file_path)
    except Exception as e:
        return False, f"Failed to write updated file: {e}"

    # Update in-memory state: sentences_by_category
    clean_target = get_clean_language_name(category)
    for cat_key in sentences_by_category.keys():
        if cat_key == category or get_clean_language_name(cat_key) == clean_target:
            for idx, (t, c) in enumerate(sentences_by_category[cat_key]):
                if t.strip() == clean_old or _norm(t) == _norm(clean_old):
                    sentences_by_category[cat_key][idx] = (clean_new_trans, clean_new_ctx)
                    break

    # If recorded in metadata manifests, update transcript there as well
    if os.path.exists(METADATA_DIR):
        for fname in os.listdir(METADATA_DIR):
            if fname.endswith("_manifest.csv"):
                mf_path = os.path.join(METADATA_DIR, fname)
                try:
                    entries = []
                    mod = False
                    with open(mf_path, "r", encoding="utf-8") as f:
                        reader = list(csv.reader(f))
                        if reader:
                            entries.append(reader[0])
                            for row in reader[1:]:
                                if len(row) >= 2 and row[1].strip() == clean_old:
                                    row[1] = clean_new_trans
                                    mod = True
                                entries.append(row)
                    if mod:
                        with open(mf_path, "w", encoding="utf-8", newline='') as f:
                            writer = csv.writer(f)
                            writer.writerows(entries)
                except Exception as e:
                    print(f"Error updating manifest {mf_path}: {e}")

    return True, f"Updated successfully in {os.path.basename(file_path)}!"
