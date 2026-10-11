# Release Notes - v1.1.0

## What's Changed in v1.1.0

### 📁 Audio Storage & Organization
- **Microphone Recordings**: Renamed `data/raw/audio/manual/` to `data/raw/audio/record/`. All microphone inputs are strictly saved here as WAV files.
- **TTS Generation**: Auto-generated voices are saved strictly in `data/raw/audio/tts/` as MP3 files.
- **Temporary Cache**: Previews are isolated in `data/raw/audio/tts_cache/` to prevent duplicate or orphaned files in permanent storage.
- **Standardized Naming**: Files now follow `<lang_prefix>_<random10>.<ext>` (e.g., `ch_g2j3ntbhb5.wav`, `pl_gj3j2n8jk8.wav`, `en_63f315a92d.mp3`).

### 📊 Manifest Architecture
- Retired single monolithic `manifest.csv`.
- Manifests are organized per language inside `data/metadata/`:
  - `ch_manifest.csv` (Chakma)
  - `pl_manifest.csv` (Pali)
  - `bn_manifest.csv` (Bengali)
  - `en_manifest.csv` (English)
- Full automatic reconciliation: re-recording a sentence automatically deletes old files from disk and updates the target language manifest.

### 🎙️ Review & Regeneration Enhancements
- Fixed voice regeneration in the "Review & Re-record" tab with phonetic normalization for multilingual scripts.
- Automated TTS language selection to mirror the active track.
- Replaced the Read option with a one-click **Clear Cache** action to free preview storage instantly.

